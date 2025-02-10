import hashlib

def hashed(s: str) -> int:
    """Converts a string into an 8-digit integer hash."""
    hash_object = hashlib.md5(s.encode())  # Create MD5 hash
    hash_int = int(hash_object.hexdigest(), 16)  # Convert hash to integer
    return hash_int % 10**8  # Keep only the last 8 digits
