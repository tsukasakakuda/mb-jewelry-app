from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import re
import io
import os
import json
import pymysql
from dotenv import load_dotenv

# --- 初期設定 ---
load_dotenv(dotenv_path='.env.development')
app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)

# --- DB接続 ---
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

# --- マテリアルマップ読み込み ---
def load_material_aliases(json_path="material_price_map.json"):
    with open(json_path, encoding='utf-8') as f:
        raw = json.load(f)
    alias_to_main = {}
    for main, aliases in raw.items():
        for alias in aliases:
            alias_to_main[alias.lower()] = main.lower()
    return alias_to_main

material_aliases = load_material_aliases()

# --- 必須カラム補完 ---
def ensure_required_columns(df, required_columns):
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    return df

# --- アイテム計算 ---
def calculate_items(item_df, price_df):
    price_df['price'] = pd.to_numeric(price_df['price'], errors='coerce').fillna(0)
    price_dict_raw = dict(zip(price_df['material'].str.lower(), price_df['price']))

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

        if "/" in material_field:
            sub_materials = material_field.split("/")
            prices = [price_dict.get(m.strip()) for m in sub_materials]
            valid_prices = [p for p in prices if p is not None]
            material_price = np.mean(valid_prices) if len(valid_prices) == len(sub_materials) else 0
        else:
            material_price = price_dict.get(material_field, 0)

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
        jewelry_price = material_weight * material_price

        return pd.Series([
            jewelry_price,
            material_price, total_weight,
            gemstone_weight, material_weight
        ])

    item_df[['jewelry_price', 'material_price', 'total_weight', 'gemstone_weight', 'material_weight']] = item_df.apply(calculate, axis=1)
    return item_df

# --- DB登録 ---
def insert_items_to_db(df):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            for _, row in df.iterrows():
                sql = """
                    INSERT INTO items (box_id, box_no, material, misc, weight,
                        jewelry_price, material_price, total_weight,
                        gemstone_weight, material_weight)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    row.get('box_id'), row.get('box_no'), row.get('material'),
                    row.get('misc'), row.get('weight'), row.get('jewelry_price'),
                    row.get('material_price'), row.get('total_weight'),
                    row.get('gemstone_weight'), row.get('material_weight')
                ))
        connection.commit()
    finally:
        connection.close()

# --- エンドポイント ---
@app.route("/items", methods=["GET"])
def get_items():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM items ORDER BY id DESC")
            return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO items (box_no, weight, jewelry_price)
                VALUES (%s, %s, %s)
            """, (data.get("box_no"), data.get("weight"), data.get("jewelry_price")))
            connection.commit()
        return jsonify({"message": "登録成功"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route("/upload-items", methods=["POST"])
def upload_items():
    try:
        item_file = request.files['item_csv']
        price_file = request.files['price_csv']

        item_df = pd.read_csv(item_file)
        price_df = pd.read_csv(price_file)

        # 必要なカラムだけに制限（余分なカラムは無視）
        required_item_columns = ['box_id', 'box_no', 'material', 'misc', 'weight', 'jewelry_price']
        item_df = ensure_required_columns(item_df, required_item_columns)
        item_df = item_df[required_item_columns]

        required_price_columns = ['material', 'price']
        price_df = ensure_required_columns(price_df, required_price_columns)
        price_df = price_df[required_price_columns]

        result_df = calculate_items(item_df, price_df)

        # NaN を None に置き換え（MySQLに渡すため）
        result_df = result_df.where(pd.notnull(result_df), None)

        insert_items_to_db(result_df)

        return jsonify({"message": "登録成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/check-weights", methods=["POST"])
def check_weights():
    try:
        file = request.files.get('item_file')
        if not file:
            return jsonify({'error': 'item_file is required'}), 400

        df = pd.read_csv(file)
        df = ensure_required_columns(df, ['box_id', 'box_no', 'material', 'misc', 'weight'])

        invalids = []
        for idx, row in df.iterrows():
            val = str(row.get('weight', '')).strip()
            if val:
                try:
                    cleaned = re.sub(r'[^0-9.]', '', val.split('g')[0])
                    float(cleaned)
                except Exception:
                    clean_row = {k: ("" if pd.isna(v) else v) for k, v in row.to_dict().items()}
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

@app.route("/edit-csv", methods=["POST"])
def edit_csv():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'CSVファイルが必要です'}), 400

        df = pd.read_csv(file)
        df['feature'] = df[['misc', 'weight', 'jewelry_carat', 'jewelry_color', 'jewelry_clarity',
                            'jewelry_cutting', 'jewelry_shape', 'jewelry_polish',
                            'jewelry_symmetry', 'jewelry_fluorescence']].fillna('').astype(str).agg(' '.join, axis=1).str.strip()

        column_map = {
            'end_date': '大会日', 'box_id': '箱番', 'box_no': '枝番',
            'subcategory_name': '品目', 'brand_name': 'ブランド',
            'material': '素材', 'feature': '備考', 'accessory_comment': '付属品'
        }

        df = df[[col for col in column_map.keys() if col in df.columns]]
        df = df.rename(columns=column_map)

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        filename = f"edited_result_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')), mimetype='text/csv', as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/calculate-fixed", methods=["POST"])
def calculate_fixed():
    try:
        data = request.json
        item_df = pd.DataFrame(data.get('item_data', []))
        price_df = pd.DataFrame(data.get('price_data', []))

        item_df = ensure_required_columns(item_df, ['box_id', 'box_no', 'material', 'misc', 'weight'])
        price_df = ensure_required_columns(price_df, ['material', 'price'])

        result_df = calculate_items(item_df, price_df)
        result_df['box_no'] = pd.to_numeric(result_df['box_no'], errors='coerce').fillna(0).astype(int)
        result_df['box_id'] = pd.to_numeric(result_df['box_id'], errors='coerce').fillna(0).astype(int)
        result_df = result_df.sort_values(by=['box_id', 'box_no'])

        output = io.StringIO()
        output_columns = [
            'box_id', 'box_no', 'material', 'misc', 'weight',
            'jewelry_price', 'material_price', 'total_weight',
            'gemstone_weight', 'material_weight'
        ]
        result_df = result_df[[col for col in output_columns if col in result_df.columns]]
        result_df.to_csv(output, index=False)
        output.seek(0)

        filename = f"calculated_result_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')),
                         mimetype='text/csv', as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_vue():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "8080"))
    print(f"✅ Starting Flask on port {port}")
    app.run(debug=True, host="0.0.0.0", port=port)