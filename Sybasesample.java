package com.example.inventory;

import java.sql.*;
import java.math.BigDecimal;
import java.util.*;
import com.sybase.jdbc3.jdbc.SybConnection;

/**
 * ProductManager - Handles product operations with Sybase database
 */
public class ProductManager {
    private static final String DB_DRIVER = "com.sybase.jdbc3.jdbc.SybDriver";
    private static final String DB_URL = "jdbc:sybase:Tds:localhost:5000/inventory";
    private static final String DB_USER = "sybase_user";
    private static final String DB_PASS = "password";
    
    /**
     * Initialize database connection
     */
    public ProductManager() {
        try {
            Class.forName(DB_DRIVER);
        } catch (ClassNotFoundException e) {
            throw new RuntimeException("Failed to load Sybase driver", e);
        }
    }
    
    /**
     * Get connection with Sybase-specific settings
     */
    private Connection getConnection() throws SQLException {
        Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
        
        // Set Sybase-specific options
        SybConnection sybConn = (SybConnection) conn;
        sybConn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
        
        return conn;
    }
    
    /**
     * Get product by ID
     */
    public Product getProduct(long id) throws SQLException {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        
        try {
            conn = getConnection();
            
            // Sybase-specific query with HOLDLOCK
            String sql = "SELECT id, name, description, price, quantity, " +
                         "IFNULL(category, 'UNKNOWN') as category, last_updated " +
                         "FROM products HOLDLOCK " +
                         "WHERE id = ?";
            
            stmt = conn.prepareStatement(sql);
            stmt.setLong(1, id);
            rs = stmt.executeQuery();
            
            if (rs.next()) {
                Product product = new Product();
                product.setId(rs.getLong("id"));
                product.setName(rs.getString("name"));
                product.setDescription(rs.getString("description"));
                product.setPrice(rs.getBigDecimal("price"));
                product.setQuantity(rs.getInt("quantity"));
                product.setCategory(rs.getString("category"));
                product.setLastUpdated(rs.getTimestamp("last_updated"));
                return product;
            }
            
            return null;
        } finally {
            closeResources(rs, stmt, conn);
        }
    }
    
    /**
     * Get products by page using Sybase pagination
     */
    public List<Product> getProductsByPage(int page, int pageSize) throws SQLException {
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;
        List<Product> products = new ArrayList<>();
        
        try {
            conn = getConnection();
            stmt = conn.createStatement();
            
            // Sybase-specific pagination
            int startRow = (page - 1) * pageSize + 1;
            
            // Using Sybase TOP N START AT syntax
            String sql = "SELECT TOP " + pageSize + " START AT " + startRow + 
                         " id, name, price, quantity " +
                         "FROM products " +
                         "ORDER BY name ASC";
            
            rs = stmt.executeQuery(sql);
            
            while (rs.next()) {
                Product product = new Product();
                product.setId(rs.getLong("id"));
                product.setName(rs.getString("name"));
                product.setPrice(rs.getBigDecimal("price"));
                product.setQuantity(rs.getInt("quantity"));
                products.add(product);
            }
            
            return products;
        } finally {
            closeResources(rs, stmt, conn);
        }
    }
    
    /**
     * Update product inventory
     */
    public void updateInventory(long id, int quantity) throws SQLException {
        Connection conn = null;
        PreparedStatement stmt = null;
        
        try {
            conn = getConnection();
            conn.setAutoCommit(false);
            
            // Sybase-specific timestamp handling
            String sql = "UPDATE products " +
                         "SET quantity = quantity + ?, " +
                         "last_updated = CURRENT TIMESTAMP " +
                         "WHERE id = ?";
            
            stmt = conn.prepareStatement(sql);
            stmt.setInt(1, quantity);
            stmt.setLong(2, id);
            
            int rows = stmt.executeUpdate();
            
            if (rows != 1) {
                conn.rollback();
                throw new SQLException("Product update failed: " + id);
            }
            
            // Log the change
            logInventoryChange(conn, id, quantity);
            
            conn.commit();
        } catch (SQLException e) {
            if (conn != null) {
                conn.rollback();
            }
            throw e;
        } finally {
            if (conn != null) {
                conn.setAutoCommit(true);
            }
            closeResources(null, stmt, conn);
        }
    }
    
    /**
     * Log inventory change
     */
    private void logInventoryChange(Connection conn, long productId, int quantity) throws SQLException {
        PreparedStatement stmt = null;
        
        try {
            String sql = "INSERT INTO inventory_log (product_id, quantity_change, change_date) " +
                         "VALUES (?, ?, GETDATE())";
            
            stmt = conn.prepareStatement(sql);
            stmt.setLong(1, productId);
            stmt.setInt(2, quantity);
            
            stmt.executeUpdate();
        } finally {
            closeResources(null, stmt, null);
        }
    }
    
