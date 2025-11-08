# DreamDemo Flower Shop - Development Roadmap

## Sprint Overview
This roadmap outlines the planned development across multiple sprints, showcasing realistic software evolution and the value of comprehensive testing with Sauce Labs.

---

## Sprint 1: Foundation ✅ COMPLETE
**Goal:** Core e-commerce functionality with intentional bugs

### Completed Features
- ✅ User authentication (register, login, JWT tokens)
- ✅ Product catalog with 300 seed products
- ✅ Shopping cart functionality
- ✅ Order creation and management
- ✅ Stripe payment integration
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ React TypeScript frontend with Material-UI
- ✅ Docker Compose orchestration

### Known Bugs (Intentional - for demo purposes)
- 🐛 Intrusive alert() dialogs instead of proper notifications
- 🐛 Poor session expiration messaging (✅ Fixed in sprint-2)
- 🐛 Duplicate email registration doesn't provide clear feedback (✅ Fixed in sprint-2)
- 🐛 No order cancellation functionality (✅ Fixed in sprint-2)
- 🐛 HTTPException used in non-HTTP contexts (✅ Fixed in sprint-3)

### Documentation
- ✅ BUGS.md created with all known issues
- ✅ SBOM.json (CycloneDX format)
- ✅ README.md

---

## Sprint 2: Bug Fixes ✅ COMPLETE
**Goal:** Address critical bugs and enhance workflow orchestration

### Completed Features
- ✅ Payment processing workflow (ProcessPaymentWorkflow)
- ✅ Multi-step order fulfillment (check inventory → allocate → notify → confirm)
- ✅ Separate workers for different task queues
- ✅ Activity-based architecture with proper error handling
- ✅ Load testing infrastructure (process_pending_orders.py)
- ✅ Order cancellation workflow
- ✅ Improved session expiration handling

### Bug Fixes
- ✅ InsufficientInventoryError - proper exception handling in activities
- ✅ User-friendly exceptions throughout workflow layer

### Remaining Bugs (Deferred to Sprint 3)
- 🐛 Intrusive alert() dialogs

---

## Sprint 3: UX Improvements 🚧 IN PROGRESS
**Goal:** Polish user experience and add order management

### Planned Features
- ✅ Replace alert() with MUI Snackbar/Toast notifications
- ✅ Improved session expiration handling
  - Detect 401 responses
  - Clear auth state and redirect to login
  - Preserve cart contents
- ✅ Better error messages on duplicate email registration
- ✅ Order filtering
- [ ] Order search
- ✅ Order status updates (real-time or polling)

### Bug Fixes
- ✅ Fix: Intrusive alert() dialogs

### Testing Focus
- End-to-end payment flows
- Error handling and recovery
- Session management
- Order lifecycle management

---

## Sprint 4: Payment Workflows + Microservices
**Goal:** Comprehensive payment handling and begin microservices architecture

### Payment Workflow Enhancement 🎯 HIGH PRIORITY
**Problem:** Declined cards fail in Stripe.js on frontend with no workflow visibility

**Implementation:**
1. **Start payment workflow immediately on order creation**
   - Don't wait for Stripe success
   - Every order gets a workflow
   - Order stays in system regardless of payment outcome

2. **Create `wait_for_payment_activity`**
   ```python
   @activity.defn
   async def wait_for_payment_activity(order_id: int) -> dict:
       """Poll database for payment confirmation up to 10 minutes"""
       # Returns: succeeded/failed/declined/timeout
   ```

3. **Update `ProcessPaymentWorkflow`**
   - First step: wait for payment confirmation
   - Handle declined cards gracefully
   - Update order status: payment_failed, payment_declined, payment_timeout
   - Release inventory on failure (compensating transaction)
   - Log to analytics/monitoring

4. **Add payment retry mechanism**
   - Allow users to retry failed payments
   - Keep original order, update payment method

**Benefits:**
- ✅ Payment failures trackable and debuggable
- ✅ Showcases saga patterns and compensating transactions
- ✅ Can retry failed payments without recreating order
- ✅ Complete order lifecycle from creation to final state

**Files to modify:**
- `workflows/process_payment.py`
- `activities/order_activities.py` 
- `main.py` - order creation endpoint
- `models.py` - add `payment_status` field to Order model
- `schemas.py` - payment status enum

**Alternative approach:** Use signals instead of polling (more elegant)

