import uuid


def is_valid_uuid4(s: str) -> bool:
    try:
        val = uuid.UUID(s, version=4)
        # Check if the string is exactly v4 (not just valid UUID of any version)
        return val.version == 4 and str(val) == s.lower()
    except ValueError:
        return False