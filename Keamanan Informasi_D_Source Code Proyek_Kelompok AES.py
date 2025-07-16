import smtplib
from email.message import EmailMessage
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter import ttk
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
import time


def encrypt_message(message, password, key_length_bits):
    salt = get_random_bytes(16)
    iv = get_random_bytes(AES.block_size)
    dk_len_bytes = key_length_bits // 8
    key = PBKDF2(password.encode(), salt, dkLen=dk_len_bytes, count=100000)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded_message = pad(message.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_message)

    encrypted = salt + iv + ciphertext
    return encrypted.hex()


def send_encrypted_email():
    sender_email = entry_your_email.get()
    app_password = entry_app_password.get()
    receiver_email = entry_send_to.get()
    subject = entry_subject.get()
    message = text_message.get("1.0", END).strip()
    aes_key = entry_aes_key.get()
    selected_key_length_str = combo_key_length.get()

    if not selected_key_length_str:
        messagebox.showerror("Error", "Pilih panjang kunci AES!")
        return

    key_length_bits = int(selected_key_length_str.split('-')[1].replace('bit', ''))

    if not (sender_email and app_password and receiver_email and subject and message and aes_key):
        messagebox.showerror("Error", "Semua kolom harus diisi!")
        return

    try:
        start_time = time.time()

        encrypted_msg = encrypt_message(message, aes_key, key_length_bits)

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.set_content(encrypted_msg)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)

        end_time = time.time()
        elapsed = end_time - start_time
        logtime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        messagebox.showinfo("Sukses", f"Email terenkripsi berhasil dikirim!\nWaktu: {logtime}\nDurasi: {elapsed:.3f} detik")

    except Exception as e:
        messagebox.showerror("Error", f"Gagal mengirim email: {str(e)}")


def decrypt_message(encrypted_hex, password, key_length_bits):
    encrypted = bytes.fromhex(encrypted_hex)
    salt = encrypted[:16]
    iv = encrypted[16:32]
    ciphertext = encrypted[32:]

    dk_len_bytes = key_length_bits // 8
    key = PBKDF2(password.encode(), salt, dkLen=dk_len_bytes, count=100000)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_padded_message = cipher.decrypt(ciphertext)

    try:
        plaintext_bytes = unpad(decrypted_padded_message, AES.block_size)
    except ValueError:
        plaintext_bytes = decrypted_padded_message

    try:
        return plaintext_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return plaintext_bytes.decode('latin-1', errors='replace')


def run_decryption():
    encrypted_hex = text_encrypted.get("1.0", END).strip()
    aes_key_decrypt = entry_key_decrypt.get()
    selected_key_length_decrypt_str = combo_key_length_decrypt.get()

    if not selected_key_length_decrypt_str:
        messagebox.showerror("Error", "Pilih panjang kunci AES!")
        return

    key_length_bits_decrypt = int(selected_key_length_decrypt_str.split('-')[1].replace('bit', ''))

    if not encrypted_hex or not aes_key_decrypt:
        messagebox.showerror("Error", "Pesan terenkripsi dan kunci AES harus diisi!")
        return

    start_time = time.time()
    result = decrypt_message(encrypted_hex, aes_key_decrypt, key_length_bits_decrypt)
    end_time = time.time()
    elapsed = end_time - start_time
    logtime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filepath:
        with open(filepath, "w", encoding='utf-8', errors='replace') as f:
            f.write(f"[Didekripsi pada: {logtime} | Durasi: {elapsed:.3f} detik]\n\n{result}")
        messagebox.showinfo("Dekripsi Selesai", f"Hasil dekripsi disimpan di:\n{filepath}\nWaktu: {logtime}\nDurasi: {elapsed:.3f} detik")


