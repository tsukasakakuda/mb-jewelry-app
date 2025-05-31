# フロントエンドビルド用ステージ
FROM node:18 AS build-stage
WORKDIR /app
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Pythonバックエンドステージ
FROM python:3.9-slim
WORKDIR /app

# ✅ requirements を正しいパスからコピー
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ✅ api.py や他のバックエンドファイルをコピー
COPY backend/ .

# ✅ ビルド済みのフロントを dist にコピー
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# ✅ ポート明示（Cloud Run用）
ENV PORT=8080

# ✅ エントリーポイントをapi.pyに
CMD ["python", "api.py"]