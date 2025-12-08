# Contributing to DreamDemo

Thank you for your interest in contributing to DreamDemo! This project aims to provide realistic e-commerce scenarios for testing tool demonstrations, and we welcome contributions that enhance its value for the testing community.

## 🎯 Project Vision

DreamDemo simulates authentic software evolution from "Dreadful" to "Magical" across multiple sprints. Each contribution should support this vision by:
- Maintaining realistic software development scenarios
- Providing comprehensive testing opportunities
- Demonstrating progressive quality improvements
- Supporting diverse testing methodologies and tools

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Basic understanding of React, FastAPI, and PostgreSQL

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dream-demo.git
   cd dream-demo
   ```

2. **Choose your development approach:**
   
   **Full Docker Development (Recommended):**
   ```bash
   docker-compose up --build
   ```
   
   **Hybrid Development (faster iteration):**
   ```bash
   # Start backend services
   docker-compose up db temporal temporal-ui -d
   
   # Frontend development
   cd frontend-web && npm install && npm start
   
   # Backend development  
   cd backend && pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Verify setup:**
   - Frontend: http://localhost:3000 (or 3001 for npm start)
   - Backend API: http://localhost:8000/docs
   - Temporal UI: http://localhost:8080

## 🌿 Sprint Development Guidelines

### Sprint Branching Strategy
- `main`: Production-ready infrastructure and documentation
- `sprint-1`, `sprint-2`, etc.: Individual demo scenarios
- `feature/*`: New features for specific sprints
- `fix/*`: Bug fixes across sprints

### Sprint Characteristics

Each sprint should maintain distinct characteristics:

**Sprint 1** 🌹 - "Dreadful"
- Intentional bugs and poor UX
- Basic functionality with obvious problems
- Minimal error handling
- Simple, outdated styling

**Sprint 2** 🌸 - "Developing"  
- Bug fixes from Sprint 1
- Enhanced backend architecture
- Workflow orchestration introduction
- Improved but still basic UI

**Sprint 3** 🌻 - "Decent"
- Better error handling and user feedback
- UI improvements and notifications
- More robust backend processing
- Enhanced testing scenarios

**Sprint 4** 🌺 - "Decent"
- Professional UI/UX design
- Advanced features and interactions
- Comprehensive error handling
- Production-quality architecture

## 🛠️ Development Standards

### Code Quality

**Frontend (React/TypeScript):**
```typescript
// Use descriptive component names
const EnhancedProductGrid: React.FC<ProductGridProps> = ({ ... }) => {

// Include proper error handling
try {
  const response = await apiCall();
} catch (error) {
  showSnackbar('Operation failed', 'error');
}

// Add accessibility attributes
<Button 
  aria-label={`Add ${product.name} to cart`}
  onClick={handleAddToCart}
>
```

**Backend (FastAPI/Python):**
```python
# Use type hints and validation
@app.post("/orders/", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Order:

# Include proper error handling
try:
    result = await temporal_client.execute_workflow(...)
except Exception as e:
    logger.error(f"Workflow execution failed: {e}")
    raise HTTPException(status_code=500, detail="Order processing failed")
```

### Testing Requirements

**Unit Tests:**
- Frontend: Jest + React Testing Library
- Backend: pytest with SQLAlchemy test fixtures

**Integration Tests:**
- API endpoint testing with TestClient
- Database transaction testing
- Temporal workflow testing

**E2E Tests:**
- Critical user journeys (registration, purchase, order tracking)
- Cross-browser compatibility testing
- Responsive design verification

### Documentation Standards

**Code Documentation:**
```python
def calculate_order_total(items: List[OrderItem]) -> Decimal:
    """
    Calculate the total cost of order items including tax.
    
    Args:
        items: List of order items with price and quantity
        
    Returns:
        Total cost as Decimal with 2 decimal places
        
    Raises:
        ValueError: If any item has invalid price or quantity
    """
```

**API Documentation:**
- All endpoints must include OpenAPI descriptions
- Request/response examples for complex endpoints
- Error response documentation

## 🧪 Testing Contribution Guidelines

### Adding Test Scenarios

When contributing new features, include corresponding test scenarios:

**Functional Testing:**
- Happy path workflows
- Edge case handling
- Error condition testing
- Input validation

**Performance Testing:**
- Load testing scenarios for new endpoints
- Database query optimization verification
- Frontend performance impact assessment

**Accessibility Testing:**
- Keyboard navigation support
- Screen reader compatibility
- ARIA label implementation
- Color contrast verification

### Test Data Management

**Database Seeding:**
- Maintain realistic product catalogs
- Include edge cases (out-of-stock items, varied pricing)
- Preserve user account diversity
- Document any new seed data requirements

## 📋 Submission Process

### Before Submitting

1. **Run the test suite:**
   ```bash
   # Frontend tests
   cd frontend-web && npm test
   
   # Backend tests
   cd backend && python -m pytest
   
   # Integration tests
   docker-compose -f docker-compose.test.yml up --abort-on-container-exit
   ```

2. **Verify cross-sprint compatibility:**
   - Test your changes don't break other sprint branches
   - Ensure infrastructure changes work across all sprints
   - Update documentation for affected sprints

3. **Check code quality:**
   ```bash
   # Frontend linting
   cd frontend-web && npm run lint
   
   # Backend formatting
   cd backend && black . && flake8
   ```

### Pull Request Guidelines

**PR Title Format:**
```
[Sprint X] Feature: Brief description

Examples:
[Sprint 4] Feature: Add product search autocomplete
[Infrastructure] Fix: Resolve Docker networking issues
[Sprint 1-3] Bug: Fix order calculation error
```

**PR Description Template:**
```markdown
## Changes Made
- Brief bullet points of changes

## Sprint Impact  
- Which sprints are affected
- Backwards compatibility considerations

## Testing Performed
- Unit tests added/updated
- Integration testing results
- Manual testing scenarios

## Testing Scenarios Enhanced
- New test cases enabled by this change
- Demo scenarios improved

## Screenshots (if UI changes)
- Before/after comparisons
- Mobile responsiveness verification
```

### Review Process

1. **Automated Checks**: CI pipeline must pass
2. **Code Review**: At least one maintainer approval
3. **Testing Verification**: Manual testing of key scenarios
4. **Documentation Review**: Ensure docs are updated
5. **Sprint Integration**: Verify compatibility across affected sprints

## 🔍 Issue Reporting

### Bug Reports

Use this template for bug reports:
```markdown
**Sprint Affected**: Sprint X

**Environment**:
- OS: [e.g., macOS, Windows, Linux]
- Browser: [e.g., Chrome 91, Firefox 89]
- Docker version: [e.g., 20.10.7]

**Steps to Reproduce**:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**:
A clear description of expected outcome

**Actual Behavior**:
What actually happened

**Testing Impact**:
How this affects testing scenarios
```

### Feature Requests

Consider these questions for feature requests:
- Which sprint(s) would benefit from this feature?
- How does this enhance testing scenarios?
- What new test cases would this enable?
- Is this realistic for the target sprint's maturity level?

## 🌟 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes for significant contributions  
- Special recognition for testing scenario improvements

## 📞 Communication

- **Issues**: GitHub Issues for bugs and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Documentation**: Wiki for detailed implementation guides

## 🔄 Continuous Improvement

We regularly review and update these guidelines based on:
- Community feedback
- Project evolution
- Testing industry best practices
- Sprint development insights

Thank you for contributing to DreamDemo and supporting the testing community! 🧪

---

*For questions about these guidelines, please open a GitHub Discussion or contact the maintainers.*
