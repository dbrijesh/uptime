graph TD
    subgraph External_Internet ["Public Internet"]
        Client["External Client"]
    end

    subgraph AWS_Public_Service ["AWS Public Service Space"]
        WAF["AWS WAF"]
        APIGW["Central API Gateway"]
        Cognito["Amazon Cognito <br/>(User Pool)"]
    end

    subgraph DMZ_Account_VPC ["DMZ Account VPC (Hub)"]
        direction TB
        subgraph Private_Subnets_DMZ ["Private Subnets"]
            Auth["Lambda Authorizer <br/>(Verifies Cognito JWT)"]
            VPCL_ENI["VPC Link ENIs"]
            InterfaceVPC["Interface VPC Endpoints <br/>(Targeting Backends)"]
            CognitoVPC_EP["Cognito VPC Endpoint <br/>(Optional)"]
        end
    end

    subgraph Backend_Account_A ["Backend Account A (Spoke)"]
        subgraph Private_Subnets_Back_A ["Private Subnet"]
            EPS_A["VPC Endpoint Service"]
            NLB_A["Private NLB"]
            ALB_A["Private ALB"]
        end
    end

    subgraph Backend_Account_B ["Backend Account B (Spoke)"]
        subgraph Private_Subnets_Back_B ["Private Subnet"]
            EPS_B["VPC Endpoint Service"]
            NLB_B["Private NLB"]
            ALB_B["Private ALB"]
        end
    end

    %% Flow Step 1: Login
    Client -->|1. Sign-in| Cognito
    Cognito -->|2. JWT| Client

    %% Flow Step 2: API Call
    Client -->|3. HTTPS + JWT| WAF
    WAF --> APIGW
    
    %% Flow Step 3: Localized Auth
    APIGW -.->|4. Trigger| Auth
    Auth -.->|5. Verify Signature| CognitoVPC_EP
    
    %% Flow Step 4: Routing
    Auth -->|6. Pass| APIGW
    APIGW --> VPCL_ENI
    VPCL_ENI --> InterfaceVPC
    
    %% Flow Step 5: Cross-Account Tunnel
    InterfaceVPC -.->|7. PrivateLink| EPS_A
    InterfaceVPC -.->|7. PrivateLink| EPS_B
    
    EPS_A --> NLB_A --> ALB_A
    EPS_B --> NLB_B --> ALB_B

    %% Styling
    style AWS_Public_Service fill:#fff,stroke:#333,stroke-dasharray: 5 5
    style Private_Subnets_DMZ fill:#e3f2fd,stroke:#0d47a1
    style Backend_Account_A fill:#f3e5f5,stroke:#7b1fa2
    style Backend_Account_B fill:#f1f8e9,stroke:#558b2f