### Microservices Architecture - Phase 1

**Email/Notification Service (Node.js)**
- Separate service for all notifications
- Email, SMS, push notifications
- Event-driven architecture
- Real SMTP with Mailpit for development

**Implementation:**
```yaml
# docker-compose.yml additions
notification-service:
  build: ./notification-service
  ports:
    - "3001:3001"
  environment:
    - SMTP_HOST=mailpit
    - SMTP_PORT=1025

mailpit:
  image: axllent/mailpit
  ports:
    - "1025:1025"  # SMTP
    - "8025:8025"  # Web UI
```

**Features:**
- Order confirmation emails
- Shipping notifications
- Payment failure alerts
- Template system
- Delivery tracking and logging
- Visible in Mailpit UI at localhost:8025

### Other Planned Features
- [ ] Webhook signature verification (re-enable Stripe signature check)
- [ ] Flower arrangement image thumbnails
- [ ] Idempotent workflow IDs (prevent duplicate processing)
- [ ] Workflow status polling endpoint
- [ ] Frontend workflow status display

### Testing Focus
- Payment failure scenarios
- Workflow retries and compensations
- Microservice communication
- Email delivery verification

---

## Sprint 5: Java Inventory Service
**Goal:** Extract inventory management into Java microservice

### Inventory Service (Java/Spring Boot)
**Why Java:** 
- Demonstrate polyglot microservices
- Showcase JPA/Hibernate for complex inventory operations
- Strong typing for financial/inventory calculations
- Good for high-concurrency scenarios

**Core Responsibilities:**
1. **Stock Level Management**
   - Query current inventory levels
   - Reserve inventory (hold items during checkout)
   - Commit reservations (finalize on payment)
   - Release reservations (cancel/timeout)
   - Adjust stock levels (restocking, damages, returns)

2. **Warehouse Operations**
   - Multi-warehouse support (East Coast, West Coast, International)
   - Warehouse allocation logic (closest to customer, most stock, cost optimization)
   - Transfer between warehouses
   - Low stock alerts and auto-reordering

3. **Inventory History & Auditing**
   - Track all inventory movements
   - Reservation history and timeline
   - Adjustment logs with reasons
   - Reconciliation reports
   - Audit trail for compliance

**API Endpoints:**
```
GET    /inventory/products/{product_id}           # Check stock level
POST   /inventory/reserve                         # Reserve items for order
POST   /inventory/commit/{reservation_id}         # Finalize reservation
POST   /inventory/release/{reservation_id}        # Cancel reservation
GET    /inventory/reservations/{order_id}         # Get order's reservations
POST   /inventory/adjust                          # Manual stock adjustment
GET    /inventory/warehouses                      # List warehouses
GET    /inventory/low-stock                       # Products below threshold
POST   /inventory/transfer                        # Warehouse transfer
```

**Database (Separate PostgreSQL instance):**
```yaml
inventory_levels:
  - product_id
  - warehouse_id
  - quantity_available
  - quantity_reserved
  - last_updated

inventory_reservations:
  - id
  - order_id
  - product_id
  - warehouse_id
  - quantity
  - status (pending, committed, released, expired)
  - reserved_at
  - expires_at (15 minutes default)
  - committed_at

inventory_movements:
  - id
  - product_id
  - warehouse_id
  - movement_type (reservation, commit, release, adjustment, transfer, restock)
  - quantity_delta
  - reference_id
  - reason
  - created_by
  - created_at

warehouses:
  - id
  - name
  - location
  - priority
  - capacity
  - active
```

**Workflow Integration:**
- Inventory reservation workflow (reserve → wait → commit/release)
- Auto-release reservations after 15 minutes
- Low stock alert workflow
- Warehouse transfer workflow (with shipping delay simulation)

**Simulated Complexity (for realistic testing):**
```yaml
performance:
  query_delay_ms: 300-800       # Simulate database queries
  lock_contention_rate: 0.15    # 15% chance of lock wait
  cache_miss_rate: 0.30         # 30% cache misses require DB lookup
  
chaos_engineering:
  enabled: true
  failure_rate: 0.05            # 5% random failures
  slow_query_rate: 0.10         # 10% very slow queries (3-5s)
  warehouse_offline_rate: 0.02  # 2% warehouse temporarily unavailable
```

