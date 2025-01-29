from flask import Flask, request, jsonify, render_template
import os
import subprocess
import config

app = Flask(__name__)

@app.route("/admin", methods=["GET"])
def admin_panel():
    return render_template("admin.html")

@app.route("/admin/restart", methods=["POST"])
def restart_app():
    try:
        subprocess.Popen(["pkill", "-f", "app.py"])
        return jsonify({"status": "success", "message": "Aplikacja zostanie zrestartowana"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/admin/update_config", methods=["POST"])
def update_config():
    try:
        new_config = request.json
        with open("backend/config.py", "w") as f:
            for key, value in new_config.items():
                f.write(f'{key.upper()} = "{value}"\n')
        return jsonify({"status": "success", "message": "Konfiguracja zaktualizowana"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/admin/logs", methods=["GET"])
def get_logs():
    try:
        with open("log.txt", "r") as log_file:
            logs = log_file.read()
        return jsonify({"status": "success", "logs": logs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
