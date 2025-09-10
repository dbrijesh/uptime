graph TB
    %% Consumer Layer
    brijeshAKIAZKDIC767N6DWBSGGendD3Tl1oxKYO1o8QZSQk+mtQV/A3LgZRS2HHxcTRix

    subgraph "Consumer Layer"
        WEB[Web Portal]
        MOBILE[Mobile App]
        ATM[ATM Network]
        BRANCH[Branch Systems]
    end
    
    %% API Gateway Layer
    subgraph "API Gateway Layer"
        GATEWAY[API Gateway]
        AUTH[Authentication Service]
        RATE[Rate Limiting]
    end
    
    %% Platform APIs Layer
    subgraph "Platform APIs Layer"
        ACCOUNT_API[Account Management API]
        PAYMENT_API[Payment Processing API]
        LOAN_API[Loan Services API]
        CARD_API[Card Services API]
        NOTIFICATION_API[Notification API]
    end
    
    %% Event Streaming Layer
    subgraph "Event Streaming Layer"
        KAFKA[Apache Kafka]
        PRODUCER[Event Producers]
        CONSUMER[Event Consumers]
    end
    
    %% Data Integration Layer
    subgraph "Data Integration Layer"
        ETL[ETL Processes]
        CDC[Change Data Capture]
        DATA_API[Data APIs]
    end
    
    %% Data Storage Layer
    subgraph "Data Storage Layer"
        subgraph "ODS (Operational Data Store)"
            ODS_OLTP[(ODS OLTP Database)]
            ODS_OLAP[(ODS OLAP Database)]
        end
        
        CACHE[(Redis Cache)]
        SEARCH[(Elasticsearch)]
    end
    
    %% Analytics & Reporting Layer
    subgraph "Analytics & Reporting Layer"
        BI[Business Intelligence]
        DASHBOARD[Dashboards]
        REPORTS[Reporting Engine]
        ML[Machine Learning Models]
    end
    
    %% Core Banking Layer
    subgraph "Core Banking Platforms"
        CORE_ACCOUNTS[Account Management System]
        CORE_PAYMENTS[Payment Processing Engine]
        CORE_LOANS[Loan Management System]
        CORE_RISK[Risk Management Platform]
        CORE_COMPLIANCE[Compliance Engine]
        LEGACY[Legacy Banking Systems]
    end
    
    %% External Systems
    subgraph "External Systems"
        PAYMENT_NETWORKS[Payment Networks<br/>SWIFT, ACH, Card Networks]
        REGULATORY[Regulatory Systems]
        THIRD_PARTY[Third Party Services]
        CREDIT_BUREAU[Credit Bureaus]
    end
    
    %% Connections - Consumer to API Gateway
    WEB --> GATEWAY
    MOBILE --> GATEWAY
    ATM --> GATEWAY
    BRANCH --> GATEWAY
    
    %% API Gateway to Platform APIs
    GATEWAY --> AUTH
    GATEWAY --> RATE
    GATEWAY --> ACCOUNT_API
    GATEWAY --> PAYMENT_API
    GATEWAY --> LOAN_API
    GATEWAY --> CARD_API
    GATEWAY --> NOTIFICATION_API
    
    %% Platform APIs to Kafka
    ACCOUNT_API --> KAFKA
    PAYMENT_API --> KAFKA
    LOAN_API --> KAFKA
    CARD_API --> KAFKA
    NOTIFICATION_API --> KAFKA
    
    %% Kafka Event Flow
    KAFKA --> PRODUCER
    KAFKA --> CONSUMER
    PRODUCER --> KAFKA
    CONSUMER --> ETL
    CONSUMER --> CDC
    
    %% Data Integration to Storage
    ETL --> ODS_OLTP
    ETL --> ODS_OLAP
    CDC --> ODS_OLTP
    DATA_API --> ODS_OLTP
    DATA_API --> ODS_OLAP
    
    %% Platform APIs to Core Banking
    ACCOUNT_API --> CORE_ACCOUNTS
    PAYMENT_API --> CORE_PAYMENTS
    LOAN_API --> CORE_LOANS
    CARD_API --> CORE_RISK
    NOTIFICATION_API --> CORE_COMPLIANCE
    
    %% Core Banking to External Systems
    CORE_PAYMENTS --> PAYMENT_NETWORKS
    CORE_COMPLIANCE --> REGULATORY
    CORE_RISK --> CREDIT_BUREAU
    CORE_ACCOUNTS --> THIRD_PARTY
    
    %% Legacy Integration
    CORE_ACCOUNTS --> LEGACY
    CORE_PAYMENTS --> LEGACY
    CORE_LOANS --> LEGACY
    
    %% Data Flow to Analytics
    ODS_OLAP --> BI
    ODS_OLAP --> DASHBOARD
    ODS_OLAP --> REPORTS
    ODS_OLAP --> ML
    
    %% Cache and Search
    ACCOUNT_API --> CACHE
    PAYMENT_API --> CACHE
    ODS_OLTP --> SEARCH
    
    %% Kafka to Analytics (Real-time)
    KAFKA --> ML
    KAFKA --> DASHBOARD
    
    %% Styling
    classDef consumerLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef eventLayer fill:#fff3e0
    classDef dataLayer fill:#e8f5e8
    classDef coreLayer fill:#fff8e1
    classDef externalLayer fill:#fce4ec
    
    class WEB,MOBILE,ATM,BRANCH consumerLayer
    class GATEWAY,AUTH,RATE,ACCOUNT_API,PAYMENT_API,LOAN_API,CARD_API,NOTIFICATION_API apiLayer
    class KAFKA,PRODUCER,CONSUMER eventLayer
    class ETL,CDC,DATA_API,ODS_OLTP,ODS_OLAP,CACHE,SEARCH,BI,DASHBOARD,REPORTS,ML dataLayer
    class CORE_ACCOUNTS,CORE_PAYMENTS,CORE_LOANS,CORE_RISK,CORE_COMPLIANCE,LEGACY coreLayer
    class PAYMENT_NETWORKS,REGULATORY,THIRD_PARTY,CREDIT_BUREAU externalLayer
