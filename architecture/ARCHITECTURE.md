# AWS Architecture Design - MyCandidate

This document describes the proposed AWS architecture for deploying the MyCandidate application in a secure, scalable, and production-ready manner.

## Architecture Diagram
![Architecture Diagram](architecture.png)

## Choice of Orchestration: Amazon ECS (Fargate)

For this project, I recommend **Amazon ECS with AWS Fargate**.

**Rationale:**
- **Simplicity:** ECS is easier to set up and manage compared to EKS, which is beneficial for smaller teams or projects with less complex orchestration needs.
- **Serverless (Fargate):** Fargate removes the need to manage EC2 instances, reducing operational overhead and improving security through task isolation.
- **Cost-Effective:** Pay only for the resources consumed by the tasks.
- **Integration:** Deeply integrated with other AWS services like IAM, Secrets Manager, and CloudWatch.

## Scaling Considerations

- **Horizontal Auto-scaling:** Configure ECS Service Auto Scaling based on CPU and memory utilization.
- **ALB Target Groups:** Ensure the Application Load Balancer is configured with health checks to route traffic only to healthy tasks.
- **Database Scaling:** Use RDS Multi-AZ for high availability and Read Replicas for scaling read-heavy workloads.
- **Redis Caching:** Use ElastiCache for Redis to reduce database load and improve response times for frequent queries.

## Security Best Practices

- **VPC Isolation:** Place the application tasks and databases in private subnets with no direct internet access.
- **Least Privilege:** Use IAM Task Execution Roles and Task Roles with scoped-down permissions.
- **Secrets Management:** Use AWS Secrets Manager to store and rotate sensitive information like database credentials and API keys.
- **Security Groups:** Implement strict Security Group rules (e.g., ALB allows 80/443 from Internet, ECS allows 5000 from ALB, RDS allows 5432 from ECS).
- **Encryption:** Enable encryption at rest for RDS and ElastiCache, and encryption in transit (TLS) using ACM certificates on the ALB.

## Instance Sizing Recommendations

| Component | Sizing Recommendation | Rationale |
|-----------|-----------------------|-----------|
| **ECS Task** | 0.5 vCPU, 1 GB RAM | Sufficient for the Flask app handling moderate traffic; easily scalable. |
| **RDS** | db.t3.medium | General purpose instance with enough performance for typical civic tech data loads. |
| **Redis** | cache.t3.micro | Small instance is usually sufficient for session/caching needs in this application. |

## CI/CD Pipeline Proposal

**Tool:** GitHub Actions

1. **Source:** Trigger on push to `main` branch.
2. **Scan:** Run `safety` and `bandit` for security vulnerabilities.
3. **Test:** Run `pytest` to ensure logic and API endpoints are correct.
4. **Build:** Build Docker image and push to Amazon ECR.
5. **Deploy:** Update ECS Service with the new image definition using `aws ecs update-service`.

![Architecture Diagram](cicd.png)