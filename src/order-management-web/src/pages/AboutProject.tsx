const technologies = {
  Frontend: ["React", "TypeScript", "Vite", "Bootstrap", "MSAL"],
  Backend: [".NET 10", "ASP.NET Core", "C#", "Entity Framework Core"],
  Data: ["PostgreSQL", "Amazon RDS"],
  Messaging: ["Amazon SNS", "Amazon SQS"],
  Cloud: [
    "AWS ECS Fargate",
    "Application Load Balancer",
    "Amazon ECR",
    "Amazon S3",
    "CloudFront",
    "Route 53",
    "ACM",
    "CloudWatch",
    "Secrets Manager",
  ],
  DevOps: ["Terraform", "Docker", "GitHub Actions", "AWS OIDC"],
  AI: [
    "Python",
    "FastAPI",
    "LangGraph",
    "OpenAI",
    "Amazon Bedrock",
    "Amazon Bedrock AgentCore",
  ],
};

const features = [
  "Microsoft Entra ID authentication",
  "Multi-user and tenant-aware order isolation",
  "Product browsing and order creation",
  "End-to-end order processing",
  "Event-driven processing with Amazon SNS and SQS",
  "Independent ERP and notification workers",
  "PostgreSQL persistence with Entity Framework Core",
  "Containerized deployment using Amazon ECS Fargate",
  "Health checks and application monitoring",
  "Infrastructure as Code with Terraform",
  "Automated CI/CD using GitHub Actions with AWS OIDC federation",
  "HTTPS delivery through CloudFront and Application Load Balancer",
];

