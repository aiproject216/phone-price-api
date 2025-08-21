from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

API_KEY = "b62c6f0ffe60c1a77c068424f772233211c8e73876e99fbd4c6fe9c2c4a57563"

# List of valid phone brands to filter queries
VALID_PHONE_BRANDS = [
    "iPhone", "Samsung", "OnePlus", "Google Pixel", "Xiaomi", "Redmi",
    "Oppo", "Vivo", "Realme", "Motorola", "Nothing", "Asus",
    "Sony Xperia", "Poco"
]

def is_phone_model(query):
    """Check if the query matches known phone brands or contains 'phone'."""
    return any(brand.lower() in query.lower() for brand in VALID_PHONE_BRANDS) or "phone" in query.lower()

def get_price_using_api(phone_model):
    """Fetch phone prices from SerpAPI"""
    params = {
        "engine": "google_shopping",
        "q": phone_model,
        "hl": "en",
        "gl": "in",
        "location": "India",
        "api_key": API_KEY
    }

    response = requests.get("https://serpapi.com/search", params=params)

    if response.status_code == 200:
        data = response.json()
        products = []

        if "shopping_results" in data:
            for result in data["shopping_results"]:
                price = result.get("price", "Not Available")
                image = result.get("thumbnail", "https://via.placeholder.com/150")
                link = result.get("product_link") or result.get("link", "#")
                store = result.get("source", "Unknown Store")

                products.append({
                    "price": price,
                    "image": image,
                    "link": link,
                    "store": store
                })

        return products if products else []

    return []

@app.route('/get_price', methods=['GET'])
def get_price():
    phone_model = request.args.get('model', '').strip()

    if not phone_model:
        return jsonify({"error": "No phone model provided", "products": []})

    # Check if it's a phone model or not
    if not is_phone_model(phone_model):
        return jsonify({"error": "Only phone models are supported!", "products": []})

    # Log the endpoint URL
    print(f"API called: http://127.0.0.1:5000/get_price?model={quote(phone_model)}")

    products = get_price_using_api(phone_model)
    if not products:
        return jsonify({"error": "No Prices Found", "products": []})

    return jsonify({"error": None, "products": products})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
