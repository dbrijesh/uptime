graph TD
    subgraph Consumers ["0. Consumers"]
        Ext_User["External User <br/>(Internet)"]
        Int_App["Internal App <br/>(DirectConnect/Corp)"]
    end

    subgraph Net_Acc ["[1. Network Account - RED]"]
        direction TB
        ALB_Net["Ingress ALB <br/>(Public)"]
        WAF_Net["AWS WAF <br/>(OWASP Rule Sets)"]
        FW_Net["AWS Network Firewall <br/>(IPS/IDS Policy)"]
        
        ALB_Net -.-> WAF_Net
        ALB_Net -->|Gateway LB| FW_Net
        FW_Net -->|Deep Scan| ALB_Net
    end

    subgraph DMZ_Acc ["[2. Central API Account - BLUE]"]
        APIGW_Central["Central API Gateway <br/>(Regional Private)"]
        Cognito["Amazon Cognito <br/>(User Pool & Scopes)"]
        APIGW_Central -.-> Cognito
    end

    subgraph Bus_Accs ["[3. LoB Business Accounts - GREEN]"]
        subgraph LOB_A ["Business Account: Accounts"]
            ALB_A["Private ALB"]
            ECS_A["ECS Microservices"]
            ALB_A --> ECS_A
        end
        subgraph LOB_B ["Business Account: Customers"]
            ALB_B["Private ALB"]
            ECS_B["ECS Microservices"]
            ALB_B --> ECS_B
        end
    end

    subgraph Int_Acc ["[4. Integration Account - ORANGE]"]
        ALB_Int["Integration ALB"]
        ECS_Int["Integration Proxy"]
        KMS["AWS KMS <br/>(Data Encryption)"]
        SOR["System of Record <br/>(DB / Mainframe)"]
        
        ALB_Int --> ECS_Int
        ECS_Int -.-> KMS
        ECS_Int --> SOR
    end

    %% Connection Logic
    Ext_User -->|HTTPS| ALB_Net
    ALB_Net -->|PrivateLink| APIGW_Central
    Int_App -->|Private DNS| APIGW_Central
    
    APIGW_Central -->|Transit Gateway| ALB_A
    APIGW_Central -->|Transit Gateway| ALB_B
    
    ECS_A & ECS_B -->|Private Connectivity| ALB_Int

    %% Styling
    style Net_Acc fill:#ffebee,stroke:#c62828,stroke-width:2px
    style DMZ_Acc fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Bus_Accs fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    style Int_Acc fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
