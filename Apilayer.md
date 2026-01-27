graph TD
    subgraph External_Consumer ["External Consumers"]
        Client["External Clients / Partners"]
    end

    subgraph DMZ_Account ["DMZ Account (Security Hub)"]
        direction TB
        WAF["AWS WAF <br/>(IP Whitelisting, Rate Limiting, <br/>OWASP Top 10)"]
        
        subgraph APIGW_Layer ["Central API Gateway"]
            RP["Resource Policy <br/>(Deny if not SourceIP)"]
            Auth["Lambda Authorizer <br/>(JWT/mTLS Validation)"]
            Routes["Path-based Router <br/>(/orders vs /users)"]
        end

        VPCLink["VPC Link"]
        
        %% Interface Endpoints with Policies
        EP_Orders["Interface Endpoint <br/>(with VPCE Policy)"]
        EP_Users["Interface Endpoint <br/>(with VPCE Policy)"]
    end

    subgraph Backend_Account_B ["Backend Account B (Orders)"]
        EPS_B["VPC Endpoint Service"]
        NLB_B["Private NLB"]
        ALB_B["Private ALB <br/>(Strict SG: Allow DMZ ENIs)"]
    end

    subgraph Backend_Account_C ["Backend Account C (Users)"]
        EPS_C["VPC Endpoint Service"]
        NLB_C["Private NLB"]
        ALB_C["Private ALB <br/>(Strict SG: Allow DMZ ENIs)"]
    end

    %% Flow Connections
    Client -->|HTTPS| WAF
    WAF --> RP
    RP --> Auth
    Auth -->|Validated| Routes
    Routes -->|Path: /orders| VPCLink
    Routes -->|Path: /users| VPCLink
    
    VPCLink --> EP_Orders
    VPCLink --> EP_Users

    %% Cross-Account Tunnels
    EP_Orders -.->|PrivateLink| EPS_B
    EP_Users -.->|PrivateLink| EPS_C

    EPS_B --> NLB_B --> ALB_B
    EPS_C --> NLB_C --> ALB_C

    %% Styling
    style WAF fill:#ffccbc,stroke:#d84315
    style APIGW_Layer fill:#e1f5fe,stroke:#0277bd
    style Auth fill:#fff9c4,stroke:#fbc02d
    style EP_Orders fill:#f3e5f5,stroke:#7b1fa2
    style EP_Users fill:#f3e5f5,stroke:#7b1fa2
