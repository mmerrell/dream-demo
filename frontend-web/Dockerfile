# frontend-web/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Set build-time environment variables
ARG SPRINT_VERSION=sprint-4
ENV REACT_APP_SPRINT_VERSION=$SPRINT_VERSION

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]