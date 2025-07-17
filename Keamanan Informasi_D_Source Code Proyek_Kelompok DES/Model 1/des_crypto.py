from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import base64

def get_fixed_key(key_str):
    """Ambil 8 byte dari key, padding jika kurang."""
    return key_str.encode()[:8].ljust(8, b'\x00')

def get_iv(iv_str=None):
    """Gunakan IV dari user atau default (8 nol)."""
    if iv_str:
        return iv_str.encode()[:8].ljust(8, b'\x00')
    return b'\x00' * 8  # default IV

def encrypt(text, key_str, mode='ECB', iv_str=None):
    key = get_fixed_key(key_str)
    padded = pad(text.encode(), 8)

    if mode.upper() == 'ECB':
        cipher = DES.new(key, DES.MODE_ECB)
        encrypted = cipher.encrypt(padded)
    elif mode.upper() == 'CBC':
        iv = get_iv(iv_str)
        cipher = DES.new(key, DES.MODE_CBC, iv)
        encrypted = cipher.encrypt(padded)
    else:
        raise ValueError("Mode not supported: choose 'ECB' or 'CBC'")

    return base64.b64encode(encrypted).decode()

def decrypt(cipher_text, key_str, mode='ECB', iv_str=None):
    key = get_fixed_key(key_str)
    data = base64.b64decode(cipher_text)

    if mode.upper() == 'ECB':
        cipher = DES.new(key, DES.MODE_ECB)
        decrypted = cipher.decrypt(data)
    elif mode.upper() == 'CBC':
        iv = get_iv(iv_str)
        cipher = DES.new(key, DES.MODE_CBC, iv)
        decrypted = cipher.decrypt(data)
    else:
        raise ValueError("Mode not supported: choose 'ECB' or 'CBC'")

    return unpad(decrypted, 8).decode()
