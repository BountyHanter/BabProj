import os
import uuid


def generate_unique_filename(file_name):
    ext = os.path.splitext(file_name)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    return unique_name


# Проверка допустимых типов файлов
def is_valid_file_type(file):
    valid_mime_types = [
        'application/pdf',  # PDF
        'image/jpeg',       # JPEG
        'image/png',        # PNG
    ]
    return file.content_type in valid_mime_types
