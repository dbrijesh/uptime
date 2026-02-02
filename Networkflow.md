graph TD
    subgraph Consumers ["0. Consumers"]
        Ext_User["External User <br/>(Internet)"]
        Int_App["Internal App <br/>(DirectConnect/VPN)"]
    end

    subgraph Net_Acc ["[1. Network Account - RED]"]
        direction TB
        ALB_Net["Public Network ALB"]
        subgraph Inspection_Zone ["Deep Packet Inspection"]
            FW["AWS Network Firewall <br/>(IPS/IDS)"]
        end
        ALB_Net -->|Traffic Redirect| FW
        FW -->|Cleaned Traffic| ALB_Net
    end

    subgraph DMZ_Acc ["[2. Central API Account - BLUE]"]
        APIGW_Central["Centralized API Gateway <br/>(Regional)"]
    end

    subgraph Bus_Acc ["[3. Business Account - GREEN]"]
        ALB_Bus["Private Business ALB"]
        ECS_Bus["ECS Microservices"]
        ALB_Bus --> ECS_Bus
    end

    subgraph Int_Acc ["[4. Integration Account - ORANGE]"]
        ALB_Int["Private Integration ALB"]
        ECS_Int["ECS Integration Proxy"]
        SOR["System of Record <br/>(DB/Mainframe)"]
        
        ALB_Int --> ECS_Int --> SOR
    end

    %% Connection Flow
    Ext_User -->|HTTPS| ALB_Net
    ALB_Net -.->|1. PrivateLink| APIGW_Central
    Int_App -->|2. Direct Route| APIGW_Central
    APIGW_Central -->|3. Transit Gateway| ALB_Bus
    ECS_Bus -->|4. Private Connectivity| ALB_Int

    %% Styling
    style Net_Acc fill:#ffebee,stroke:#c62828,stroke-width:2px
    style DMZ_Acc fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Bus_Acc fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    style Int_Acc fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
