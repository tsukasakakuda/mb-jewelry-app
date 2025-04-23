# ベースイメージ（Pythonスリム）
FROM python:3.9-slim

# 作業ディレクトリ作成
WORKDIR /app

# 必要ファイルをコピー
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run は PORT を環境変数で受け取る
ENV PORT=8080

# Flask 実行
CMD ["python", "app.py"]