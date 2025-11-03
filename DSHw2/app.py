from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error, pooling
import os

app = Flask(__name__)
app.secret_key = "change-me"  # replace with something long & random for production

# --- MySQL connection config ---
# If your MySQL is on Windows and your Flask runs in WSL/Ubuntu, 172.31.160.1 is common.
# If everything is local on one OS, use "127.0.0.1".
DB_CONFIG = {
    "host": "172.31.160.1",      # change to 127.0.0.1 if needed
    "port": 3306,
    "user": "root",
    "password": "F-15Eagle@WC",   # consider changing after testing
    "database": "database"
}

# Connection pool (more robust than opening/closing ad hoc connections)
cnxpool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    pool_reset_session=True,
    **DB_CONFIG
)

def get_conn():
    return cnxpool.get_connection()

def init_db():
    """Create database/table if they don't exist."""
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id   INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
                )
            """)
            conn.commit()
            print("[init_db] users table is ready.")
    except Error as e:
        print(f"[init_db] Database error: {e}")

@app.route("/", methods=["GET"])
def index():
    """Show form + current users."""
    users = []
    try:
        with get_conn() as conn, conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, name FROM users ORDER BY id")
            users = cur.fetchall()
    except Error as e:
        flash(f"Database read error: {e}", "error")
    return render_template("index.html", users=users)

@app.route("/add_user", methods=["POST"])
def add_user():
    """Insert a new user (name only; id auto-increments)."""
    name = (request.form.get("name") or "").strip()
    if not name:
        return "Missing name", 400
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO users (name) VALUES (%s)", (name,))
            conn.commit()
        flash("User added!", "success")
    except Error as e:
        return f"Database error: {e}", 500
    return redirect(url_for("index"))

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    """Delete a user by ID."""
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
        flash("User deleted.", "success")
    except Error as e:
        return f"Database error: {e}", 500
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    # host="0.0.0.0" lets you reach it from outside the machine if needed.
    app.run(debug=True, host="0.0.0.0", port=5000)