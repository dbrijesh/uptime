graph TD
    subgraph Consumers ["0. Consumers"]
        Ext_User["External User <br/>(Internet)"]
        Int_App["Internal App <br/>(DirectConnect)"]
    end

    subgraph Net_Acc ["[1. Network Account - RED]"]
        direction TB
        ALB_Net["Ingress ALB <br/>(Public)"]
        WAF_Net["AWS WAF <br/>(IP Whitelist/OWASP)"]
        FW_Net["Net Firewall <br/>(DPI/IPS)"]
        
        ALB_Net --> WAF_Net
        ALB_Net -->|GWLB| FW_Net
        FW_Net --> ALB_Net
    end

    subgraph DMZ_Acc ["[2. Central API Account - BLUE]"]
        direction TB
        APIGW["Central REST API Gateway"]
        Cognito["Amazon Cognito <br/>(JWT Authorizer)"]
        VPCL["VPC Link (REST)"]
        
        APIGW -.-> Cognito
        APIGW --> VPCL
    end

    subgraph Bus_Accs ["[3. LoB Business Accounts - GREEN]"]
        subgraph LOB_A ["Finance Business Unit"]
            NLB_A["Private NLB <br/>(Entry Point)"]
            ALB_A["Private ALB <br/>(Path Routing)"]
            ECS_A["ECS Cluster <br/>(Spring/Node Services)"]
            NLB_A --> ALB_A --> ECS_A
        end
        subgraph LOB_B ["HR Business Unit"]
            NLB_B["Private NLB <br/>(Entry Point)"]
            ALB_B["Private ALB <br/>(Path Routing)"]
            ECS_B["ECS Cluster <br/>(Python Services)"]
            NLB_B --> ALB_B --> ECS_B
        end
    end

    subgraph Int_Acc ["[4. Integration Account - ORANGE]"]
        ALB_Int["Integration ALB"]
        ECS_Int["ECS Connector Proxy"]
        Secrets["Secrets Manager <br/>(DB Creds)"]
        SOR["System of Record <br/>(Legacy DB)"]
        
        ALB_Int --> ECS_Int
        ECS_Int -.-> Secrets
        ECS_Int --> SOR
    end

    %% Connectivity
    Ext_User -->|HTTPS| ALB_Net
    ALB_Net -->|PrivateLink| APIGW
    Int_App -->|Direct Route| APIGW
    
    VPCL -->|Transit Gateway| NLB_A
    VPCL -->|Transit Gateway| NLB_B
    
    ECS_A & ECS_B -->|Private Connectivity| ALB_Int

    %% Styling
    style Net_Acc fill:#ffebee,stroke:#c62828,stroke-width:2px
    style DMZ_Acc fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Bus_Accs fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    style Int_Acc fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
