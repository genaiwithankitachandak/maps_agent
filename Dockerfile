# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the production bundle
RUN npm run build

# Stage 2: Build the Python backend and serve
FROM python:3.13-slim

WORKDIR /app

# Upgrade pip and install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY . .

# Copy the built React application from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the port Cloud Run uses
EXPOSE 8080

# Command to run the unified application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
