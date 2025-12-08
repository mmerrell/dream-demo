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
   
   In a new terminal:
```bash
   docker-compose exec backend python seed_database.py
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

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines, coding standards, and submission process.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

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

