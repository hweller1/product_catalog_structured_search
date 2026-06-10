"""Compatibility shim for imghdr (removed in Python 3.13)."""

def what(file, h=None):
    """Determine the image type of a file or bytes-like object."""
    if h is None:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            h = file.read(32)
    if h[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if h[:2] in (b'\xff\xd8', b'\xff\xe0', b'\xff\xe1'):
        return 'jpeg'
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if h[:2] == b'BM':
        return 'bmp'
    if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'
    return None
