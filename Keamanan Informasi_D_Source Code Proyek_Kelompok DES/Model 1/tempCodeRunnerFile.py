from flask import Flask, render_template, request
from des_crypto import encrypt, decrypt
import time
import os

app = Flask(__name__)
LOG_FILE = 'logs.txt'

def append_log(entry):
    with open(LOG_FILE, 'a') as f:
        f.write(entry + '\n')

def read_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r') as f:
        return f.read().splitlines()

@app.route('/', methods=['GET', 'POST'])
def index():
    plain_text = ''
    cipher_text = ''
    key = ''
    log = ''

    if request.method == 'POST':
        plain_text = request.form.get('plain_text', '')
        key = request.form.get('key', '')

        if not key:
            cipher_text = 'Error: Key cannot be empty.'
        else:
            start_time = time.time()
            if 'encrypt' in request.form:
                cipher_text = encrypt(plain_text, key)
                action = "Encryption"
            elif 'decrypt' in request.form:
                cipher_text = decrypt(plain_text, key)
                action = "Decryption"
            else:
                action = "Unknown"
            end_time = time.perf_counter_ns()
            elapsed_time = end_time - start_time  # Waktu dalam nanosecond 
            
            # Format waktu dengan konversi satuan otomatis
            if elapsed_time >= 1_000_000:
                formatted_time = f"{elapsed_time/1_000_000:.2f} ms"
            elif elapsed_time >= 1_000:
                formatted_time = f"{elapsed_time/1_000:.2f} μs"
            else:
