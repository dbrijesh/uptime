graph TD
    subgraph Public ["1. Public Entry (External)"]
        Client["External Client"]
        Cognito["Amazon Cognito <br/>(OAuth 2.0 IdP)"]
    end

    subgraph DMZ_Account ["2. DMZ Account (Ingress Hub)"]
        WAF["AWS WAF <br/>(Rate Limit, Bot Control)"]
        APIGW["Central API Gateway <br/>(Public)"]
        Auth["Cognito Authorizer <br/>(Scope: Accounts/Customers)"]
        VPCL["VPC Link ENIs"]
        VPCE["Interface VPC Endpoint <br/>(Consumer)"]
        
        WAF --> APIGW
        APIGW -.-> Auth
        APIGW --> VPCL --> VPCE
    end

    subgraph Network_Account ["3. Network Account (Inspection Zone)"]
        direction TB
        EPS["VPC Endpoint Service <br/>(Provider)"]
        NLB_Net["Central Network LB"]
        TGW_Attach_Net["TGW Attachment <br/>(Appliance Mode On)"]
        
        EPS --> NLB_Net
        NLB_Net -->|Targets: TGW ENI IPs| TGW_Attach_Net
    end

    subgraph TGW_Service ["4. AWS Transit Gateway (The Backbone)"]
        TGW_Route["TGW Route Table <br/>(Traffic Steering)"]
    end

    subgraph Backend_Accounts ["5. Workload Accounts (Spokes)"]
        subgraph Acc_Account ["Backend: Accounts"]
            TGW_Attach_Acc["TGW Attachment"]
            ALB_Acc["Private ALB"]
            App_Acc["Accounts API"]
        end

        subgraph Cust_Account ["Backend: Customers"]
            TGW_Attach_Cust["TGW Attachment"]
            ALB_Cust["Private ALB"]
            App_Cust["Customers API"]
        end
    end

    %% Flow Connections
    Client -->|1. Request| WAF
    VPCE -.->|2. PrivateLink| EPS
    TGW_Attach_Net --- TGW_Service
    TGW_Service --- TGW_Attach_Acc
    TGW_Service --- TGW_Attach_Cust
    TGW_Attach_Acc --> ALB_Acc --> App_Acc
    TGW_Attach_Cust --> ALB_Cust --> App_Cust

    %% Styling
    style Network_Account fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style TGW_Service fill:#eceff1,stroke:#455a64,stroke-width:2px
    style DMZ_Account fill:#e3f2fd,stroke:#0d47a1
