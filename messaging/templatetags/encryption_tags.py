import rsa
from django.template import Library

register = Library()


@register.filter
def decrypt_with(encrypted: bytes, private_key: rsa.PrivateKey):
    return rsa.decrypt(encrypted, private_key).decode("utf8")
