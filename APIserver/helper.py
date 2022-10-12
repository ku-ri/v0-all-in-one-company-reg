from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import base64
import os

# AES 방식 암호화
class AESCrypto(object):
    def __init__(self):
        block_size = 16
        padding = '|'.encode()
        secret = os.environ['AES_SECRET_KEY']
        cipher = AES.new(secret.encode('utf8'), AES.MODE_CBC)
        pad = lambda s: s + ((block_size - len(s) % block_size) * padding)
        self.encryptAES = lambda s: base64.b64encode(cipher.encrypt(pad(s)))
        self.decryptAES = lambda e: cipher.decrypt(base64.b64decode(e)).rstrip(base64.b64decode(padding))

    def encrypt(self, data):
        data = data.encode()
        encrypted = self.encryptAES(data).decode('utf-8').replace('/', '_')
        return encrypted

    def decrypt(self, data):
        data = data.replace('_', '/')
        padding = '|'
        decrypted = self.decryptAES(data).decode('utf-8').rstrip(padding)
        return decrypted

def sha256(to_encrypt):
    sha = SHA256.new()
    sha.update(bytes(to_encrypt, encoding='utf-8'))
    encrypted = sha.hexdigest()
    return encrypted

# I can help you api
