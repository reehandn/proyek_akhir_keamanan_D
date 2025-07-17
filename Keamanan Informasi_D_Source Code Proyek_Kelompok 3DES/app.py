import streamlit as st
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import time
import os
from dotenv import load_dotenv
import re
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
from email.mime.application import MIMEApplication

# ===== Load .env =====
load_dotenv()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Konfigurasi Email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "krisnap770@gmail.com"

# ===== Fungsi Enkripsi & Dekripsi =====
def generate_key():
    return get_random_bytes(24)  # 3DES key: 24 bytes

def encrypt_3des(data, key):
    cipher = DES3.new(key, DES3.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, DES3.block_size))
    return cipher.iv + ct_bytes

def decrypt_3des_with_unpad(encrypted_data, key):
    iv = encrypted_data[:8]
    ct = encrypted_data[8:]
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), DES3.block_size)

def decrypt_3des_no_unpad(encrypted_data, key):
    iv = encrypted_data[:8]
    ct = encrypted_data[8:]
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return cipher.decrypt(ct)


# ===== Kirim Email =====
def send_encryption_email(receiver_email, encrypted_data, key_hex, filename, encrypt_time):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver_email
    msg["Subject"] = "Hasil Enkripsi Dokumen 3DES"

    encrypted_b64 = base64.b64encode(encrypted_data).decode()
    body = f"""
Dokumen berhasil dienkripsi dan dilampirkan sebagai file terenkripsi (.enc).

🔒 Hasil Enkripsi (base64) (hanya sebagian ditampilkan):
{encrypted_b64[:100]}...

🔑 Kunci 3DES (hex):
{key_hex}

📅 Waktu proses: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
⏱️ Durasi enkripsi: {encrypt_time:.4f} detik

⚠️ Simpan kunci ini untuk keperluan dekripsi!
"""

    msg.attach(MIMEText(body, "plain"))

    attachment = MIMEApplication(encrypted_data)
    attachment.add_header("Content-Disposition", "attachment", filename=f"encrypted_{filename}.enc")
    msg.attach(attachment)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# ===== UI Streamlit =====
st.set_page_config(page_title="Enkripsi & Dekripsi 3DES", layout="centered")
st.title("🔐 Enkripsi & Dekripsi Dokumen 3DES")

menu = st.sidebar.radio("Pilih Mode", ["Enkripsi", "Dekripsi"])

# ========================================
# ========== Bagian Enkripsi ============
# ========================================
if menu == "Enkripsi":
    st.header("🔒 Enkripsi Dokumen dan Kirim ke Email")
    uploaded_file = st.file_uploader("📄 Unggah file (.txt / .pdf / .docx)", type=["txt", "pdf", "docx"])
    email_receiver = st.text_input("📧 Masukkan alamat email tujuan")

    if st.button("Enkripsi & Kirim"):
        if not uploaded_file or not email_receiver:
            st.warning("Silakan unggah file dan isi alamat email.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email_receiver):
            st.warning("Alamat email tidak valid.")
        else:
            try:
                file_content = uploaded_file.read()
                filename = uploaded_file.name
                key = generate_key()

                start_time = time.time()
                encrypted_data = encrypt_3des(file_content, key)
                encrypt_time = time.time() - start_time

                send_encryption_email(email_receiver, encrypted_data, key.hex(), filename, encrypt_time)

                st.success(f"✅ Hasil enkripsi berhasil dikirim ke {email_receiver}")
                st.write(f"⏱️ Waktu enkripsi: {encrypt_time:.4f} detik")
                st.subheader("📦 Hasil Enkripsi (Base64)")
                st.text_area("Base64 Enkripsi", base64.b64encode(encrypted_data).decode(), height=150)

                st.warning("⚠️ Simpan kunci ini untuk dekripsi!")
                st.code(key.hex())

                st.download_button(
                    label="⬇️ Unduh File Terenkripsi (.enc)",
                    data=encrypted_data,
                    file_name=f"encrypted_{filename}.enc",
                    mime="application/octet-stream"
                )
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")

# ========================================
# ========== Bagian Dekripsi ============
# ========================================
elif menu == "Dekripsi":
    st.header("🔓 Dekripsi File Terenkripsi (.enc)")
    encrypted_file = st.file_uploader("📤 Unggah file terenkripsi (.enc)", type=["enc"], key="decrypt_file")
    key_hex_input = st.text_input("🔑 Masukkan Kunci 3DES (hex)", key="decrypt_key")
    output_filename = st.text_input("📁 Nama file hasil dekripsi (cth: hasil.txt, hasil.pdf, hasil.docx)", key="decrypt_name")
    
    safe_mode = st.checkbox("Gunakan unpad (hasil bersih, file asli) — jika ingin file bisa dibuka normal", value=True)

    if st.button("Dekripsi"):
        if not encrypted_file or not key_hex_input or not output_filename:
            st.warning("Mohon lengkapi semua kolom dan unggah file.")
        else:
            try:
                encrypted_data = encrypted_file.read()
                key = bytes.fromhex(key_hex_input.strip())

                start_time = time.time()
                if safe_mode:
                    decrypted_data = decrypt_3des_with_unpad(encrypted_data, key)
                else:
                    decrypted_data = decrypt_3des_no_unpad(encrypted_data, key)
                decrypt_time = time.time() - start_time

                st.success("✅ Dekripsi selesai!")
                st.write(f"⏱️ Waktu dekripsi: {decrypt_time:.4f} detik")

                if output_filename.endswith(".txt"):
                    st.text_area("📄 Isi File", decrypted_data.decode(errors='replace'), height=200)

                st.download_button(
                    label="⬇️ Unduh Hasil Dekripsi",
                    data=decrypted_data,
                    file_name=output_filename,
                    mime="application/octet-stream"
                )

            except Exception as e:
                st.error(f"❌ Gagal mendekripsi: {e}")
