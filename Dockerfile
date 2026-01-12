# Multi-stage Dockerfile for PyRelDB
# Runs both backend and frontend in production mode

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY web-app/package*.json ./
RUN npm install
COPY web-app/ ./
RUN npm run build

# Stage 2: Python backend with frontend static files
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy Python application
COPY pyreldb/ ./pyreldb/
COPY web-app/backend/ ./web-app/backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./web-app/build

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Run application
CMD ["python", "-m", "web-app.backend.app"]