def open_encrypt_gui():
    encrypt_window = Toplevel()
    encrypt_window.title("Enkripsi & Kirim Email (CBC Mode)")
    encrypt_window.geometry("650x550")
    frame = ttk.Frame(encrypt_window, padding=15)
    frame.pack(fill=BOTH, expand=True)

    for i in range(7):
        frame.rowconfigure(i, weight=1)
    frame.columnconfigure(1, weight=1)

    def add_labeled_entry(label_text, row, show=None):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="e", pady=5, padx=5)
        entry = ttk.Entry(frame, width=40, show=show)
        entry.grid(row=row, column=1, pady=5, padx=5, sticky="ew")
        return entry

    global entry_your_email, entry_app_password, entry_send_to, entry_subject, entry_aes_key, text_message, combo_key_length

    entry_your_email = add_labeled_entry("Email Anda:", 0)
    entry_app_password = add_labeled_entry("Password Aplikasi:", 1, show="*")
    entry_send_to = add_labeled_entry("Kirim ke Email:", 2)
    entry_subject = add_labeled_entry("Subjek:", 3)
    entry_aes_key = add_labeled_entry("Kunci AES:", 4, show="*")

    ttk.Label(frame, text="Panjang Kunci AES:").grid(row=5, column=0, sticky="e", pady=5, padx=5)
    key_length_options = ["AES-128-bit", "AES-192-bit", "AES-256-bit"]
    combo_key_length = ttk.Combobox(frame, values=key_length_options, state="readonly")
    combo_key_length.set("AES-256-bit")
    combo_key_length.grid(row=5, column=1, pady=5, padx=5, sticky="ew")

    ttk.Label(frame, text="Pesan:").grid(row=6, column=0, sticky="ne", pady=5, padx=5)
    text_message = Text(frame, height=10)
    text_message.grid(row=6, column=1, pady=5, padx=5, sticky="nsew")

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=7, column=1, pady=15, sticky="e")
    ttk.Button(button_frame, text="Kirim Pesan", command=send_encrypted_email).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="Kembali", command=encrypt_window.destroy).pack(side=LEFT, padx=5)


def open_decrypt_gui():
    decrypt_window = Toplevel()
    decrypt_window.title("Dekripsi Pesan (CBC Mode)")
    decrypt_window.geometry("650x450")
    frame = ttk.Frame(decrypt_window, padding=15)
    frame.pack(fill=BOTH, expand=True)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(0, weight=1)

    global text_encrypted, entry_key_decrypt, combo_key_length_decrypt

    ttk.Label(frame, text="Pesan Terenkripsi (hex):").grid(row=0, column=0, sticky="ne", pady=5, padx=5)
    text_encrypted = Text(frame, height=10)
    text_encrypted.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")

    ttk.Label(frame, text="Kunci AES:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
    entry_key_decrypt = ttk.Entry(frame, show="*")
    entry_key_decrypt.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

    ttk.Label(frame, text="Panjang Kunci AES:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
    key_length_options_decrypt = ["AES-128-bit", "AES-192-bit", "AES-256-bit"]
    combo_key_length_decrypt = ttk.Combobox(frame, values=key_length_options_decrypt, state="readonly")
    combo_key_length_decrypt.set("AES-256-bit")
    combo_key_length_decrypt.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=3, column=1, pady=15, sticky="e")
    ttk.Button(button_frame, text="Dekripsi dan Simpan", command=run_decryption).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="Kembali", command=decrypt_window.destroy).pack(side=LEFT, padx=5)


# Main Window
root = Tk()
root.title("AES Enkripsi Email (CBC Mode)")
root.geometry("400x250")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=BOTH, expand=True)

ttk.Label(main_frame, text="Pilih Mode Operasi", font=("Arial", 14)).pack(pady=20)
ttk.Button(main_frame, text="\U0001F510 Enkripsi dan Kirim Pesan", command=open_encrypt_gui).pack(pady=10, ipadx=10, ipady=5)
ttk.Button(main_frame, text="\U0001F513 Dekripsi Pesan dari Email", command=open_decrypt_gui).pack(pady=10, ipadx=10, ipady=5)

root.mainloop()