from flask import Flask, jsonify, request, send_from_directory
import requests
import json
import os

app = Flask(__name__, static_folder='static')

# Load product data from JSON file (ensure products.json is in the correct location)
try:
    with open('products.json', 'r') as f:
        products = json.load(f)
except FileNotFoundError:
    products = []
    print("Warning: products.json not found!")

# Fetch real-time gold price (replace with actual API)
def get_gold_price():
    api_key = "goldapi-3euodsm4qx8b7p-io"
    symbol = "XAU"
    curr = "USD"
    date = ""  # You can modify this if you need a specific date

    url = f"https://www.goldapi.io/api/{symbol}/{curr}{date}"
    
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an error if the status code is not 200

        # Parse the response JSON to extract the price
        data = response.json()
        gold_price = data.get('price', 50)  # Default to $50 if the 'price' key is not found
        
        return gold_price
    except requests.exceptions.RequestException as e:
        print("Error:", str(e))
    
    return 50  # Return the fallback price if any error occurs

@app.route('/products', methods=['GET'])
def get_products():
    gold_price = get_gold_price()
    updated_products = []

    for product in products:
        price = (product['popularityScore'] + 1) * product['weight'] * gold_price
        updated_product = {
            **product,
            'price': round(price, 2),
            'popularityScoreFormatted': round(product['popularityScore'] * 5, 1)  # Convert to 5-point scale
        }
        updated_products.append(updated_product)

    # Filtering logic
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_popularity = request.args.get('min_popularity', type=float)
    max_popularity = request.args.get('max_popularity', type=float)

    if min_price is not None:
        updated_products = [p for p in updated_products if p['price'] >= min_price]
    if max_price is not None:
        updated_products = [p for p in updated_products if p['price'] <= max_price]
    if min_popularity is not None:
        updated_products = [p for p in updated_products if p['popularityScoreFormatted'] >= min_popularity]
    if max_popularity is not None:
        updated_products = [p for p in updated_products if p['popularityScoreFormatted'] <= max_popularity]

    return jsonify(updated_products)

@app.route('/', methods=['GET'])
def serve_frontend():
    # Ensure index.html is located in the static folder
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static_files(path):
    # Serve any static files like images, JS, or CSS located in the static folder
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)
