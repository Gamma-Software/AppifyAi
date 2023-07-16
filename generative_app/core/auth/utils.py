import struct
from binascii import b2a_base64 as e64
from binascii import a2b_base64 as d64
import scrypt
import Crypto.Random
random = Crypto.Random.new().read
from passlib.utils import consteq

_PARAMS = struct.Struct("!BBBB")

def pack_verifier( logN,r,p, salt, hash):
    packed = _PARAMS.pack(logN,r,p,len(salt)) + salt + hash
    return packed

def unpack_verifier(verifier):
    logN,r,p,salt_bytes = _PARAMS.unpack_from(verifier)
    i = _PARAMS.size+salt_bytes
    salt = verifier[_PARAMS.size:i]
    hash = verifier[i:]
    return logN,r,p,salt,hash

def make_verifier( password, logN=14, r=8, p=1, salt_bytes=16,hash_bytes=16):
    salt = random(salt_bytes)
    hash = scrypt.hash(password,salt,1<<logN,r,p,hash_bytes)
    return pack_verifier(logN,r,p,salt,hash)

def verify_password( password, verifier ):
    logN,r,p,salt,hash = unpack_verifier(verifier)
    newhash = scrypt.hash(password,salt,1<<logN,r,p,len(hash))
    return consteq(newhash,hash)

def crypt_password(password: str) -> bytes:
    return e64(make_verifier(password)).strip()

def is_password_ok(password: str, crypt: bytes) -> bool:
    return verify_password(password,d64(crypt))