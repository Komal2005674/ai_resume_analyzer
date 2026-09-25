import re


def clean_text(text):
    text = text.lower()

    # Keep useful skill characters such as +, #, and . for C++, C#, and .NET.
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()