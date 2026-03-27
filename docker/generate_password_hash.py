#!/usr/bin/env python3
"""生成密码的 bcrypt 哈希值"""
import bcrypt
import sys

if len(sys.argv) < 2:
    password = "admin123"
else:
    password = sys.argv[1]

password_bytes = password.encode('utf-8')[:72]
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt)
print(hashed.decode('utf-8'))

