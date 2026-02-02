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
        APIGW["Central API Gateway"]
        VPCL["VPC Link"]
        APIGW --> VPCL
    end

    subgraph Bus_Accs ["[3. LoB Business Accounts - GREEN]"]
        subgraph LOB_A ["Business Account A"]
            NLB_A["Private NLB (Target)"]
            ALB_A["Private ALB"]
            ECS_A["ECS Microservices"]
            NLB_A --> ALB_A --> ECS_A
        end
        subgraph LOB_B ["Business Account B"]
            NLB_B["Private NLB (Target)"]
            ALB_B["Private ALB"]
            ECS_B["ECS Microservices"]
            NLB_B --> ALB_B --> ECS_B
        end
    end

    subgraph Int_Acc ["[4. Integration Account - ORANGE]"]
        ALB_Int["Integration ALB"]
        ECS_Int["Integration Proxy"]
        SOR["System of Record"]
        ALB_Int --> ECS_Int --> SOR
    end

    %% Connectivity
    Ext_User --> ALB_Net
    ALB_Net -->|PrivateLink| APIGW
    Int_App -->|Direct Route| APIGW
    VPCL -->|Transit Gateway| NLB_A & NLB_B
    ECS_A & ECS_B --> ALB_Int

    %% Styling
    style Net_Acc fill:#ffebee,stroke:#c62828
    style DMZ_Acc fill:#e3f2fd,stroke:#1565c0
    style Bus_Accs fill:#f1f8e9,stroke:#558b2f
    style Int_Acc fill:#fff3e0,stroke:#ef6c00
