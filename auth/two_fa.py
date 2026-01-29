import pyotp
from flask import request, jsonify

def generate_2fa():
    secret = pyotp.random_base32()
    return jsonify({"secret": secret, "qr_code_url": f"otpauth://totp/RLdC-Trading-Bot?secret={secret}"})

def verify_2fa():
    data = request.json or {}
    secret = data.get("secret")
    token = data.get("token")
    if not secret or not token:
        return jsonify({"error": "Missing secret or token"}), 400
    totp = pyotp.TOTP(secret)
    if totp.verify(token):
        return jsonify({"message": "2FA verification successful"})
    return jsonify({"error": "Invalid 2FA token"}), 400
