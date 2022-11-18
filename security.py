import hashlib
from Crypto.Random import get_random_bytes
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512


def kdf(password, salt):
    keys = PBKDF2(password, salt, 64, count=1000000, hmac_hash_module=SHA512)
    key = keys[:32]
    return key

def make_salt():
    salt = get_random_bytes(16)
    return salt

def AES_Encrypt(key, data): # The data should be in bytes here
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    ct = b64encode(ct_bytes).decode('utf-8')
    iv = b64encode(ECB_encrypt(cipher.iv, key)).decode('utf-8')
    encrypted_data = {'iv': iv, 'ct': ct}
    return encrypted_data

    
def AES_Decrypt(key, encrypted_data): # enrypted_data is a dictionary which contains the encrypted form of the iv and the encrypted data
    iv = ECB_decrypt(b64decode(encrypted_data['iv']), key) # decoding from base64 and then getting the iv back by decrypting it
    ct = b64decode(encrypted_data['ct'])
    cipher = AES.new(key, AES.MODE_CBC, iv = iv )
    pt_bytes = unpad(cipher.decrypt(ct), AES.block_size)
    return pt_bytes

