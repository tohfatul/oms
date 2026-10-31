\# OrderFlow Architecture



The OrderFlow frontend is built with React and TypeScript.



The backend API is implemented using .NET and ASP.NET Core with Entity Framework Core and PostgreSQL.



The application is deployed on AWS.



Backend containers run on Amazon ECS Fargate behind an Application Load Balancer.



PostgreSQL runs on Amazon RDS.



Container images are stored in Amazon ECR.



The frontend is hosted using Amazon S3 and delivered through Amazon CloudFront.



Route 53 and AWS Certificate Manager are used for DNS and TLS.



Terraform provisions the AWS infrastructure.



GitHub Actions provides automated CI/CD and authenticates to AWS through OIDC federation.



The AI service is implemented using Python, FastAPI, LangGraph, and an LLM provider abstraction.

