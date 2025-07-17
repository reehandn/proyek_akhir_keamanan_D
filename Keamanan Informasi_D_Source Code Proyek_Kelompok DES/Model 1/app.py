from flask import Flask, render_template, request
from des_crypto import encrypt, decrypt  # Pastikan encrypt & decrypt menerima mode dan iv
import time
import os

app = Flask(__name__)
LOG_FILE = 'logs.txt'

def append_log(entry):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')


def read_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return f.read().splitlines()

@app.route('/', methods=['GET', 'POST'])
def index():
    plain_text = ''
    cipher_text = ''
    key = ''
    iv = ''
    mode = 'ECB'
    log = ''

    if request.method == 'POST':
        plain_text = request.form.get('plain_text', '')
        key = request.form.get('key', '')
        mode = request.form.get('mode', 'ECB')
        iv = request.form.get('iv', '')  # optional, only used in CBC

        if not key:
            cipher_text = 'Error: Key cannot be empty.'
        else:
            start_time = time.perf_counter_ns()

            try:
                if 'encrypt' in request.form:
                    cipher_text = encrypt(plain_text, key, mode, iv)
                    action = "Encrypt"
                elif 'decrypt' in request.form:
                    cipher_text = decrypt(plain_text, key, mode, iv)
                    action = "Decrypt"
                else:
                    action = "Unknown"
            except Exception as e:
                cipher_text = f"Error: {str(e)}"
                action = "Failed"

            end_time = time.perf_counter_ns()
            elapsed_time = end_time - start_time  # Waktu dalam nanosecond 

            # Format waktu dengan konversi satuan otomatis
            if elapsed_time >= 1_000_000:
                formatted_time = f"{elapsed_time/1_000_000:.2f} ms"
            elif elapsed_time >= 1_000:
                formatted_time = f"{elapsed_time/1_000:.2f} μs"
            else:
                formatted_time = f"{elapsed_time} ns"

            log = f"{action} ({mode}) | Key: {key} | IV: {iv or 'default'} | Time: {formatted_time}"
            append_log(log)

    log_history = read_logs()

    return render_template(
        'index.html',
        plain_text=plain_text,
        cipher_text=cipher_text,
        key=key,
        iv=iv,
        mode=mode,
        log_history=log_history
    )

if __name__ == '__main__':
    app.run(debug=True)
