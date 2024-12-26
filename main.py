from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import hashlib
import requests


# Database Manager for handling SQLite operations
class DatabaseManager:
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect('lockzilla.db', timeout=10)  # Timeout to prevent immediate lock errors
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode = WAL')  # Enable Write-Ahead Logging (WAL) for concurrency
        return conn

    @staticmethod
    def get_user_by_username(username):
        with DatabaseManager.get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        return user

    @staticmethod
    def insert_user(username, password, email):
        with DatabaseManager.get_db_connection() as conn:
            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                         (username, generate_password_hash(password), email))
            conn.commit()

    @staticmethod
    def validate_user(username, password):
        user = DatabaseManager.get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    @staticmethod
    def get_passwords(user_id):
        with DatabaseManager.get_db_connection() as conn:
            passwords = conn.execute('SELECT * FROM passwords WHERE user_id = ?', (user_id,)).fetchall()
        return passwords

    @staticmethod
    def get_filtered_passwords(user_id, search_term):
        with DatabaseManager.get_db_connection() as conn:
            passwords = conn.execute('SELECT * FROM passwords WHERE user_id = ? AND service LIKE ?',
                                     (user_id, f'%{search_term}%')).fetchall()
        return passwords

    @staticmethod
    def insert_password(user_id, service, password):
        with DatabaseManager.get_db_connection() as conn:
            conn.execute('INSERT INTO passwords (user_id, service, password) VALUES (?, ?, ?)',
                         (user_id, service, password))
            conn.commit()

    @staticmethod
    def update_password(user_id, service, password):
        with DatabaseManager.get_db_connection() as conn:
            conn.execute('UPDATE passwords SET password = ? WHERE user_id = ? AND service = ?',
                         (password, user_id, service))
            conn.commit()

    @staticmethod
    def delete_password(user_id, service):
        with DatabaseManager.get_db_connection() as conn:
            conn.execute('DELETE FROM passwords WHERE user_id = ? AND service = ?',
                         (user_id, service))
            conn.commit()


# Flask app to handle routes and logic
class AppRoutes:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'your_secret_key'  # Secret key for session management
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/logout', 'logout', self.logout)
        self.app.add_url_rule('/add', 'add_password', self.add_password, methods=['GET', 'POST'])
        self.app.add_url_rule('/update/<service>', 'update_password', self.update_password, methods=['GET', 'POST'])
        self.app.add_url_rule('/delete/<service>', 'delete_password', self.delete_password, methods=['POST'])
        self.app.add_url_rule('/register', 'register', self.register, methods=['GET', 'POST'])
        self.app.add_url_rule('/get_password', 'get_password', self.get_password, methods=['GET'])

    def check_password_breach(self, password):
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url)

        if response.status_code == 200:
            hashes = response.text.splitlines()
            for hash_entry in hashes:
                hash_suffix, count = hash_entry.split(':')
                if hash_suffix == suffix:
                    print(f"Password has been exposed {count} times in data breaches.")
                    return True
            
            return False
        else:
            print("Error querying the API.")
            return False

    def index(self):
        if 'username' not in session:
            return redirect(url_for('login'))
        user_id = session['user_id']

        search_term = request.args.get('search', '')  # Get search term from query string
        if search_term:
            passwords = DatabaseManager.get_filtered_passwords(user_id, search_term)
        else:
            passwords = DatabaseManager.get_passwords(user_id)

        return render_template('index.html', passwords=passwords, username=session['username'], search_term=search_term)

    def login(self):
        if 'username' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = DatabaseManager.validate_user(username, password)
            if user:
                session['username'] = username
                session['user_id'] = user['id']
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'danger')

        return render_template('login.html')

    def logout(self):
        session.clear()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('login'))

    def register(self):
        if 'username' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            email = request.form['email']

            if password != confirm_password:
                flash('Passwords do not match, please try again.', 'danger')
                return redirect(url_for('register'))

            if DatabaseManager.get_user_by_username(username):
                flash('Username already exists.', 'danger')
                return redirect(url_for('register'))

            DatabaseManager.insert_user(username, password, email)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    def add_password(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            service = request.form['service_name']
            password = request.form['password']
            user_id = session['user_id']
            self.check_password_breach(password)

            DatabaseManager.insert_password(user_id, service, password)
            flash(f'Password for {service} added successfully!', 'success')
            return redirect(url_for('index'))

        return render_template('add_password.html')

    def update_password(self, service):
        if 'username' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        existing_password = DatabaseManager.get_passwords(user_id)
        service_password = next((pw for pw in existing_password if pw['service'] == service), None)

        if request.method == 'POST':
            password = request.form['password']
            DatabaseManager.update_password(user_id, service, password)
            flash(f'Password for {service} updated successfully!', 'success')
            return redirect(url_for('index'))

        return render_template('update_password.html', service_password=service_password)

    def delete_password(self, service):
        if 'username' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        DatabaseManager.delete_password(user_id, service)
        flash(f'Password for {service} deleted successfully!', 'success')
        return redirect(url_for('index'))

    # API endpoint for retrieving stored password for autofill
    def get_password(self):
        if 'username' not in session:
            return jsonify({"error": "User not logged in"}), 401

        user_id = session['user_id']
        domain = request.args.get('domain')

        if not domain:
            return jsonify({"error": "Domain parameter missing"}), 400

        with DatabaseManager.get_db_connection() as conn:
            passwords = conn.execute('SELECT * FROM passwords WHERE user_id = ? AND service LIKE ?',
                                     (user_id, f'%{domain}%')).fetchall()

        if passwords:
            password_data = []
            for password in passwords:
                password_data.append({
                    "service": password['service'],
                    "password": password['password']
                })
            return jsonify(password_data)
        else:
            return jsonify({"error": "No passwords found for this domain"}), 404

    def run(self):
        self.app.run(debug=True)


# Run the app
if __name__ == '__main__':
    app = AppRoutes()
    app.run()
