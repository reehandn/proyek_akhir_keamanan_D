from flask import Flask, render_template, request, session
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import time

app = Flask(__name__)
app.secret_key = 'supersecret'  # Kunci rahasia untuk session

# Fungsi untuk generate kunci RSA dengan durasi waktu
def generate_keys():
    start_time = time.time()
    key = RSA.generate(2048)
    duration = time.time() - start_time
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    return private_key, public_key, duration

# Fungsi enkripsi dengan durasi waktu
def encrypt_note(note, public_key_str):
    try:
        start_time = time.time()
        recipient_key = RSA.import_key(public_key_str)
        cipher = PKCS1_OAEP.new(recipient_key)
        encrypted = cipher.encrypt(note.encode())
        duration = time.time() - start_time
        return base64.b64encode(encrypted).decode(), duration
    except Exception as e:
        return f"[ENCRYPTION FAILED] {e}", 0

# Fungsi dekripsi dengan durasi waktu
def decrypt_note(ciphertext, private_key_str):
    try:
        start_time = time.time()
        private_key = RSA.import_key(private_key_str)
        cipher = PKCS1_OAEP.new(private_key)
        decrypted = cipher.decrypt(base64.b64decode(ciphertext))
        duration = time.time() - start_time
        return decrypted.decode(), duration
    except Exception as e:
        return f"[DECRYPTION FAILED] {e}", 0

# Routing utama
@app.route("/", methods=["GET", "POST"])
def index():
    encrypted_note = ""
    decrypted_note = ""

    if request.method == "POST":
        action = request.form.get("action")

        # Generate RSA key
        if action == "generate":
            private_key, public_key, duration = generate_keys()
            session["private_key"] = private_key
            session["public_key"] = public_key
            session["keygen_timing"] = f"🔑 Waktu generate key: {duration:.4f} detik"
            session["encrypt_timing"] = ""
            session["decrypt_timing"] = ""

        # Enkripsi catatan
        elif action == "encrypt":
            note = request.form.get("note")
            public_key = session.get("public_key")
            if public_key and note:
                encrypted_note, duration = encrypt_note(note, public_key)
                session["encrypt_timing"] = f"🛡️ Waktu enkripsi: {duration:.4f} detik"

        # Dekripsi catatan
        elif action == "decrypt":
            ciphertext = request.form.get("ciphertext")
            private_key = request.form.get("private_key") or session.get("private_key")
            if ciphertext and private_key:
                decrypted_note, duration = decrypt_note(ciphertext, private_key)
                session["decrypt_timing"] = f"🔓 Waktu dekripsi: {duration:.4f} detik"

    return render_template("index.html",
                           public_key=session.get("public_key", ""),
                           private_key=session.get("private_key", ""),
                           encrypted_note=encrypted_note,
                           decrypted_note=decrypted_note,
                           keygen_timing=session.get("keygen_timing", ""),
                           encrypt_timing=session.get("encrypt_timing", ""),
                           decrypt_timing=session.get("decrypt_timing", ""))

# Jalankan aplikasi Flask
if __name__ == "__main__":
    app.run(debug=True)
