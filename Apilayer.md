graph TD
    subgraph DMZ_Account_VPC ["DMZ Account VPC (Hub)"]
        subgraph Public_Subnets ["Public Subnets (AZ1 & AZ2)"]
            WAF["AWS WAF"]
            APIGW["Central API Gateway"]
            NAT["NAT Gateway (for Lambda Egress)"]
        end

        subgraph Private_Subnets_DMZ ["Private Subnets (AZ1 & AZ2)"]
            Auth["Lambda Authorizer <br/>(Validates JWT/mTLS)"]
            VPCLink["VPC Link"]
            InterfaceVPC["Interface VPC Endpoints <br/>(for Backend A & B)"]
        end
    end

    subgraph Backend_Account_A ["Backend Account A (Spoke)"]
        subgraph Private_Subnets_A ["Private Subnets"]
            EPS_A["VPC Endpoint Service"]
            NLB_A["Private NLB"]
            ALB_A["Private ALB"]
            App_A["Microservices / EC2"]
        end
    end

    subgraph Backend_Account_B ["Backend Account B (Spoke)"]
        subgraph Private_Subnets_B ["Private Subnets"]
            EPS_B["VPC Endpoint Service"]
            NLB_B["Private NLB"]
            ALB_B["Private ALB"]
            App_B["Microservices / EC2"]
        end
    end

    %% Flow
    Client["External Client"] -->|HTTPS| WAF
    WAF --> APIGW
    APIGW -.->|Trigger| Auth
    Auth -->|IAM Policy Result| APIGW
    APIGW --> VPCLink
    VPCLink --> InterfaceVPC
    
    %% Cross-Account PrivateLink
    InterfaceVPC -.->|PrivateLink A| EPS_A
    InterfaceVPC -.->|PrivateLink B| EPS_B

    EPS_A --> NLB_A --> ALB_A --> App_A
    EPS_B --> NLB_B --> ALB_B --> App_B

    %% Styling
    style DMZ_Account_VPC fill:#f5f5f5,stroke:#333
    style Public_Subnets fill:#fff3e0,stroke:#ef6c00
    style Private_Subnets_DMZ fill:#e1f5fe,stroke:#0277bd
    style Backend_Account_A fill:#f3e5f5,stroke:#7b1fa2
    style Backend_Account_B fill:#f1f8e9,stroke:#558b2f
