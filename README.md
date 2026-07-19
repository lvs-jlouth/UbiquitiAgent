# UniFi AI Operations Assistant

An AI-powered network operations platform for UniFi infrastructure, designed for homelab and SMB environments.

## Overview

The UniFi AI Operations Assistant provides:

- **Real-time monitoring** of UniFi gateways, switches, and access points
- **AI-powered analysis** via OpenAI function calling (GPT-4o)
- **Deterministic audit engine** for configuration compliance checking
- **Security posture analysis** with FACTS/OBSERVATIONS/RISKS/RECOMMENDATIONS
- **Change approval workflows** for controlled remediation
- **Multi-tenant RBAC** (admin, operator, viewer roles)
- **Rich reporting** (HTML, PDF, Markdown)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│                  React / TypeScript / Tailwind               │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      API Layer                               │
│                FastAPI / REST / OpenAPI                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    Service Layer                              │
│         Device / Client / Audit / Report / Approval         │
└──────┬────────────────────┴──────────────────────┬──────────┘
       │                                            │
┌──────▼──────┐                         ┌──────────▼──────────┐
│  AI Layer   │                         │   Rules Engine       │
│  GPT-4o +   │                         │  Deterministic       │
│  Function   │                         │  Audit Rules         │
│  Calling    │                         │  (no AI)             │
└──────┬──────┘                         └──────────┬──────────┘
       │                                            │
┌──────▼────────────────────────────────────────────▼─────────┐
│                   Persistence Layer                          │
│              PostgreSQL / SQLAlchemy / Alembic               │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                UniFi Integration Layer                       │
│         UniFi API Client / Telemetry Collector               │
└─────────────────────────────────────────────────────────────┘
```

## Operating Modes

| Mode | Description |
|------|-------------|
| `read_only` | Monitoring, reporting, analysis only. No writes. |
| `approval_required` | Generate changes, produce diffs, wait for approval. |
| `authorized_change` | Execute pre-approved changes only. |

## Technology Stack

### Backend
- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy 2.x (async)
- Alembic migrations
- APScheduler for telemetry
- OpenAI API (GPT-4o, function calling)
- PostgreSQL + asyncpg
- structlog (JSON logging)

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- React Router v6
- Recharts
- Vite

### Infrastructure
- Docker + Docker Compose
- PostgreSQL 16
- Nginx (frontend proxy)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- UniFi Controller access

### Setup

1. Clone the repository:
```bash
git clone https://github.com/lvs-jlouth/UbiquitiAgent.git
cd UbiquitiAgent
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start services:
```bash
docker compose up -d
```

4. Access the UI at http://localhost:3000

### Default Admin Credentials
Username: `admin`
Password: Set via `ADMIN_PASSWORD` env variable (default: `changeme123`)

## Development Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
cd backend
pytest tests/ --cov=app --cov-report=term-missing -v
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Security Model

- **Principle of least privilege** - RBAC with viewer/operator/admin roles
- **Audit logging** - All actions logged with user and timestamp
- **Change approval workflows** - No direct configuration changes without approval
- **API key encryption** - Fernet symmetric encryption for stored secrets
- **Rate limiting** - Agent chat endpoint rate-limited per user
- **Input validation** - All inputs validated via Pydantic schemas
- **JWT authentication** - Short-lived tokens with refresh
- **No arbitrary code execution** - AI can only call approved tool functions

## AI Agent

The AI agent acts as a Network Operations Engineer. It:

1. **Separates information** into FACTS, OBSERVATIONS, RISKS, RECOMMENDATIONS
2. **Never presents** assumptions as facts
3. **Only accesses** systems through approved tool functions
4. **Never directly** modifies network configuration
5. **Uses function calling** to gather real-time data before responding

### Available AI Tools

| Tool | Description |
|------|-------------|
| `get_network_health()` | Overall network health status |
| `get_devices()` | All network devices |
| `get_clients()` | Connected clients |
| `get_access_points()` | Wireless APs |
| `get_switches()` | Network switches |
| `get_security_events()` | Security events |
| `get_firewall_configuration()` | Firewall rules |
| `get_vlan_configuration()` | VLAN configuration |
| `get_topology()` | Network topology |
| `get_recent_alerts()` | Recent alerts |
| `run_configuration_audit()` | Run audit rules |
| `propose_change()` | Propose configuration change (requires approval) |
| `generate_report()` | Generate network report |

## Audit Rules

The deterministic audit engine (separate from AI) checks:

### Security
- Guest VLAN isolation
- Management VLAN exposure
- Open port forwards
- Firmware drift

### VLAN
- Missing segmentation
- VLAN consistency

### WiFi
- Weak security (WEP, open networks)
- High channel utilization

### Firewall
- Excessive permissions
- High-risk rules

## Phased Delivery

- **Phase 1**: Read-only monitoring ✅
- **Phase 2**: Audit engine ✅
- **Phase 3**: AI recommendations ✅
- **Phase 4**: Approval workflows ✅
- **Phase 5**: Controlled remediation (authorized_change mode)

## License

MIT