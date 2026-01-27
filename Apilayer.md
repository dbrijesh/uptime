graph TD
    subgraph Internet ["Public Internet"]
        Client["External Clients"]
        Cognito["Amazon Cognito <br/>(Managed IdP)"]
    end

    subgraph AWS_Managed ["AWS Public Service Space"]
        WAF["AWS WAF <br/>- Bot Control <br/>- IP Rate Limiting <br/>- SQLi/XSS Filtering"]
        
        subgraph APIGW ["API Gateway (Public Hub)"]
            RP["Resource Policy <br/>(IP Whitelisting)"]
            Auth["Cognito Authorizer <br/>(JWT Claims Validation)"]
            Router["Path-Based Routing <br/>(/accounts vs /customers)"]
        end
    end

    subgraph DMZ_VPC ["DMZ Hub VPC"]
        direction TB
        subgraph Private_Subnets_DMZ ["Private Subnets (Dual AZ)"]
            VPCL_ENI["VPC Link ENIs <br/>(Security Group: <br/>Inbound 443 from APIGW)"]
            
            EP_Accounts["VPC Endpoint (Accounts) <br/>+ EP Policy (Least Privilege)"]
            EP_Customers["VPC Endpoint (Customers) <br/>+ EP Policy (Least Privilege)"]
        end
    end

    subgraph Backend_Account_1 ["Backend Account: Accounts"]
        subgraph Private_Subnets_1 ["Private Subnets"]
            EPS_1["VPC Endpoint Service <br/>(Whitelist DMZ Account ID)"]
            NLB_1["Private NLB <br/>(Layer 4 Security)"]
            ALB_1["Private ALB <br/>- TLS Termination <br/>- SG: Inbound only from NLB"]
            Workload_1["Accounts Microservice"]
        end
    end

    subgraph Backend_Account_2 ["Backend Account: Customers"]
        subgraph Private_Subnets_2 ["Private Subnets"]
            EPS_2["VPC Endpoint Service <br/>(Whitelist DMZ Account ID)"]
            NLB_2["Private NLB <br/>(Layer 4 Security)"]
            ALB_2["Private ALB <br/>- TLS Termination <br/>- SG: Inbound only from NLB"]
            Workload_2["Customers Microservice"]
        end
    end

    %% Auth Flow
    Client -->|1. Authenticate| Cognito
    Client -->|2. HTTPS + JWT| WAF
    WAF --> RP
    RP --> Auth
    Auth --> Router

    %% Routing Flow
    Router -->|Path: /accounts| VPCL_ENI
    Router -->|Path: /customers| VPCL_ENI
    
    VPCL_ENI --> EP_Accounts
    VPCL_ENI --> EP_Customers

    %% Cross-Account PrivateLink
    EP_Accounts -.->|PrivateLink| EPS_1
    EP_Customers -.->|PrivateLink| EPS_2

    %% Backend Flow
    EPS_1 --> NLB_1 --> ALB_1 --> Workload_1
    EPS_2 --> NLB_2 --> ALB_2 --> Workload_2

    %% Styling
    style WAF fill:#ffccbc,stroke:#d84315,stroke-width:2px
    style APIGW fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Private_Subnets_DMZ fill:#fff9c4,stroke:#fbc02d,stroke-dasharray: 5 5
    style ALB_1 fill:#f1f8e9,stroke:#558b2f
    style ALB_2 fill:#f1f8e9,stroke:#558b2f
