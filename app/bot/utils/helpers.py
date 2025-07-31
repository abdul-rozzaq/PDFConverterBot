import os
import magic
import aiofiles
from pathlib import Path
from typing import Optional, Tuple
from app.core.config import settings


async def get_file_info(file_path: str) -> Tuple[str, int, str]:
    """Get file MIME type, size, and extension"""
    try:
        # Get file size
        file_size = os.path.getsize(file_path)

        # Get MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)

        # Get extension
        extension = Path(file_path).suffix.lower().lstrip(".")

        return mime_type, file_size, extension

    except Exception as e:
        raise Exception(f"Failed to get file info: {str(e)}")


def is_file_size_valid(file_size: int) -> bool:
    """Check if file size is within limits"""
    return file_size <= settings.MAX_FILE_SIZE


def get_file_type_from_mime(mime_type: str) -> Optional[str]:
    """Get simplified file type from MIME type"""
    mime_mapping = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "text/plain": "txt",
    }
    return mime_mapping.get(mime_type)


async def cleanup_temp_files(*file_paths: str):
    """Clean up temporary files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Ignore cleanup errors


async def save_telegram_file(file_path: str, file_content: bytes) -> str:
    """Save Telegram file to local storage"""
    temp_dir = Path(settings.TEMP_DIR)
    temp_dir.mkdir(exist_ok=True)

    local_path = temp_dir / Path(file_path).name

    async with aiofiles.open(local_path, "wb") as f:
        await f.write(file_content)

    return str(local_path)
