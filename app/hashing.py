# hashing.py
import hashlib

def hash_value(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def check_value(hashed_password, password, salt):
    return hashed_password == hash_value(password, salt)
