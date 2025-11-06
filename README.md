# Dream Demo - E-Commerce Flower Shop

A full-stack e-commerce application designed to demonstrate comprehensive testing capabilities with Sauce Labs. This project intentionally includes both working features and documented bugs to showcase real-world testing scenarios.

## 🎯 Project Goals

This application serves as the ultimate demo for Sauce Labs testing features, showcasing:

- **Complex Web Application Testing**: Multi-page flows, authentication, payments
- **Third-Party Integrations**: Stripe payments, future support for Venmo, CashApp
- **API Testing**: RESTful backend with FastAPI
- **Database Operations**: PostgreSQL with inventory management
- **Detailed Logging**: Comprehensive workflow tracking and monitoring
- **Intentional Bugs**: Documented issues for testing and debugging demonstrations

## 🏗️ Architecture

**Current Stack:**
- **Frontend**: React with TypeScript, Material-UI components
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL 13
- **Payment Processing**: Stripe (test mode)
- **Containerization**: Docker Compose

**Tech Stack:**
```
Frontend (Port 3000)
    ├── React 18
    ├── TypeScript
    ├── Material-UI (MUI)
    ├── Axios
    └── Stripe.js

Backend (Port 8000)
    ├── FastAPI
    ├── SQLAlchemy
    ├── Pydantic
    ├── python-jose (JWT)
    ├── passlib (bcrypt)
    └── Stripe Python SDK

Database (Port 5432)
    └── PostgreSQL 13
```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Stripe test account (free at [stripe.com](https://stripe.com))
- Git

### Installation

1. **Clone the repository:**
```bash
   git clone <repository-url>
   cd dream-demo
```

2. **Set up environment variables:**
   
   Create a `.env` file in the project root:
```bash
   # .env
   STRIPE_SECRET_KEY=sk_test_your_secret_key_here
   STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

   **Getting Stripe Keys:**
   - Sign up at https://dashboard.stripe.com/register
   - Navigate to https://dashboard.stripe.com/test/apikeys
   - Copy both "Publishable key" (pk_test_...) and "Secret key" (sk_test_...)
   - Paste into your `.env` file

3. **Build and start all services:**
```bash
   docker-compose up --build
```

   This will start:
   - Frontend at http://localhost:3000
   - Backend API at http://localhost:8000
   - Backend API docs at http://localhost:8000/docs
   - PostgreSQL database at localhost:5432

4. **Seed the database with products:**
   
   In a new terminal, from the project root directory:
```bash
   # Install requests library if not already installed
   pip3 install --break-system-packages requests
   
   # Run the seed script
   python3 scripts/seed_database.py
```

5. **Access the application:**
   
   Open http://localhost:3000 in your browser

### Test Credentials

**Stripe Test Cards:**
- Success: `4242 4242 4242 4242`
- Declined: `4000 0000 0000 0002`
- Insufficient funds: `4000 0000 0000 9995`
- Any future expiry date (e.g., 12/34)
- Any 3-digit CVC (e.g., 123)

More test cards: https://stripe.com/docs/testing

## 🐛 Known Bugs

This application intentionally contains bugs for testing demonstrations. See [BUGS.md](./BUGS.md) for:
- Documented issues and their severity
- Reproduction steps
- Expected vs. actual behavior
- Potential fixes (not implemented)

These bugs are valuable for:
- Demonstrating test automation capabilities
- Showcasing bug detection and reporting
- Training on QA workflows
- Proving ROI of testing tools

## 📋 Features

### Implemented
- ✅ User registration and authentication (JWT)
- ✅ Product catalog with 300+ flower products
- ✅ Shopping cart management
- ✅ Order placement and tracking
- ✅ Stripe payment integration
- ✅ Inventory management
- ✅ Order fulfillment workflow
- ✅ Email confirmation (mocked)
- ✅ Session persistence

### E-Commerce Workflow
1. Browse products (anonymous or authenticated)
2. Add items to cart
3. Register/Login
4. Place order (creates pending order)
5. Pay with Stripe (triggers workflow)
6. Inventory allocation
7. Fulfillment notification
8. Customer confirmation
9. Order completion

## 🛠️ Development

### Project Structure
```
dream-demo/
├── frontend-web/          # React frontend
│   ├── src/
│   │   ├── App.tsx       # Main application
│   │   ├── components/   # React components
│   │   └── services/     # API service layer
│   ├── public/           # Static assets
│   └── Dockerfile
├── backend/              # FastAPI backend
│   └── app/
│       ├── main.py       # API endpoints
│       ├── models.py     # Database models
│       ├── schemas.py    # Pydantic schemas
│       ├── crud.py       # Database operations
│       ├── security.py   # Auth & hashing
│       └── config.py     # Configuration
├── docker-compose.yml    # Container orchestration
├── .env                  # Environment variables (not in git)
├── BUGS.md              # Known issues documentation
└── README.md            # This file
```

### Common Commands

**Start services:**
```bash
docker-compose up
```

**Restart a service:**
```bash
docker-compose restart backend
docker-compose restart frontend
```

**View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Install frontend packages:**
```bash
docker-compose exec frontend npm install <package-name>
```

**Install backend packages:**
```bash
docker-compose exec backend pip install <package-name>
```

**Rebuild after dependency changes:**
```bash
docker-compose build --no-cache
docker-compose up
```

**Stop all services:**
```bash
docker-compose down
```

**Clean up volumes (WARNING: deletes database):**
```bash
docker-compose down -v
```

## 🗺️ Roadmap

## 🗺️ Roadmap

### Phase 1: Enhanced Infrastructure
- [ ] AWS/GCP deployment configurations
- [ ] Kubernetes orchestration
- [ ] gRPC service communication
- [ ] Kafka event streaming
- [ ] Configuration-driven architecture (YAML-based service orchestration)
- [ ] Microservices split: auth, products, orders, payments, notifications, inventory services

### Phase 2: Observability & Analytics
- [ ] OpenTelemetry integration
- [ ] Grafana dashboards
- [ ] ReportPortal.io test reporting
- [ ] Google Analytics tracking
- [ ] Mixpanel user analytics
- [ ] Segment multi-destination analytics
- [ ] Structured logging with ELK stack
- [ ] Backtrace for production-level error monitoring

### Phase 3: Payment & Inventory Expansion
- [ ] Venmo integration
- [ ] CashApp integration
- [ ] PayPal integration
- [ ] Open-source inventory management system
- [ ] Multi-warehouse support
- [ ] Real-time inventory updates via WebSocket
- [ ] ShipStation/EasyPost shipping integration

### Phase 4: Advanced Features
- [ ] Feature flags (LaunchDarkly or custom)
- [ ] A/B testing framework
- [ ] Internationalization (i18n) - multi-language support
- [ ] Currency conversion
- [ ] Progressive Web App (PWA) features
- [ ] Dark mode toggle
- [ ] Product recommendations engine
- [ ] Order tracking with shipping carriers
- [ ] Customer reviews and ratings
- [ ] Promotional codes and discounts
- [ ] Admin dashboard
- [ ] Social authentication (Google/Facebook OAuth)

### Phase 5: Real-time & Communication
- [ ] WebSocket connections for live updates
- [ ] Customer support chat
- [ ] SendGrid email integration
- [ ] Twilio SMS notifications
- [ ] Push notifications
- [ ] Real-time inventory alerts

### Phase 6: Mobile & Accessibility
- [ ] QR code scanning
- [ ] Camera integration for product reviews
- [ ] Geolocation-based features
- [ ] Touch gesture support
- [ ] Enhanced accessibility (WCAG compliance)
- [ ] Screen reader optimization
- [ ] Keyboard navigation improvements

### Phase 7: Advanced Testing Scenarios
- [ ] Chaos engineering (configurable failure modes)
- [ ] GraphQL API endpoint
- [ ] Complex user journey flows
- [ ] Multi-tab workflow testing
- [ ] File upload capabilities
- [ ] Infinite scroll/pagination
- [ ] Autocomplete search
- [ ] CAPTCHA handling
- [ ] Browser storage testing (cookies, localStorage, IndexedDB)

### Phase 8: Testing Showcase
- [ ] Selenium test suites
- [ ] Cypress E2E tests
- [ ] Playwright test scenarios
- [ ] API test collections (Postman/RestAssured)
- [ ] Performance testing scenarios
- [ ] Visual regression tests
- [ ] Accessibility testing suites
- [ ] Mobile responsive testing
- [ ] Cross-browser compatibility tests
- [ ] Load testing with concurrent users
- [ ] Security testing demonstrations
- [ ] Contract testing for microservices

### Phase 9: Production Realism
- [ ] Rate limiting and throttling
- [ ] Database connection pooling
- [ ] Cache strategies (Redis)
- [ ] CDN integration
- [ ] SSL/TLS configuration
- [ ] Intentional performance bottlenecks (for testing)
- [ ] Security vulnerability scenarios (test mode)
- [ ] CORS and CSRF handling demonstrations
- [ ] Retry logic and circuit breakers
- [ ] Graceful degradation patterns

## 🎯 Sauce Labs Integration

This application is specifically designed to showcase:

- **Cross-browser testing**: Test across Chrome, Firefox, Safari, Edge
- **Mobile testing**: iOS and Android device testing
- **Visual testing**: Screenshot comparison and visual regression
- **API testing**: Backend endpoint validation
- **Performance testing**: Load testing and bottleneck identification
- **Test orchestration**: Parallel test execution
- **CI/CD integration**: Automated testing pipelines
- **Test analytics**: Comprehensive test reporting and insights

## 🤝 Contributing

This is an internal demo project. For questions or suggestions, contact the Sauce Labs demo team.

## 📝 License

Internal use only - Sauce Labs, Inc.

## 🆘 Troubleshooting

**"Module not found" errors in frontend:**
```bash
docker-compose exec frontend npm install
docker-compose restart frontend
```

**Database connection errors:**
```bash
docker-compose down -v
docker-compose up
# Then re-seed: docker-compose exec backend python seed_database.py
```

**Stripe payment fails:**
- Verify `.env` file has correct keys
- Check keys start with `sk_test_` and `pk_test_`
- Restart backend after adding keys

**Port already in use:**
```bash
# Find process using port 3000/8000/5432
lsof -i :3000
# Kill process or change port in docker-compose.yml
```

**Frontend shows blank page:**
- Check browser console for errors
- Verify backend is running: http://localhost:8000/docs
- Check docker logs: `docker-compose logs frontend`

## 📧 Support

For technical support or questions about this demo:
- Internal Wiki: [link-to-wiki]
- Slack: #demo-support
- Email: demo-team@saucelabs.com