**Updated Order Workflow:**
```
1. Create Order Intent
2. → Call Inventory Service: Reserve Stock
   - If successful: Continue
   - If failed: Abort order, return error
3. Wait for Payment (with 15-min reservation timeout)
4. On Payment Success:
   - → Call Inventory Service: Commit Reservation
   - Continue to fulfillment
5. On Payment Failure/Timeout:
   - → Call Inventory Service: Release Reservation
   - Update order status
```

**Technology Stack:**
- Spring Boot 3.x
- Temporal Java SDK
- JPA/Hibernate
- PostgreSQL
- Lombok (reduce boilerplate)
- MapStruct (entity/DTO mapping)
- Testcontainers (integration tests)

**Files:**
```
inventory-service/
├── src/main/java/com/saucelabs/inventory/
│   ├── InventoryServiceApplication.java
│   ├── controller/
│   │   └── InventoryController.java
│   ├── service/
│   │   ├── InventoryService.java
│   │   └── ReservationService.java
│   ├── temporal/
│   │   ├── workflows/
│   │   │   ├── ReservationWorkflow.java
│   │   │   └── LowStockAlertWorkflow.java
│   │   └── activities/
│   │       └── InventoryActivities.java
│   ├── repository/
│   │   ├── InventoryLevelRepository.java
│   │   └── ReservationRepository.java
│   └── model/
│       ├── InventoryLevel.java
│       └── Reservation.java
├── pom.xml
└── Dockerfile
```

### Testing Focus
- Distributed transaction testing
- Inventory race conditions
- Reservation timeout handling
- Multi-language microservice integration
- Chaos engineering scenarios

---

## Sprint 6: Advanced Features
**Goal:** Production-grade features and observability

### Planned Features
- [ ] **Feature Flags System**
  - Toggle features without deployment
  - A/B testing support
  - Gradual rollout capability
  
- [ ] **GraphQL API** (alongside REST)
  - Already have strawberry-graphql installed
  - Product catalog queries
  - Order management mutations
  - Real-time subscriptions
  
- [ ] **Real-time Order Updates**
  - WebSocket connections
  - Push notifications to frontend
  - Order status streaming
  
- [ ] **Product Recommendations**
  - "Customers also bought..."
  - ML-based suggestions
  - Collaborative filtering
  
- [ ] **Multiple Payment Providers**
  - Keep Stripe as primary
  - Add mock Venmo/PayPal
  - Add mock Apple Pay
  - Payment provider selection workflow
  
- [ ] **Observability Stack**
  - OpenTelemetry integration
  - Distributed tracing
  - Metrics dashboard (Prometheus + Grafana)
  - Log aggregation (ELK stack)

### Testing Focus
- Feature flag behavior
- GraphQL query optimization
- WebSocket connection handling
- Payment provider fallback
- Performance under load

---

## Sprint 7: Migration to pyproject.toml
**Goal:** Modernize Python dependency management

### Migration Tasks
- [ ] Convert requirements.txt to pyproject.toml
- [ ] Set up Poetry or pip-tools
- [ ] Update Dockerfile build process
- [ ] Update docker-compose volumes
- [ ] Dependency lock files
- [ ] CI/CD pipeline updates
- [ ] Documentation updates

**Implications:**
- Dockerfile changes (poetry install vs pip install)
- Developer onboarding docs
- CI/CD configuration
- Dependency resolution improvements
- Better dev/prod dependency separation

### Testing Focus
- Build process validation
- Dependency conflict resolution
- Docker image size optimization

---

## Sprint 8: Internationalization (i18n)
**Goal:** Multi-language support

### Implementation
- [ ] i18next integration (frontend)
- [ ] Language detection
- [ ] Translation files (en, es, fr, de, ja)
- [ ] RTL language support (Arabic, Hebrew)
- [ ] Currency localization
- [ ] Date/time formatting
- [ ] Backend locale handling

### Testing Focus
- Language switching
- RTL layout testing
- Translation completeness
- Currency conversion
- Locale-specific formatting

---

## Sprint 9: Chaos Engineering
**Goal:** Test system resilience

### Chaos Scenarios
- [ ] **Service Failures**
  - Random service crashes
  - Network partitions
  - Database connection failures
  
- [ ] **Performance Degradation**
  - Slow database queries
  - High latency networks
  - Memory pressure
  
- [ ] **Data Consistency**
  - Duplicate message handling
  - Partial failures
  - Retry storms
  
