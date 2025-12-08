# Software Bill of Materials (SBOM)

**Project:** DreamDemo Flower Shop  
**Version:** 0.0.1 (Sprint 1)  
**Organization:** Sauce Labs  
**License:** Apache-2.0  
**Generated:** 2025-11-03  
**Format:** CycloneDX 1.5

## Overview
Full-stack e-commerce application designed to demonstrate comprehensive testing capabilities with Sauce Labs.

## Architecture Components

### Frontend Container
- **Base Image:** node:18-alpine
- **Runtime:** Node.js 18 (Alpine Linux)
- **Framework:** React 19.2.0 + TypeScript 4.9.5

### Backend Container
- **Base Image:** python:3.9-slim
- **Runtime:** Python 3.9
- **Framework:** FastAPI + Uvicorn

### Infrastructure Services
- **Temporal Server:** 1.22.4
- **Temporal UI:** 2.21.3
- **PostgreSQL:** 13.22 (Alpine)

## Frontend Dependencies

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| react | 19.2.0 | MIT | UI Framework |
| react-dom | 19.2.0 | MIT | React DOM rendering |
| typescript | 4.9.5 | Apache-2.0 | Type safety |
| @mui/material | 7.3.4 | MIT | UI component library |
| @emotion/react | 11.14.0 | MIT | CSS-in-JS |
| @emotion/styled | 11.14.1 | MIT | Styled components |
| @stripe/react-stripe-js | 5.3.0 | MIT | Stripe integration |
| @stripe/stripe-js | 8.2.0 | MIT | Stripe JS library |
| axios | 1.12.2 | MIT | HTTP client |
| react-scripts | 5.0.1 | MIT | Build tooling |
| @testing-library/react | 16.3.0 | MIT | Testing utilities (dev) |
| @testing-library/jest-dom | 6.9.1 | MIT | Testing utilities (dev) |
| web-vitals | 2.1.4 | Apache-2.0 | Performance metrics |

## Backend Dependencies

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| fastapi | latest | MIT | Web framework |
| uvicorn | latest | BSD-3-Clause | ASGI server |
| sqlalchemy | latest | MIT | ORM |
| psycopg2-binary | latest | LGPL-3.0 | PostgreSQL adapter |
| passlib | 1.7.4 | BSD-3-Clause | Password hashing |
| bcrypt | 4.0.1 | Apache-2.0 | Cryptographic hashing |
| python-jose | latest | MIT | JWT handling |
| python-multipart | latest | Apache-2.0 | Form data parsing |
| strawberry-graphql | latest | MIT | GraphQL support |
| stripe | latest | MIT | Payment processing |
| email-validator | latest | CC0-1.0 | Email validation |
| temporalio | latest | MIT | Workflow orchestration |

## Known Security Considerations

### Pinned Versions (for compatibility)
- `passlib==1.7.4` - Pinned for bcrypt compatibility
- `bcrypt==4.0.1` - Pinned for passlib compatibility

### Intentional Vulnerabilities (for testing demos)
- Session management issues (documented in BUGS.md)
- Error handling gaps (documented in BUGS.md)

## Future Considerations

### Planned Upgrades
- Migration to `pyproject.toml` from `requirements.txt`
- Regular security updates and dependency audits
- Addition of dependency-check CI/CD integration

## Usage

### Validate SBOM
```bash
# Using cyclonedx-cli
cyclonedx-cli validate --input-file sbom.json

# Using OWASP Dependency-Check
dependency-check --project DreamDemo --scan sbom.json
```

### Generate Updated SBOM
```bash
# Frontend
npm run sbom

# Backend
pip-audit --format cyclonedx > backend-sbom.json
```

## Compliance

This SBOM is compliant with:
- CycloneDX 1.5 Specification
- NTIA Minimum Elements for SBOM
- Executive Order 14028 requirements

