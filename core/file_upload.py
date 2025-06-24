import os
import uuid
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
from PIL import Image
import io


MEDIA_DIR = "media"
ALLOWED_TYPES = {
    # Изображения
    "image/jpeg": "image",
    "image/png": "image",
    "image/gif": "image",
    "image/webp": "image",
    "image/svg+xml": "image",
    "image/tiff": "image",

    # Видео
    "video/mp4": "video",
    "video/mpeg": "video",
    "video/ogg": "video",
    "video/webm": "video",
    "video/quicktime": "video",
    "video/x-msvideo": "video",  # AVI

    # Аудио
    "audio/mpeg": "audio",
    "audio/ogg": "audio",
    "audio/wav": "audio",
    "audio/webm": "audio",
    "audio/aac": "audio",
    "audio/flac": "audio",

    # Документы
    "application/pdf": "document",
    "application/msword": "document",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",  # .docx
    "application/vnd.ms-excel": "document",  # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "document",  # .xlsx
    "application/vnd.ms-powerpoint": "document",  # .ppt
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "document",  # .pptx
    "text/plain": "document",
    "text/csv": "document",
    "text/html": "document",
    "application/rtf": "document",

    # Архивы
    "application/zip": "archive",
    "application/x-tar": "archive",
    "application/x-rar-compressed": "archive",
    "application/x-7z-compressed": "archive",
    "application/gzip": "archive",

    # Прочие
    "application/json": "other",
    "application/xml": "other",
    "application/octet-stream": "other"
}


def get_file_type(content_type: str) -> str:
    if content_type in ALLOWED_TYPES:
        return ALLOWED_TYPES[content_type]

    if content_type.startswith("image/"):
        return "image"
    if content_type.startswith("video/"):
        return "video"
    if content_type.startswith("audio/"):
        return "audio"
    if content_type.startswith("text"):
        return "document"

    return "other"


async def generate_image_thumbnail(
        file_path: Path,
        size: tuple = (300, 300)
) -> str:
    try:
        thumb_dir = Path("thumbnails")
        thumb_dir.mkdir(exist_ok=True)

        thumb_name = f"thumb_{file_path.stem}.jpg"
        thumb_path = thumb_dir / thumb_name

        with Image.open(file_path) as img:
            img.thumbnail(size)

        if img.mode != "RGB":
            img = img.convert("RGB")

        img.save(thumb_path, "JPEG", quality=85)

        return f"/thumbnails/{thumb_name}"
    except Exception as e:
        print(f"Error:{e}")
        return None


async def save_uploaded_file(file: UploadFile) -> dict:
    content_type = file.content_type or "application/octet-stream"

    file_type = get_file_type(content_type)
    if file_type == "unknown":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {content_type}"
        )

    media_path = Path(MEDIA_DIR)
    media_path.mkdir(parents=True,exist_ok=True)

    file_ext = file.filename.split('.')[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(MEDIA_DIR, file_name)

    file_size = 0
    with open(file_path, "wb") as buffer:
        while content := await file.read(1024*1024):
            buffer.write(content)
            file_size += len(content)

    thumbnail_url = None
    if file_type == "image":
        thumbnail_url = await generate_image_thumbnail(file_path)

    return {
        "file_url": f"/{MEDIA_DIR}/{file_name}",
        "file_name": file.filename,
        "file_type": file_type,
        "file_size": file_size,
        "thumbnail_url": thumbnail_url
    }
