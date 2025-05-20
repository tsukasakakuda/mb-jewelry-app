from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import numpy as np
import pandas as pd
import re
import io
import os

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)

def ensure_required_columns(df, required_columns):
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    return df

def check_invalid_weights(df):
    invalid_rows = []
    for idx, row in df.iterrows():
        weight_value = str(row.get('weight', '')).strip()
        if weight_value:
            try:
                cleaned = re.sub(r'[^0-9.]', '', weight_value.split('g')[0])
                float(cleaned)
            except ValueError:
                invalid_rows.append({
                    'index': idx,
                    'weight': weight_value,
                    'row_data': row.to_dict()
                })
    return invalid_rows

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

        required_columns = ['box_id', 'box_no', 'material', 'misc', 'weight']
        df = ensure_required_columns(df, required_columns)

        invalids = []
        for idx, row in df.iterrows():
            val = row.get('weight')
            if pd.isna(val) or str(val).strip() == "":
                continue
            val = str(val).strip()
            try:
                cleaned = re.sub(r'[^0-9.]', '', val.split('g')[0])
                float(cleaned)
            except Exception:
                clean_row = row.to_dict()
                for k, v in clean_row.items():
                    if pd.isna(v) or (isinstance(v, float) and np.isnan(v)):
                        clean_row[k] = ""
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

@app.route('/calculate-fixed', methods=['POST'])
def calculate_fixed():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON provided'}), 400

        item_df = pd.DataFrame(data.get('item_data', []))
        price_df = pd.DataFrame(data.get('price_data', []))

        for idx, row in item_df.iterrows():
            if 'weight' in row and str(row['weight']).strip() == "":
                item_df.at[idx, 'weight'] = None

        required_columns = ['box_id', 'box_no', 'material', 'misc', 'weight']
        item_df = ensure_required_columns(item_df, required_columns)

        result_df = calculate_items(item_df, price_df)

        result_df['box_no'] = pd.to_numeric(result_df['box_no'], errors='coerce').fillna(0).astype(int)
        result_df['box_id'] = pd.to_numeric(result_df['box_id'], errors='coerce').fillna(0).astype(int)
        result_df = result_df.sort_values(by=['box_no', 'box_id'], ascending=[True, True])

        # ✅ 必要なカラムだけに制限
        output_columns = [
            'box_id', 'box_no', 'material', 'misc', 'weight',
            'jewelry_price', 'material_price', 'total_weight',
            'gemstone_weight', 'material_weight'
        ]
        result_df = result_df[output_columns]

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
    print(f"✅ Starting Flask on port {port}")
    app.run(debug=True, host="0.0.0.0", port=port)