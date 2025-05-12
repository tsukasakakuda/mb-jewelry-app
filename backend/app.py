from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        item_file = request.files.get('item_file')
        price_file = request.files.get('price_file')

        item_df = pd.read_csv(item_file)
        price_df = pd.read_csv(price_file)

        item_df.columns = item_df.columns.str.lower()
        price_df.columns = price_df.columns.str.lower()

        item_df['material'] = item_df['material'].str.lower()
        price_df['material'] = price_df['material'].str.lower()

        # データ結合と価格計算
        merged = pd.merge(item_df, price_df, on='material', how='left')
        merged['value'] = merged['weight'] * merged['price']

        # NaN をゼロに置き換え（←これが重要！）
        merged['value'] = merged['value'].fillna(0)

        # name または material を使って返す
        if 'name' in merged.columns:
            results = merged[['name', 'value']].to_dict(orient='records')
        else:
            results = merged[['material', 'value']].to_dict(orient='records')

        return jsonify(results=results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/ping')
def ping():
    return jsonify({"message": "pong"})

if __name__ == '__main__':
    app.run(debug=True, port=5050, host='0.0.0.0')