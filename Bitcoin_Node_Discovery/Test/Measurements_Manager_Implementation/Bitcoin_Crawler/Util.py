import os

import requests
import click
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_key(public_exponent=65537, key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
        backend=default_backend()
    )

    return private_key


def load_key(file_name, password):
    pwd = bytes(password, encoding="utf-8")
    with open(file_name, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=pwd,
            backend=default_backend()
        )

    return private_key


def store_key(private_key, file_name, password):
    pwd = bytes(password, encoding="utf-8")
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(pwd)
    )

    f = open(file_name, 'wb')

    f.write(pem)

    f.close()


def get_private_key(private_key_file):
    if os.path.isfile(private_key_file):
        if click.confirm('File containing a private key has been detected. '
                         'Do you want to load it (the file will be overwritten if No) ?', default=True):
            print("Enter the Password for decrypting the Private Key :")
            password = input()
            private_key = load_key(private_key_file, password)

            return private_key
        else:
            if not click.confirm('You pressed No. Do you confirm ?', default=True):
                print("Enter the Password for decrypting the Private Key :")
                password = input()
                private_key = load_key(private_key_file, password)

                return private_key

    private_key = generate_key()
    print("Enter the Password for encrypting the Private Key :")
    password = input()
    store_key(private_key, private_key_file, password)

    return private_key


def public_key_to_bytes(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def bytes_to_public_key(public_key_bytes):
    return serialization.load_pem_public_key(
        data=public_key_bytes,
        backend=default_backend()
    )


def get_public_ip():
    result = requests.get('https://api.ipify.org?format=json')

    ip = result.json()["ip"]

    return ip