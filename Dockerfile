# ベースイメージ（Node + Python構成でVueとFlaskをビルド）
FROM node:18 AS build-stage
WORKDIR /app
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Flask本番用イメージ
FROM python:3.9-slim
WORKDIR /app

# Flaskの依存をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# VueのdistをFlask用静的フォルダに配置
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# Flask起動設定（Vueの静的配信を含む app.py を使用）
ENV PORT=8080
CMD ["python", "api.py"]