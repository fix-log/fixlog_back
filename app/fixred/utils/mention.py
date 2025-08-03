import re

from app.accounts.models import User


def extract_mentioned_users(content):
    mentions = re.findall(r"@(\w+)", content)
    return User.objects.filter(username__in=mentions)
