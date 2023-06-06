import re
from typing import Iterable

import rsa
from django.template import Library
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe, SafeString

from messaging.models import CustomUser, GroupMessage

register = Library()


@register.filter
def decrypt_with(encrypted: bytes, private_key: rsa.PrivateKey):
    return rsa.decrypt(encrypted, private_key).decode("utf8")


@register.filter(is_safe=True)
def highlight_mentions(value: str, users: Iterable[CustomUser]) -> SafeString:
    escaped_value = escape(value)
    for user in users:
        pattern = fr"@{user.username}\b"
        replacement = f'<a class="mention" href="#">@{user.username}</a>'
        matches = re.search(pattern, escaped_value)
        print(f"searched '{pattern}' over '{escaped_value}' and found {matches}")
        escaped_value = re.sub(pattern, replacement, escaped_value)
    return mark_safe(escaped_value)


@register.filter
def is_mentioned_in(user: CustomUser, message: GroupMessage) -> bool:
    return re.search(fr"@{user.username}\b", message.content) is not None
