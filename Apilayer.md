graph TD
    subgraph Internet ["Public Internet"]
        Client["External Clients"]
        Cognito["Amazon Cognito"]
    end

    subgraph AWS_Managed ["AWS Public Service Space"]
        WAF["AWS WAF"]
        APIGW["API Gateway (Hub)"]
    end

    subgraph DMZ_Account_VPC ["DMZ Account VPC (Consumer)"]
        subgraph Private_Subnets_DMZ ["Private Subnets"]
            VPCL_ENI["VPC Link ENIs"]
            InterfaceVPC["Interface VPC Endpoint <br/>(Pointing to Network Account)"]
        end
    end

    subgraph Network_Account_VPC ["Network Account VPC (Inspection Zone)"]
        direction TB
        subgraph Inspection_Subnets ["Inspection Subnets"]
            EPS["VPC Endpoint Service <br/>(PrivateLink Provider)"]
            NLB_Net["Private NLB"]
            TGW_Attach_Net["TGW Attachment"]
        end
    end

    subgraph TGW_Hub ["AWS Transit Gateway"]
        TGW_Route["TGW Route Table <br/>(Appliance Mode Enabled)"]
    end

    subgraph Backend_Account_Accounts ["Backend: Accounts"]
        subgraph Private_Subnets_Acc ["Private Subnet"]
            TGW_Attach_Acc["TGW Attachment"]
            ALB_Acc["Private ALB"]
            App_Acc["Accounts API"]
        end
    end

    subgraph Backend_Account_Cust ["Backend: Customers"]
        subgraph Private_Subnets_Cust ["Private Subnet"]
            TGW_Attach_Cust["TGW Attachment"]
            ALB_Cust["Private ALB"]
            App_Cust["Customers API"]
        end
    end

    %% Flow
    Client -->|HTTPS| WAF
    WAF --> APIGW
    APIGW --> VPCL_ENI
    VPCL_ENI --> InterfaceVPC

    %% Cross-Account PrivateLink
    InterfaceVPC -.->|PrivateLink| EPS
    EPS --> NLB_Net
    NLB_Net --> TGW_Attach_Net

    %% Transit Gateway Routing
    TGW_Attach_Net --> TGW_Route
    TGW_Route -->|Route: /accounts| TGW_Attach_Acc
    TGW_Route -->|Route: /customers| TGW_Attach_Cust

    %% Final Delivery
    TGW_Attach_Acc --> ALB_Acc --> App_Acc
    TGW_Attach_Cust --> ALB_Cust --> App_Cust

    %% Styling
    style Network_Account_VPC fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style TGW_Hub fill:#eceff1,stroke:#455a64,stroke-width:2px