- [ ] **Resource Exhaustion**
  - Connection pool depletion
  - Memory leaks
  - CPU saturation

**Tools:**
- Chaos Mesh or Toxiproxy
- Custom failure injection

### Testing Focus
- System recovery
- Data consistency under failure
- User experience during degradation
- Alert/monitoring accuracy

---

## Sprint 10: Security Hardening
**Goal:** Production-ready security

### Security Enhancements
- [ ] **Authentication & Authorization**
  - OAuth2/OIDC integration
  - Role-based access control (RBAC)
  - API key management
  - Rate limiting
  
- [ ] **Input Validation**
  - Comprehensive input sanitization
  - SQL injection prevention (audit)
  - XSS prevention
  - CSRF protection
  
- [ ] **Secrets Management**
  - HashiCorp Vault integration
  - Encrypted environment variables
  - Secret rotation
  
- [ ] **Security Headers**
  - HSTS
  - CSP
  - X-Frame-Options
  
- [ ] **Dependency Scanning**
  - Automated CVE checking
  - SBOM updates
  - License compliance

### Testing Focus
- Penetration testing
- Security scanning automation
- Secrets exposure detection
- Authentication bypass attempts

---

## Future Considerations (Backlog)

### Advanced Workflow Management Features
- Saga pattern demonstrations
- Long-running workflows (days/weeks)
- Workflow versioning strategies
- Workflow cron jobs
- Parent-child workflow orchestration

### Additional Microservices
- [ ] **Analytics Service (Node.js)**
  - Event tracking
  - Real-time dashboards
  - Business intelligence
  
- [ ] **Search Service (Elasticsearch)**
  - Full-text product search
  - Faceted navigation
  - Autocomplete
  
- [ ] **Image Service (Go)**
  - Image optimization
  - Multiple sizes/formats
  - CDN integration

### DevOps & Infrastructure
- [ ] Kubernetes deployment
- [ ] Helm charts
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated testing suite
- [ ] Performance benchmarking
- [ ] Blue-green deployments
- [ ] Canary releases

### Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Architecture decision records (ADRs)
- [ ] Developer onboarding guide
- [ ] Testing strategy document
- [ ] Incident response playbook

---

## Success Metrics

### Technical Metrics
- Test coverage > 80%
- API response time < 200ms (p95)
- Workflow success rate > 99%
- Zero critical security vulnerabilities
- SBOM up-to-date and validated

### Demo Metrics
- Showcases 5+ testing scenarios
- Demonstrates polyglot architecture
- Utilizes workflow capabilities
- Shows realistic bug discovery and fixing
- Proves value of comprehensive testing

---

## Notes for Sauce Labs Demos

### Key Selling Points
1. **Realistic Software Evolution**
   - Shows how software actually develops
   - Bugs discovered and fixed across sprints
   - Technical debt addressed incrementally

2. **Comprehensive Testing Needs**
   - Multiple languages (Python, Java, Node.js, TypeScript)
   - Multiple platforms (web, API, workflows)
   - Multiple testing types (E2E, integration, chaos, security)

3. **Modern Architecture**
   - Microservices
   - Event-driven
   - Workflow orchestration
   - Real-time features

4. **Testing Challenges**
   - Async workflows (hard to test)
   - Distributed systems (race conditions)
   - Payment processing (requires mocking)
   - Multi-language (different test tools)
   - Workflow replay (determinism requirements)

### Demo Scenarios to Highlight
- Order creation with intentional bugs (Sprint 1)
- Payment failure handling (Sprint 4)
- Inventory race conditions (Sprint 5)
- Chaos engineering resilience (Sprint 9)
- i18n testing across locales (Sprint 8)
- Cross-service integration tests
- Workflow testing strategies

## 🗺 Aspirational Roadmap

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
- [ ] **Internationalization (i18n) - Multi-language Support**
  - [ ] English (en-US) - default
  - [ ] French (fr-FR)
  - [ ] Spanish (es-ES)
  - [ ] Arabic (ar-SA) - includes RTL layout support
  - [ ] Japanese (ja-JP)
  - [ ] Translation files for all UI text, labels, buttons, messages
  - [ ] Locale-aware date/time formatting
  - [ ] Currency display per locale
  - [ ] Language selector in header
  - [ ] Product names: remain in English (inventory consistency)

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
