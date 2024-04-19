import chardet
import io
from octopus.core import app

def read_uploaded_file(uploaded_file):
    file_bytes = uploaded_file.stream.read()
    return file_bytes

def decode_csv_bytes(csv_bytes):
    encoding = chardet.detect(csv_bytes)['encoding']
    encoding_str = 'utf-8'
    if encoding in ['ISO-8859-1', 'UTF-8-SIG', 'UTF-8', 'utf-8']:
        encoding_str = encoding
    else:
        app.logger.warning(f'unknown encoding[{encoding}], decode as utf8')
    try:
        decoded_csv_bytes = csv_bytes.decode(encoding=encoding_str, errors='ignore')
    except Exception as e:
        return False, str(e)
    return True, decoded_csv_bytes