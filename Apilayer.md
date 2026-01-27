graph TD
    subgraph External_Consumer ["External Consumer"]
        User["Public Client"]
    end

    subgraph DMZ_Account ["DMZ Account (Public Face)"]
        WAF["AWS WAF"]
        APIGW["API Gateway (Public)"]
        VPCLink["VPC Link"]
        InterfaceVPC["Interface VPC Endpoint"]
        
        User -->|HTTPS| WAF
        WAF --> APIGW
        APIGW --> VPCLink
        VPCLink --> InterfaceVPC
    end

    subgraph Network_Boundary ["AWS PrivateLink (Cross-Account)"]
        InterfaceVPC -.->|Secure Tunnel| EPService["VPC Endpoint Service"]
    end

    subgraph Backend_Account ["Backend Account (Workload)"]
        EPService --> NLB["Network Load Balancer (Private)"]
        NLB --> ALB["Application Load Balancer (Private)"]
        
        subgraph Private_Subnet ["Private Subnet"]
            ALB --> EC2["API Instances / Microservices"]
        end
    end

    %% Styling
    style DMZ_Account fill:#f9f,stroke:#333,stroke-width:2px
    style Backend_Account fill:#bbf,stroke:#333,stroke-width:2px
    style Private_Subnet fill:#eee,stroke:#999,stroke-dasharray: 5 5
