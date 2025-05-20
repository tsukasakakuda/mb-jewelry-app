# Dockerfile
FROM node:18 AS build-stage
WORKDIR /app
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install && npm run build

FROM python:3.9-slim
WORKDIR /app

#COPY backend/requirements.txt ./
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#COPY . .
COPY backend/ .       

COPY --from=build-stage /app/frontend/dist ./frontend/dist

#これは追加
ENV PORT=8080

#CMD ["python", "backend/api.py"]
CMD ["python", "api.py"]