response = b'\x88\x02\x03\xf3'

try:
    iso_text = response.decode('iso-8859-1')
    print("[✓]iso-8859-1: ", iso_text)
except Exception as e:print("[✗]E:", e)

try:
    bytes_utf8 = iso_text.encode('utf-8')
    print("[✓]utf-8: ", bytes_utf8.decode('utf-8'))
except Exception as e:print("[✗]E:", e)
