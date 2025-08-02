from typing import Optional
from shortuuid import ShortUUID
import os

short = ShortUUID()


def generate_uniq_filename(filename: str, ext: Optional[str] = None, uuid_length=6) -> str:
    base, orig_ext = os.path.splitext(filename)
    new_ext = ext or orig_ext.lstrip(".")
    uuid = short.uuid()[:uuid_length]
    return f"{base}-{uuid}.{new_ext}"
