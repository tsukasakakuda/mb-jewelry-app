from flask import Flask, request, render_template, send_file
import pandas as pd
import io
import re

app = Flask(__name__)

def calculate_items(item_file, price_file):
    item_data = pd.read_csv(item_file)
    price_data = pd.read_csv(price_file)

    price_dict = dict(zip(price_data['material'].str.lower(), price_data['price']))

    def calculate_material_value(row):
        total_weight = float(re.sub(r'[^0-9.]', '', row['weight'].split('g')[0])) if pd.notna(row['weight']) and row['weight'].strip() else 0.0
        gemstone_weight = 0.0
        material_price = 0.0
        parts = row['misc'].split() if pd.notna(row['misc']) and row['misc'].strip() else []
        material_name = row['material'].strip().lower() if pd.notna(row['material']) and row['material'].strip() else None

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
        result = calculate_items(item_file, price_file)
        return send_file(result, as_attachment=True, download_name='calculated_items.csv', mimetype='text/csv')
    return render_template('index.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)