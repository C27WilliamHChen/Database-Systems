from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL connection configuration
db_config = {
    'host': '172.31.160.1',
    'port': '3306',
    'user': 'root',
    'password': 'F-15Eagle@WC',
    'database': 'database'
}

# Home page with form
@app.route('/')
def index():
    return render_template('index.html')

# Handle form submission
@app.route('/add_user', methods=['POST'])
def add_user():
    user_id = request.form.get('id')
    name = request.form.get('name')

    if not user_id or not name:
        return "Missing id or name", 400

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id, name) VALUES (%s, %s)", (user_id, name))
        conn.commit()
        return redirect(url_for('index'))
    except Error as e:
        return f"Database error: {e}", 500
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
