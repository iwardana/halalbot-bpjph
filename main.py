from flask_cors import CORS
from model import chatbot_response
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Membuat database SQLite dan tabel pengguna
conn = sqlite3.connect('users.db')

# Baca dataset dari file JSON
with open('dataset.json', 'r') as file:
    dataset = json.load(file)

# Hubungkan ke database SQLite3
connection = sqlite3.connect('chatbot.db')
cursor = connection.cursor()

# Buat tabel jika belum ada
cursor.execute('''
    CREATE TABLE IF NOT EXISTS intent_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        intent_name TEXT,
        tags TEXT,
        patterns TEXT,
        responses TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        question TEXT,
        response TEXT
    )
''')


# Masukkan data ke dalam tabel
for intent_data in dataset.get('intents', []):
    intent_name = intent_data.get('intent_name', '')
    tags = ', '.join(intent_data.get('tags', []))
    patterns = ', '.join(intent_data.get('patterns', []))
    responses = ', '.join(intent_data.get('responses', []))

    cursor.execute("INSERT INTO intent_data (intent_name, tags, patterns, responses) VALUES (?, ?, ?, ?)",
                   (intent_name, tags, patterns, responses))

# Commit perubahan dan tutup koneksi
connection.commit()
connection.close()


@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        # Ambil data dari formulir
        tag = request.form.get('tag')
        patterns = request.form.get('patterns')
        responses = request.form.get('responses')

        # Hubungkan ke database SQLite3
        connection = sqlite3.connect('chatbot.db')
        cursor = connection.cursor()

        # Masukkan data ke dalam tabel
        cursor.execute("INSERT INTO intent_data (tags, patterns, responses) VALUES (?, ?, ?)",
                       (tag, patterns, responses))

        # Commit perubahan dan tutup koneksi
        connection.commit()
        connection.close()

        return redirect(url_for('edit'))  # Redirect ke halaman edit setelah berhasil

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def root():
    if 'username' in session:
        return redirect(url_for('base'))
    else:
        return redirect(url_for('login'))

@app.route('/base')
def base():
    if 'username' in session:
        return render_template('base.html')
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)

        # Lakukan sesuatu dengan peran pengguna (secara otomatis setel ke "pengguna_biasa")
        role = "pengguna_biasa"

        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", (username, email, hashed_password, role))
        conn.commit()
        session['username'] = username  # Tambahkan nama pengguna ke sesi setelah sign-up

        conn.close()
        return jsonify({'success': True, 'message': 'Registrasi berhasil! Silakan login.'})


    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['username'] = user[0]  # Tambahkan nama pengguna ke sesi setelah login
            return jsonify({'success': True, 'message': 'Login berhasil!'})
        else:
            return jsonify({'success': False, 'message': 'Login gagal. Email atau password salah.'})

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)  # Hapus sesi nama pengguna
    return redirect(url_for('login'))


@app.route('/layanan')
def layanan():
    if 'username' in session:
        return render_template('layanan.html')
    else:
        return redirect(url_for('login'))

@app.route('/informasi')
def informasi():
    if 'username' in session:
        return render_template('informasi.html')
    else:
        return redirect(url_for('login'))

@app.route('/regulasi')
def regulasi():
    if 'username' in session:
        return render_template('regulasi.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/edit', methods=['GET'])
def edit():
    if 'username' in session:
        # Ensure user role is 'admin' before allowing access to the edit page
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (session['username'],))
        user_role = cursor.fetchone()
        conn.close()

        if user_role and user_role[0] == 'admin':
            # Read data intents from dataset.json
            with open('dataset.json', 'r') as file:
                intents_data_list = json.load(file)['intents']

            return render_template('edit.html', intents_data=intents_data_list)
        else:
            flash('Anda tidak memiliki izin untuk mengakses halaman edit.', 'error')
            return redirect(url_for('base'))
    else:
        return redirect(url_for('login', _external=True))


