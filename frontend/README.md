# UniFi AI Operations Assistant — Frontend

Production-quality React + TypeScript frontend for the UniFi AI Operations
Assistant. Built with Vite, Tailwind CSS, React Router, Recharts, and Axios.

## Features

- **Dashboard** — network health score, device status breakdown, security
  summary, and recent events.
- **Devices / Clients** — sortable, paginated tables with detail modals.
- **Events** — severity filtering and acknowledgement.
- **Audit** — run security audits and triage findings.
- **Recommendations** — review and act on AI-generated recommendations.
- **Approvals** — authorize or reject sensitive network actions.
- **Reports** — operational summary and report generation.
- **AI Assistant** — flagship chat interface that parses assistant replies into
  Facts / Observations / Risks / Recommendations sections.
- Dark mode (system preference + toggle), full keyboard and screen-reader
  accessibility, and responsive layouts.

## Getting Started

```bash
npm install
npm run dev       # start the dev server (http://localhost:5173)
npm run build     # type-check and build for production
npm run preview   # preview the production build
npm run lint      # run ESLint
```

## Configuration

Set the backend API base URL via an environment variable (see `.env.example`):

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

During development, requests to `/api` are proxied to `http://localhost:8000`.

## Docker

```bash
docker build -t unifi-ai-frontend .
docker run -p 8080:80 unifi-ai-frontend
```

The container serves the static build via nginx and proxies `/api` to the
`backend` service.
