from flask import Flask, request, redirect, jsonify
import sqlite3
import hashlib
import base64

app = Flask(__name__)

# Conexión a la base de datos SQLite
conn = sqlite3.connect('url_shortener.db', check_same_thread=False)
cursor = conn.cursor()

# Crear tabla para almacenar URLs si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    long_url TEXT NOT NULL,
    short_url TEXT NOT NULL UNIQUE
)
''')
conn.commit()

def generar_url_corta(url_larga):
    hash_object = hashlib.sha256(url_larga.encode())
    base64_encoded = base64.urlsafe_b64encode(hash_object.digest()).decode('utf-8')[:6]
    return base64_encoded

def acortar_url(url_larga):
    cursor.execute("SELECT short_url FROM urls WHERE long_url = ?", (url_larga,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    url_corta = generar_url_corta(url_larga)
    
    cursor.execute("INSERT INTO urls (long_url, short_url) VALUES (?, ?)", (url_larga, url_corta))
    conn.commit()
    
    return url_corta

def obtener_url_larga(url_corta):
    cursor.execute("SELECT long_url FROM urls WHERE short_url = ?", (url_corta,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    url_larga = data['url']
    url_corta = acortar_url(url_larga)
    return jsonify({'short_url': request.host_url + url_corta})

@app.route('/<url_corta>')
def redirect_to_long_url(url_corta):
    url_larga = obtener_url_larga(url_corta)
    if url_larga:
        return redirect(url_larga)
    else:
        return jsonify({'error': 'URL corta no encontrada'}), 404

@app.route('/')
def home():
    return "Bienvenido a mi aplicación Flask!"

if __name__ == '__main__':
    app.run(debug=True)
