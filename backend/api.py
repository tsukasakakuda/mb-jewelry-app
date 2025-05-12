# ✅ api.py
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import numpy as np
import pandas as pd
import re
import io
import os

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)

@app.route('/')
def serve_vue():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/check-weights', methods=['POST'])
def check_weights():
    try:
        file = request.files.get('item_file')
        if not file:
            return jsonify({'error': 'item_file is required'}), 400
        df = pd.read_csv(file)
        invalids = []
        for idx, row in df.iterrows():
            val = row.get('weight')
            if pd.isna(val) or str(val).strip() == "":
                continue
            try:
                cleaned = re.sub(r'[^0-9.]', '', str(val).split('g')[0])
                float(cleaned)
            except Exception:
                clean_row = row.fillna("").to_dict()
                invalids.append({
                    'index': idx,
                    'weight': val,
                    'box_id': row.get('box_id', ''),
                    'box_no': row.get('box_no', ''),
                    'row_data': clean_row
                })
        return jsonify({'invalid_weights': invalids})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_items(item_df, price_df):
    price_df['price'] = pd.to_numeric(price_df['price'], errors='coerce').fillna(0)
    price_dict = dict(zip(price_df['material'].str.lower(), price_df['price']))
    def calculate(row):
        try:
            raw = str(row['weight']).split('g')[0]
            cleaned = re.sub(r'[^0-9.]', '', raw)
            total_weight = float(cleaned) if cleaned else 0.0
        except Exception:
            total_weight = 0.0
        gemstone_weight = 0.0
        material_price = 0.0
        parts = str(row['misc']).split() if pd.notna(row['misc']) else []
        material_name = str(row['material']).strip().lower() if pd.notna(row['material']) else None
        if material_name and material_name in price_dict:
            for part in parts:
                if any(x in part for x in ['#', 'cm', '%']):
                    continue
                matches = re.findall(r'(\d+(?:\.\d+)?)', part)
                if matches:
                    num = float(matches[0])
                    if 'mm' in part:
                        gemstone_weight += num ** 3 / 700
                    elif '.' in part:
                        gemstone_weight += num * 0.2
            material_price = price_dict.get(material_name, 0)
            material_weight = total_weight - gemstone_weight
            material_value = material_weight * material_price
        else:
            material_weight = 0
            material_value = 0
        return pd.Series([material_value, material_price, total_weight, gemstone_weight, material_weight])
    item_df[['jewelry_price', 'material_price', 'total_weight', 'gemstone_weight', 'material_weight']] = item_df.apply(calculate, axis=1)
    return item_df

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        item_file = request.files.get('item_file')
        price_file = request.files.get('price_file')
        if not item_file or not price_file:
            return jsonify({'error': 'Both files are required'}), 400
        item_df = pd.read_csv(item_file)
        price_df = pd.read_csv(price_file)
        result_df = calculate_items(item_df, price_df)
        output = io.StringIO()
        result_df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='calculated_result.csv'
        )
    except Exception as e:
        print("エラー詳細:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/calculate-fixed', methods=['POST'])
def calculate_fixed():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON provided'}), 400
        item_df = pd.DataFrame(data.get('item_data', []))
        for idx, row in item_df.iterrows():
            if 'weight' in row and str(row['weight']).strip() == "":
                item_df.at[idx, 'weight'] = None
        price_df = pd.DataFrame(data.get('price_data', []))
        result_df = calculate_items(item_df, price_df)
        result_df['box_no'] = pd.to_numeric(result_df['box_no'], errors='coerce').fillna(0).astype(int)
        result_df['box_id'] = pd.to_numeric(result_df['box_id'], errors='coerce').fillna(0).astype(int)
        result_df = result_df.sort_values(by=['box_no', 'box_id'])
        if 'original_index' in result_df.columns:
            result_df = result_df.drop(columns=['original_index'])
        output = io.StringIO()
        result_df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='calculated_result.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"\n✅ Starting Flask on port {port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)