def get_intent_data_list():
    connection = sqlite3.connect('chatbot.db')
    cursor = connection.cursor()

    cursor.execute("SELECT intent_name, tags, patterns, responses FROM intent_data")
    intents_data = cursor.fetchall()

    connection.close()

    # Format data intents sebagai list
    intents_data_list = []
    for intent_row in intents_data:
        json_patterns = intent_row[2].strip()
        json_responses = intent_row[3].strip()

    try:
        intent_data = {
            "intent_name": intent_row[0],
            "tags": intent_row[1],
            "patterns": json.loads(json_patterns),
            "responses": json.loads(json_responses)
        }
        intents_data_list.append(intent_data)
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON for intent: {e}")




def get_user_id(username):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    connection.close()
    return user_id

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json['message']
        response = chatbot_response(user_message)

        # Simpan log chat ke dalam tabel chat_logs
        if 'username' in session:
            user_id = get_user_id(session['username'])

            connection = sqlite3.connect('chatbot.db')
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO chat_logs (user_id, question, response)
                VALUES (?, ?, ?)
            ''', (user_id, user_message, response))
            connection.commit()
            connection.close()

        return jsonify({'answer': response})
    except Exception as e:
        return jsonify({'error': str(e)})
    

# Fungsi untuk mendapatkan log chat dari kedua database
def get_admin_chat_logs():
    # Koneksi ke database users
    conn_users = sqlite3.connect('users.db')
    cursor_users = conn_users.cursor()

    # Kueri ke tabel users untuk mendapatkan ID pengguna dan username
    cursor_users.execute("SELECT id, username FROM users")
    users_data = cursor_users.fetchall()

    # Tutup koneksi ke database users
    conn_users.close()

    # Koneksi ke database chatbot
    conn_chatbot = sqlite3.connect('chatbot.db')
    cursor_chatbot = conn_chatbot.cursor()

    # Kueri ke tabel chat_logs untuk mendapatkan log chat
    cursor_chatbot.execute("SELECT id, user_id, timestamp, question FROM chat_logs ORDER BY timestamp DESC")
    chat_logs = cursor_chatbot.fetchall()

    # Tutup koneksi ke database chatbot
    conn_chatbot.close()

    # Gabungkan data dari kedua database
    admin_chat_logs = []

    for log in chat_logs:
        user_id = log[1]

        # Temukan username yang sesuai berdasarkan user_id
        username = next((user[1] for user in users_data if user[0] == user_id), None)

        # Tambahkan log chat beserta username ke daftar admin_chat_logs
        admin_chat_logs.append({
            'id': log[0],
            'username': username,
            'timestamp': log[2],
            'question': log[3]
        })

    return admin_chat_logs

# Route untuk menampilkan log chat di halaman edit
@app.route('/admin/chat_logs')
def admin_chat_logs_route():
    # Pastikan hanya admin yang dapat mengakses halaman ini
    if 'username' in session:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (session['username'],))
        user_role = cursor.fetchone()
        conn.close()

        if user_role and user_role[0] == 'admin':
            # Ambil data log chat dari kedua database
            chat_logs = get_admin_chat_logs()

            return render_template('edit.html', chat_logs=chat_logs, permission_message="Anda memiliki izin untuk mengakses halaman ini.")
        else:
            permission_message = "Anda tidak memiliki izin untuk mengakses halaman ini."
            return render_template('edit.html', permission_message=permission_message)
    else:
        return redirect(url_for('login'))
    

# Menambahkan rute API untuk mengambil log chat (untuk digunakan oleh JavaScript)
@app.route('/api/admin/chat_logs')
def api_admin_chat_logs():
    # Pastikan hanya admin yang dapat mengakses API ini
    if 'username' in session:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (session['username'],))
        user_role = cursor.fetchone()
        conn.close()

        if user_role and user_role[0] == 'admin':
            # Ambil data log chat dari kedua database
            chat_logs = get_admin_chat_logs()

            return jsonify({'logs': chat_logs})
        else:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Unauthorized'}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
