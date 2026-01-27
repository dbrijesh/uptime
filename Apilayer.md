graph TD
    subgraph DMZ_Account ["DMZ Hub Account"]
        WAF["AWS WAF"]
        APIGW["Central API Gateway"]
        VPCLink["VPC Link"]
        
        %% Endpoints in DMZ for each backend
        EP_Orders["Interface Endpoint (Orders)"]
        EP_Users["Interface Endpoint (Users)"]
        
        WAF --> APIGW
        APIGW --> VPCLink
        VPCLink --> EP_Orders
        VPCLink --> EP_Users
    end

    subgraph Backend_B ["Backend Account B (Orders)"]
        EPS_Orders["VPC Endpoint Service"]
        NLB_B["Private NLB"]
        ALB_B["Private ALB"]
        
        EPS_Orders --> NLB_B --> ALB_B
    end

    subgraph Backend_C ["Backend Account C (Users)"]
        EPS_Users["VPC Endpoint Service"]
        NLB_C["Private NLB"]
        ALB_C["Private ALB"]
        
        EPS_Users --> NLB_C --> ALB_C
    end

    %% Cross-Account PrivateLink Connections
    EP_Orders -.->|PrivateLink| EPS_Orders
    EP_Users -.->|PrivateLink| EPS_Users

    %% Styling
    style DMZ_Account fill:#f9f,stroke:#333
    style Backend_B fill:#e1f5fe,stroke:#01579b
    style Backend_C fill:#fff3e0,stroke:#e65100
