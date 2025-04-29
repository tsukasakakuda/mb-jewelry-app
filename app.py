from flask import Flask, request, render_template, send_file, session
import pandas as pd
import io
import re
import tempfile
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

def check_invalid_weights(item_data):
    invalid_rows = []
    for idx, row in item_data.iterrows():
        weight_value = row.get('weight', '')
        if pd.notna(weight_value) and weight_value.strip():
            try:
                cleaned_weight = re.sub(r'[^0-9.]', '', weight_value.split('g')[0])
                float(cleaned_weight)
            except ValueError:
                invalid_rows.append({
                    'index': idx,
                    'weight': weight_value,
                    'row_data': row.to_dict()
                })
    return invalid_rows

def calculate_items(item_data, price_data):
    price_dict = dict(zip(price_data['material'].str.lower(), price_data['price']))

    def calculate_material_value(row):
        total_weight = float(re.sub(r'[^0-9.]', '', str(row['weight']).split('g')[0])) if pd.notna(row['weight']) and str(row['weight']).strip() else 0.0
        gemstone_weight = 0.0
        material_price = 0.0
        parts = str(row['misc']).split() if pd.notna(row['misc']) and str(row['misc']).strip() else []
        material_name = str(row['material']).strip().lower() if pd.notna(row['material']) and str(row['material']).strip() else None

        if material_name and material_name in price_dict:
            for part in parts:
                if any(x in part for x in ['#', 'cm', '%']):
                    continue
                number_match = re.findall(r'(\d+(?:\.\d+)?)', part)
                if number_match:
                    num = float(number_match[0])
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

    item_data[['jewelry_price', 'material_price', 'total_weight', 'gemstone_weight', 'material_weight']] = item_data.apply(calculate_material_value, axis=1)

    output = io.BytesIO()
    item_data.to_csv(output, index=False)
    output.seek(0)
    return output

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        item_file = request.files['item_file']
        price_file = request.files['price_file']

        tmp_price_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        price_file.save(tmp_price_file.name)
        session['price_file_path'] = tmp_price_file.name

        item_data = pd.read_csv(item_file)
        price_data = pd.read_csv(tmp_price_file.name)

        # 初回に元データを保存
        session['original_item_data'] = item_data.to_dict(orient='records')

        invalid_weights = check_invalid_weights(item_data)
        if invalid_weights:
            return render_template('invalid_weights.html', invalid_data=invalid_weights)

        result = calculate_items(item_data, price_data)
        return send_file(result, as_attachment=True, download_name='calculated_items.csv', mimetype='text/csv')

    return render_template('index.html')

@app.route('/fix_weights', methods=['POST'])
def fix_weights():
    original_data = session.get('original_item_data', [])
    if not original_data:
        return "元のデータが見つかりません", 400

    df = pd.DataFrame(original_data)

    # 💡 フォームの情報で全カラムを更新（型も考慮して！）
    for idx in df.index:
        # box_id, box_noは数字ならintに変換
        box_id = request.form.get(f'box_id_{idx}', df.at[idx, 'box_id'])
        box_no = request.form.get(f'box_no_{idx}', df.at[idx, 'box_no'])
        
        try:
            box_id = int(box_id)
        except (ValueError, TypeError):
            pass  # 変換できなければそのまま

        try:
            box_no = int(box_no)
        except (ValueError, TypeError):
            pass  # 変換できなければそのまま

        df.at[idx, 'box_id'] = box_id
        df.at[idx, 'box_no'] = box_no
        df.at[idx, 'material'] = request.form.get(f'material_{idx}', df.at[idx, 'material'])
        df.at[idx, 'misc'] = request.form.get(f'misc_{idx}', df.at[idx, 'misc'])
        df.at[idx, 'weight'] = request.form.get(f'weight_{idx}', df.at[idx, 'weight'])

    session['original_item_data'] = df.to_dict(orient='records')

    # 再チェック
    invalid_weights = check_invalid_weights(df)
    if invalid_weights:
        return render_template('invalid_weights.html', invalid_data=invalid_weights)

    # 問題なければ計算
    price_file_path = session.get('price_file_path')
    if not price_file_path or not os.path.exists(price_file_path):
        return "価格データが見つかりません", 400

    price_data = pd.read_csv(price_file_path)
    result = calculate_items(df, price_data)

    return send_file(result, as_attachment=True, download_name='calculated_all_items.csv', mimetype='text/csv')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)