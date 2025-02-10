import os

def absolute_path(relative_path: str) -> str:
    """Returns the absolute path of a given file with forward slashes."""
    return os.path.abspath(relative_path).replace("\\", "/")
