import qrcode
from io import BytesIO

def generate_qr_code(data: dict) -> BytesIO:
    """
    Generate a QR code (PNG) from data dictionary.
    Return an in-memory BytesIO object containing the PNG.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    # Convert dict to a simple string; you might use JSON
    import json
    qr.add_data(json.dumps(data))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def decode_qr_code(image_bytes: bytes) -> dict:
    """
    Decode a QR code from raw image bytes.
    Return a dictionary of the data that was encoded.
    This requires a library like `pyzbar` or similar.
    """
    from PIL import Image
    from pyzbar.pyzbar import decode
    img = Image.open(BytesIO(image_bytes))
    result = decode(img)
    if not result:
        return {}
    # Assume one code
    import json
    data_str = result[0].data.decode("utf-8")
    return json.loads(data_str)
