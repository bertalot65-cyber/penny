import os
from flask import Flask, jsonify, request
from x402.http import HTTPFacilitatorClientSync, FacilitatorConfig, PaymentOption
from x402.http.middleware.flask import payment_middleware
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServerSync

app = Flask(__name__)

WALLET = os.getenv("EVM_WALLET", "")
NETWORK = os.getenv("NETWORK", "eip155:84532")
PRICE_USD = os.getenv("PRICE_USD", "0.001")
FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")

if not WALLET:
    raise RuntimeError("EVM_WALLET is required")

facilitator = HTTPFacilitatorClientSync(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServerSync(facilitator)
server.register(NETWORK, ExactEvmServerScheme())

price = PRICE_USD if PRICE_USD.startswith("$") else f"${PRICE_USD}"
routes = {
    "GET /normalize": RouteConfig(
        accepts=[PaymentOption(scheme="exact", pay_to=WALLET, price=price, network=NETWORK)],
        mime_type="application/json",
        description="Normalize text by trimming whitespace and converting to lowercase",
    ),
    "GET /estimate": RouteConfig(
        accepts=[PaymentOption(scheme="exact", pay_to=WALLET, price=price, network=NETWORK)],
        mime_type="application/json",
        description="Calculate a labor estimate from hours and hourly rate",
    ),
}
payment_middleware(app, routes=routes, server=server)

@app.get("/")
def home():
    return jsonify({
        "service": "Penny API",
        "status": "online",
        "network": NETWORK,
        "price_usd": PRICE_USD,
        "payment_mode": "x402 testnet" if NETWORK == "eip155:84532" else "x402",
        "paid_endpoints": ["/normalize?text=hello", "/estimate?hours=8&rate=125"],
        "free_endpoints": ["/", "/health"]
    })

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "penny-api", "payments": "x402"})

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
