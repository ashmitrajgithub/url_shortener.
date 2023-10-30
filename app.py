from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string

app = Flask(__name__)

# Set up the database
def initialize_database():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS url_map (id INTEGER PRIMARY KEY, original_url TEXT, short_url TEXT)")
    conn.commit()
    conn.close()

# Generate a random short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    original_url = request.form["original_url"]

    # Ensure the URL has the appropriate prefix
    if not (original_url.startswith("http://") or original_url.startswith("https://")):
        original_url = "http://" + original_url

    # Database connection
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    # Check if the URL is already in the database
    cursor.execute("SELECT short_url FROM url_map WHERE original_url = ?", (original_url,))
    row = cursor.fetchone()

    if row:
        short_url = row[0]
    else:
        short_url = generate_short_url()
        cursor.execute("INSERT INTO url_map (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
        conn.commit()

    conn.close()

    return render_template("shortened.html", original_url=original_url, short_url=short_url)

@app.route("/<short_url>")
def redirect_to_original(short_url):
    # Database connection
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    # Retrieve the original URL from the database
    cursor.execute("SELECT original_url FROM url_map WHERE short_url = ?", (short_url,))
    row = cursor.fetchone()
    conn.close()

    if row:
        original_url = row[0]
        return redirect(original_url)
    else:
        return "URL not found"

if __name__ == "__main__":
    initialize_database()
    app.run()
