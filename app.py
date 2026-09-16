import os
from flask import Flask, jsonify, request

app = Flask(__name__)

WALLET = os.getenv("EVM_WALLET", "")
NETWORK = os.getenv("NETWORK", "eip155:84532")
PRICE_USD = os.getenv("PRICE_USD", "0.001")

@app.get("/")
def home():
    return jsonify({
        "service": "Penny API",
        "status": "online",
        "network": NETWORK,
        "price_usd": PRICE_USD,
        "payment_mode": "testnet configuration",
        "endpoints": ["/health", "/normalize?text=hello", "/estimate?hours=8&rate=125"]
    })

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "penny-api"})

@app.get("/normalize")
def normalize():
    text = request.args.get("text", "")
    return jsonify({"input": text, "normalized": " ".join(text.strip().lower().split())})

@app.get("/estimate")
def estimate():
    try:
        hours = float(request.args.get("hours", "0"))
        rate = float(request.args.get("rate", "0"))
    except ValueError:
        return jsonify({"error": "hours and rate must be numbers"}), 400
    return jsonify({"hours": hours, "rate": rate, "total": round(hours * rate, 2)})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
