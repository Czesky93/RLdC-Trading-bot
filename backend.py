
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/settings", methods=["POST"])
def settings():
    api_key = request.form.get("apiKey")
    secret_key = request.form.get("secretKey")
    with open("user_settings.txt", "w") as file:
        file.write(f"API Key: {api_key}\nSecret Key: {secret_key}")
    return "Ustawienia zapisane pomyślnie!"

if __name__ == "__main__":
    app.run(debug=True)
    