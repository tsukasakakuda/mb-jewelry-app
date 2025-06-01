from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
import numpy as np
import pandas as pd
import re
import io
import os
import json

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)

@app.route('/edit-csv', methods=['POST'])
def edit_csv():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'CSVファイルが必要です'}), 400

        df = pd.read_csv(file)

        # カラム結合（NaN対応）: "misc + weight" → "詳細情報"
        #['misc', 'weight', 'jewelry_carat', 'jewelry_color', 'jewelry_clarity', 'jewelry_cutting', 'jewelry_shape', 'jewelry_polish', 'jewelry_symmetry', 'jewelry_3ex', 'jewelry_h_c', 'jewelry_fluorescence']
        df['feature'] = df[['misc', 'weight', 'jewelry_carat', 'jewelry_color', 'jewelry_clarity', 'jewelry_cutting', 'jewelry_shape', 'jewelry_polish', 'jewelry_symmetry', 'jewelry_fluorescence']].fillna('').astype(str).agg(' '.join, axis=1).str.strip()


        # 残したいカラムと対応する日本語ラベル
        column_map = {
            'end_date': '大会日',
            'box_id': '箱番',
            'box_no': '枝番',
            'subcategory_name': '品目',
            'brand_name': 'ブランド',
            'material': '素材',
            'feature': '備考',
            'accessory_comment': '付属品'
        }

        # 必要なカラムだけを抽出
        needed_columns = [col for col in column_map.keys() if col in df.columns]
        df = df[needed_columns]

        # カラム名を日本語に変換
        df = df.rename(columns=column_map)

        # CSVをバイトストリームにして返す
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename_edt = f"edited_result_{timestamp}.csv"

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename_edt
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- エイリアスマップ読み込み ---
def load_material_aliases(json_path="material_price_map.json"):
    with open(json_path, encoding='utf-8') as f:
        raw = json.load(f)
    alias_to_main = {}
    for main, aliases in raw.items():
        for alias in aliases:
            alias_to_main[alias.lower()] = main.lower()
    return alias_to_main

material_aliases = load_material_aliases()

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
    # --- 金額辞書を作る（素材名はエイリアス含む） ---
    price_df['price'] = pd.to_numeric(price_df['price'], errors='coerce').fillna(0)
    price_dict_raw = dict(zip(price_df['material'].str.lower(), price_df['price']))

    # エイリアス展開
    price_dict = {}
    for alias, main in material_aliases.items():
        if main in price_dict_raw:
            price_dict[alias] = price_dict_raw[main]

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
        material_field = str(row['material']).strip().lower() if pd.notna(row['material']) else ""

        # 複数素材を処理（例: "pt900/k18"）
        if "/" in material_field:
            sub_materials = material_field.split("/")
            prices = [price_dict.get(m.strip()) for m in sub_materials]
            valid_prices = [p for p in prices if p is not None]
            material_price = np.mean(valid_prices) if len(valid_prices) == len(sub_materials) else 0
        else:
            material_price = price_dict.get(material_field, 0)

        # 宝石重量推定
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

        material_weight = total_weight - gemstone_weight
        material_value = material_weight * material_price

        return pd.Series([
            material_value, material_price, total_weight,
            gemstone_weight, material_weight
        ])

    item_df[['jewelry_price', 'material_price', 'total_weight', 'gemstone_weight', 'material_weight']] = item_df.apply(calculate, axis=1)
    return item_df

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
        result_df = result_df.sort_values(by=['box_id', 'box_no'])

        # ✅ 出力対象のカラムだけに制限
        output_columns = [
            'box_id', 'box_no', 'material', 'misc', 'weight',
            'jewelry_price', 'material_price', 'total_weight',
            'gemstone_weight', 'material_weight'
        ]
        result_df = result_df[[col for col in output_columns if col in result_df.columns]]

        output = io.StringIO()
        result_df.to_csv(output, index=False)
        output.seek(0)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename_cal = f"calculated_result_{timestamp}.csv"

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename_cal
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_vue():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"✅ Starting Flask on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)