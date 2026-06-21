import io
from pathlib import Path
from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image


def optimize_image(image_file, max_width=1200, quality=80):
    img = Image.open(image_file)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format='WEBP', quality=quality, method=6)
    buffer.seek(0)

    original_name = Path(image_file.name).stem
    return buffer, f"{original_name}.webp"
