function AppFooter() {
  return (
    <footer className="border-top bg-light mt-auto">
      <div className="container py-3">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-center gap-2">
          <small className="text-secondary">
            OrderFlow • Built by Md Tohfatul Islam
          </small>

          <div className="d-flex gap-3">
            <a
              href="https://www.linkedin.com/in/tohfatul-islam"
              target="_blank"
              rel="noreferrer"
              className="text-decoration-none"
            >
              LinkedIn
            </a>

            <a
              href="https://github.com/tohfatul"
              target="_blank"
              rel="noreferrer"
              className="text-decoration-none"
            >
              GitHub
            </a>

            <a
              href="mailto:tohfatul.islam53@gmail.com"
              className="text-decoration-none"
            >
              Email
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default AppFooter;
