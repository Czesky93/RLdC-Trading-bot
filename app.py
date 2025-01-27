
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'secretkey123'

# Placeholder for user database
users = {"admin": "password"}  # Example user

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            return redirect(url_for('login'))
        return "User already exists"
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/binance/disconnect', methods=['POST'])
def disconnect_binance():
    # Placeholder for disconnecting Binance
    return jsonify({"status": "success", "message": "Binance disconnected successfully"})

@app.route('/account/settings', methods=['GET', 'POST'])
def account_settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        users[session['user']] = new_password
        return jsonify({"status": "success", "message": "Password updated successfully"})
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)
