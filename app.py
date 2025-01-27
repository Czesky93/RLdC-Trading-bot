
from flask import Flask, render_template_string
import importlib
import os

app = Flask(__name__)

MODULES_DIR = 'modules'

def load_module(module_name):
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError as e:
        print(f"Error loading module {module_name}: {e}")
        return None

def discover_modules():
    return [d for d in os.listdir(MODULES_DIR) if os.path.isdir(os.path.join(MODULES_DIR, d))]

@app.route('/')
def home():
    # Dynamiczne generowanie strony głównej
    modules = discover_modules()
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Modular Bot</title>
    </head>
    <body>
        <h1>Welcome to Modular Bot</h1>
        <h2>Available Modules:</h2>
        <ul>
        {% for module in modules %}
            <li>{{ module }}</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    '''
    return render_template_string(html, modules=modules)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
