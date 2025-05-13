# Multi-stage build to include Vue build and Flask API
# Build frontend
FROM node:18 AS build-stage
WORKDIR /app
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Build backend with Flask
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=build-stage /app/frontend/dist ./frontend/dist
ENV PORT=8080
CMD ["python", "backend/api.py"]