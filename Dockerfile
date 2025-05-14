# Dockerfile
FROM node:18 AS build-stage
WORKDIR /app
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install && npm run build

FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .
COPY --from=build-stage /app/frontend/dist ./frontend/dist
ENV PORT=8080
CMD ["python", "backend/api.py"]