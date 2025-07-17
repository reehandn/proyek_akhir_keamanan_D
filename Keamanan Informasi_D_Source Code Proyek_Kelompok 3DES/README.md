# 🔐 Aplikasi Enkripsi & Dekripsi Dokumen 3DES dengan Streamlit

Aplikasi ini memungkinkan pengguna untuk **mengunggah file dokumen (.txt, .pdf, .docx)** dan melakukan **enkripsi menggunakan algoritma 3DES**. Hasil enkripsi dikirim melalui email dan dapat dideskripsi kembali menggunakan kunci 3DES.

---

## 📦 Fitur

- Enkripsi file menggunakan **algoritma Triple DES (3DES, CBC Mode + Padding)**
- Kirim file terenkripsi ke alamat email tujuan
- Dekripsi file `.enc` menggunakan kunci hex yang diberikan
- Tampilan antarmuka berbasis **Streamlit**
- Mendukung mode dekripsi aman (dengan `unpad`) atau mentah (tanpa `unpad`)

---

## ⚙️ Cara Menjalankan Aplikasi

### 1. Clone atau Simpan Proyek

Pastikan file Python disimpan sebagai `app.py`.

### 2. Install Dependensi

```bash
pip install streamlit pycryptodome python-dotenv
```

### 3. Buat File `.env`

Buat file `.env` di direktori yang sama dengan `app.py`:

```
EMAIL_PASSWORD=your_gmail_app_password
```

> ⚠️ Gunakan **App Password Gmail**, bukan password biasa. Aktifkan 2-Step Verification di akun Gmail terlebih dahulu.

### 4. Jalankan Aplikasi

```bash
streamlit run app.py
```

---

## 💌 Konfigurasi Email

- Server SMTP: `smtp.gmail.com`
- Port: `587`
- Email pengirim: `krisnap770@gmail.com` *(bisa disesuaikan di kode)*
- Email penerima: sesuai input dari pengguna di UI

---

## 📁 Format File yang Didukung

- **Untuk Enkripsi**: `.txt`, `.pdf`, `.docx`
- **Untuk Dekripsi**: `.enc` hasil dari enkripsi aplikasi ini

---

## 🛡️ Catatan Keamanan

- Kunci 3DES hanya ditampilkan sekali setelah enkripsi.
- Pastikan untuk menyimpan kunci tersebut agar dapat digunakan untuk dekripsi.
- File dan kunci dikirim melalui email sebagai lampiran.

---

## ✅ Contoh Output Email

- Lampiran file: `encrypted_namafile.enc`
- Isi email:
  - Hasil enkripsi (base64, sebagian)
  - Kunci enkripsi (hex)
  - Waktu dan durasi proses

---

## Lisensi

Proyek ini untuk keperluan pembelajaran dan tugas akademik. Gunakan secara bijak.