    /**
     * Search products with dynamic SQL
     */
    public List<Product> searchProducts(String nameFilter, BigDecimal minPrice) throws SQLException {
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;
        List<Product> products = new ArrayList<>();
        
        try {
            conn = getConnection();
            stmt = conn.createStatement();
            
            // Build dynamic SQL with Sybase syntax
            StringBuilder sql = new StringBuilder();
            sql.append("SELECT id, name, price, quantity ")
               .append("FROM products ")
               .append("WHERE 1=1 ");
            
            if (nameFilter != null && !nameFilter.isEmpty()) {
                // Using Sybase string concatenation
                sql.append(" AND name LIKE '").append(nameFilter).append("%'");
            }
            
            if (minPrice != null) {
                sql.append(" AND price >= ").append(minPrice);
            }
            
            sql.append(" ORDER BY name ASC");
            
            rs = stmt.executeQuery(sql.toString());
            
            while (rs.next()) {
                Product product = new Product();
                product.setId(rs.getLong("id"));
                product.setName(rs.getString("name"));
                product.setPrice(rs.getBigDecimal("price"));
                product.setQuantity(rs.getInt("quantity"));
                products.add(product);
            }
            
            return products;
        } finally {
            closeResources(rs, stmt, conn);
        }
    }
    
    /**
     * Get inventory report using stored procedure
     */
    public List<CategorySummary> getInventoryReport() throws SQLException {
        Connection conn = null;
        CallableStatement cstmt = null;
        ResultSet rs = null;
        List<CategorySummary> results = new ArrayList<>();
        
        try {
            conn = getConnection();
            
            // Call Sybase stored procedure
            cstmt = conn.prepareCall("{call sp_inventory_report(?, ?)}");
            
            // Register output parameters
            cstmt.registerOutParameter(1, Types.INTEGER); // Return code
            cstmt.registerOutParameter(2, Types.VARCHAR); // Error message
            
            boolean hasResults = cstmt.execute();
            
            // Check return code
            int returnCode = cstmt.getInt(1);
            if (returnCode != 0) {
                String errorMsg = cstmt.getString(2);
                throw new SQLException("Stored procedure failed: " + errorMsg);
            }
            
            if (hasResults) {
                rs = cstmt.getResultSet();
                while (rs.next()) {
                    CategorySummary summary = new CategorySummary();
                    summary.setCategory(rs.getString("category"));
                    summary.setProductCount(rs.getInt("product_count"));
                    summary.setTotalQuantity(rs.getInt("total_quantity"));
                    summary.setAveragePrice(rs.getBigDecimal("average_price"));
                    results.add(summary);
                }
            }
            
            return results;
        } finally {
            closeResources(rs, cstmt, conn);
        }
    }
    
    /**
     * Archive old records using temp table
     */
    public int archiveOldRecords(int daysOld) throws SQLException {
        Connection conn = null;
        Statement stmt = null;
        
        try {
            conn = getConnection();
            conn.setAutoCommit(false);
            stmt = conn.createStatement();
            
            // Create temp table using Sybase syntax
            stmt.execute("CREATE TABLE #temp_records (id INT, product_id INT, quantity INT, log_date DATETIME)");
            
            // Insert records to archive
            String insertSql = "INSERT INTO #temp_records " +
                              "SELECT id, product_id, quantity_change, change_date " +
                              "FROM inventory_log " +
                              "WHERE DATEDIFF(day, change_date, GETDATE()) > " + daysOld;
            
            int inserted = stmt.executeUpdate(insertSql);
            
            if (inserted > 0) {
                // Move to archive and delete from source
                stmt.executeUpdate("INSERT INTO inventory_log_archive SELECT * FROM #temp_records");
                stmt.executeUpdate("DELETE FROM inventory_log WHERE id IN (SELECT id FROM #temp_records)");
            }
            
            // Drop temp table
            stmt.execute("DROP TABLE #temp_records");
            
            conn.commit();
            return inserted;
        } catch (SQLException e) {
            if (conn != null) {
                conn.rollback();
            }
            throw e;
        } finally {
            if (conn != null) {
                conn.setAutoCommit(true);
            }
            closeResources(null, stmt, conn);
        }
    }
    
    /**
     * Close resources safely
     */
    private void closeResources(ResultSet rs, Statement stmt, Connection conn) {
        try { if (rs != null) rs.close(); } catch (SQLException e) { /* ignore */ }
        try { if (stmt != null) stmt.close(); } catch (SQLException e) { /* ignore */ }
        try { if (conn != null) conn.close(); } catch (SQLException e) { /* ignore */ }
    }
    
    /**
     * Product class
     */
    public static class Product {
        private long id;
        private String name;
        private String description;
        private BigDecimal price;
        private int quantity;
        private String category;
        private Timestamp lastUpdated;
        
        // Getters and setters
        public long getId() { return id; }
        public void setId(long id) { this.id = id; }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public BigDecimal getPrice() { return price; }
        public void setPrice(BigDecimal price) { this.price = price; }
        
        public int getQuantity() { return quantity; }
        public void setQuantity(int quantity) { this.quantity = quantity; }
        
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        
        public Timestamp getLastUpdated() { return lastUpdated; }
        public void setLastUpdated(Timestamp lastUpdated) { this.lastUpdated = lastUpdated; }
    }
    
    /**
     * Category summary class
     */
    public static class CategorySummary {
        private String category;
        private int productCount;
        private int totalQuantity;
        private BigDecimal averagePrice;
        
        // Getters and setters
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        
        public int getProductCount() { return productCount; }
        public void setProductCount(int productCount) { this.productCount = productCount; }
        
        public int getTotalQuantity() { return totalQuantity; }
        public void setTotalQuantity(int totalQuantity) { this.totalQuantity = totalQuantity; }
        
        public BigDecimal getAveragePrice() { return averagePrice; }
        public void setAveragePrice(BigDecimal averagePrice) { this.averagePrice = averagePrice; }
    }
}
