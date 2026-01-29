from flask import Flask, request, session, jsonify

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Zmień na bezpieczny klucz sesji

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")  # Można dodać weryfikację

    # Sprawdzenie poprawności użytkownika (np. w bazie danych)
    if username == "admin" and password == "password":  # Przykład
        session["user"] = username
        return jsonify({"message": "Zalogowano pomyślnie"})
    
    return jsonify({"error": "Nieprawidłowe dane logowania"}), 401

@app.route("/set_api_keys", methods=["POST"])
def set_api_keys():
    if "user" not in session:
        return jsonify({"error": "Brak sesji użytkownika"}), 403
    
    api_key = request.form.get("api_key")
    api_secret = request.form.get("api_secret")

    # Zapisujemy klucze w sesji (lub w bazie danych)
    session["api_key"] = api_key
    session["api_secret"] = api_secret
    
    return jsonify({"message": "Klucze API zostały zapisane"})

@app.route("/some_protected_route", methods=["GET"])
def some_protected_route():
    if "api_key" not in session or "api_secret" not in session:
        return jsonify({"error": "Brak kluczy API"}), 403
    
    api_key = session["api_key"]
    api_secret = session["api_secret"]
    
    return jsonify({"message": "Endpoint działa poprawnie z kluczami API"})