function AboutProject() {
  return (
    <div className="container py-4">
      {/* Hero */}
      <section className="mb-5">
        <div className="p-4 p-md-5 bg-light border rounded-3">
          <span className="badge text-bg-primary mb-3">
            Full-Stack Cloud Portfolio Project
          </span>

          <h1 className="display-6 fw-bold">Order Management System</h1>

          <p className="lead mb-3">
            A production-oriented Order Management System demonstrating modern
            full-stack architecture, secure authentication, event-driven
            processing, cloud-native deployment, and infrastructure automation.
          </p>

          <p className="text-secondary mb-0">
            The application combines a React frontend, ASP.NET Core APIs,
            PostgreSQL, asynchronous messaging, background workers, and a
            production-style AWS deployment.
          </p>
        </div>
      </section>

      {/* Author */}
      <section className="mb-5">
        <div className="card bg-dark text-white shadow">
          <div className="card-body p-4 p-md-5">
            <div className="row align-items-center g-4">
              {/* Photo */}
              <div className="col-md-auto text-center">
                <img
                  src="/tohfatul-profile.jpg"
                  alt="Md Tohfatul Islam"
                  className="rounded-circle border border-3 border-light"
                  style={{
                    width: "120px",
                    height: "120px",
                    objectFit: "cover",
                  }}
                />
              </div>

              {/* Developer information */}
              <div className="col">
                {/* <h2 className="h3">Build by</h2> */}

                <h3 className="h5 mt-3">Build by Tohfatul Islam</h3>

                <p className="text-white-50">
                  Senior Software Engineer • Full-Stack • Cloud • AI Engineering
                </p>

                <p className="mb-0">
                  I build scalable enterprise applications using modern .NET,
                  React, cloud-native architecture, distributed systems, and
                  AI-enabled software engineering.
                </p>
              </div>
            </div>

            {/* Contact links */}
            <div className="d-flex flex-wrap justify-content-center gap-3 mt-4 pt-3 border-top border-secondary">
              <a
                href="https://www.linkedin.com/in/tohfatul-islam/"
                target="_blank"
                rel="noreferrer"
                className="btn btn-outline-light"
              >
                LinkedIn
              </a>

              <a
                href="YOUR_GITHUB_URL"
                target="_blank"
                rel="noreferrer"
                className="btn btn-outline-light"
              >
                GitHub
              </a>

              <a
                href="mailto:tohfatul.islam53@gmail.com"
                className="btn btn-outline-light"
              >
                Email
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="mb-5">
        <h2 className="h3 mb-3">Key Features</h2>

        <div className="row g-3">
          {features.map((feature) => (
            <div className="col-md-6 col-lg-4" key={feature}>
              <div className="card h-100 shadow-sm">
                <div className="card-body">
                  <div className="d-flex gap-2">
                    <span className="text-success fw-bold">✓</span>
                    <span>{feature}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Architecture */}
      <section className="mb-5">
        <h2 className="h3 mb-3">Solution Architecture</h2>

        <div className="row g-3">
          <ArchitectureCard
            title="Presentation Layer"
            description="React, TypeScript, Vite, Bootstrap, and Microsoft Authentication Library provide the browser-based user experience and authentication flow."
          />

          <ArchitectureCard
            title="API Layer"
            description="ASP.NET Core REST APIs expose secure application capabilities and validate Microsoft Entra ID access tokens."
          />

          <ArchitectureCard
            title="Application & Domain Layers"
            description="Business workflows, domain entities, service abstractions, validation, and order-processing rules are isolated from infrastructure concerns."
          />

          <ArchitectureCard
            title="Infrastructure Layer"
            description="Entity Framework Core, PostgreSQL, AWS messaging, external service integrations, and persistence implementations support the application layer."
          />

          <ArchitectureCard
            title="Event-Driven Processing"
            description="Order events are published through Amazon SNS and distributed to Amazon SQS queues for independent ERP and notification workers."
          />

          <ArchitectureCard
            title="Cloud Infrastructure"
            description="ECS Fargate, ALB, RDS, ECR, S3, CloudFront, Route 53, ACM, CloudWatch, and Secrets Manager provide the production cloud platform."
          />
        </div>
      </section>

      {/* Flow */}
      <section className="mb-5">
        <h2 className="h3 mb-3">Request & Order Processing Flow</h2>

        <div className="card shadow-sm">
          <div className="card-body p-4">
            <div className="text-center fw-semibold">
              React Web Application
              <div className="my-2">↓</div>
              Microsoft Entra ID Authentication
              <div className="my-2">↓</div>
              ASP.NET Core REST API
              <div className="my-2">↓</div>
              Application / Domain Logic
              <div className="my-2">↓</div>
              PostgreSQL / Amazon RDS
              <div className="my-2">↓</div>
              Amazon SNS
              <div className="my-2">↓</div>
              Amazon SQS
              <div className="my-2">↓</div>
              ERP Worker &nbsp; | &nbsp; Notification Worker
            </div>
          </div>
        </div>
      </section>

      {/* Tech stack */}
      <section className="mb-5">
        <h2 className="h3 mb-3">Technology Stack</h2>

        <div className="row g-3">
          {Object.entries(technologies).map(([category, items]) => (
            <div className="col-md-6" key={category}>
              <div className="card h-100 shadow-sm">
                <div className="card-body">
                  <h3 className="h6 text-uppercase text-secondary">
                    {category}
                  </h3>

                  <div className="d-flex flex-wrap gap-2 mt-3">
                    {items.map((item) => (
                      <span
                        className="badge rounded-pill text-bg-light border text-dark"
                        key={item}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* DevOps */}
      <section className="mb-5">
        <h2 className="h3 mb-3">Cloud & DevOps</h2>

        <div className="card shadow-sm">
          <div className="card-body p-4">
            <p>
              The complete AWS environment is provisioned using{" "}
              <strong>Terraform</strong>. Application containers and frontend
              assets are deployed through automated{" "}
              <strong>CI/CD pipelines in GitHub Actions</strong>. The pipelines
              build, test, package, and deploy the application to AWS using
              <strong>OIDC federation</strong> instead of long-lived AWS access
              keys.
            </p>

            <p className="mb-0">
              The frontend is delivered through private Amazon S3 and
              CloudFront, while the API and background workers run on Amazon ECS
              Fargate. PostgreSQL is hosted using Amazon RDS, with CloudWatch
              used for logs and operational monitoring.
            </p>
          </div>
        </div>
      </section>

      {/* AI */}
      <section>
        <h2 className="h3 mb-3">AI Integration & Roadmap</h2>

        <div className="card border-primary shadow-sm">
          <div className="card-body p-4 text-start">
            <p>
              The solution includes a separate Python/FastAPI AI service with
              LangGraph and an LLM-provider abstraction.
            </p>

            <p className="mb-2">
              Continued development is focused on production-oriented agentic
              capabilities using technologies such as Amazon Bedrock and Amazon
              Bedrock AgentCore, including:
            </p>

            <ul className="mb-0">
              <li>Natural-language order and product interactions</li>
              <li>Secure tool calling against OMS APIs</li>
              <li>Multi-agent orchestration</li>
              <li>Retrieval-Augmented Generation (RAG)</li>
              <li>Amazon Bedrock Knowledge Bases</li>
              <li>Amazon Bedrock Guardrails</li>
              <li>Amazon Bedrock AgentCore</li>
              <li>Model Context Protocol (MCP)</li>
              <li>Grounding and citations</li>
              <li>Conversation memory</li>
              <li>Observability and AI evaluation</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

type ArchitectureCardProps = {
  title: string;
  description: string;
};

function ArchitectureCard({ title, description }: ArchitectureCardProps) {
  return (
    <div className="col-md-6 col-lg-4">
      <div className="card h-100 shadow-sm">
        <div className="card-body">
          <h3 className="h5">{title}</h3>
          <p className="text-secondary mb-0">{description}</p>
        </div>
      </div>
    </div>
  );
}

export default AboutProject;
