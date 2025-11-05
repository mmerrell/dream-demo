## Quick Start with Public Images

1. **Download the compose file:**
```bash
   wget https://raw.githubusercontent.com/yourusername/dream-demo/main/docker-compose.public.yml
   wget https://raw.githubusercontent.com/yourusername/dream-demo/main/.env.template
```

2. **Set up environment:**
```bash
   cp .env.template .env
   # Edit .env with your Stripe keys
```

3. **Start the application:**
```bash
   docker compose -f docker-compose.public.yml up
```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Temporal UI: http://localhost:8080