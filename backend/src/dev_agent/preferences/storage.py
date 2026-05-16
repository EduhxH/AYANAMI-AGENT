import uuid
from pathlib import Path

from fastapi import UploadFile

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_AVATAR_BYTES = 5 * 1024 * 1024


def get_upload_root() -> Path:
    root = Path(__file__).resolve().parents[3] / "uploads" / "avatars"
    root.mkdir(parents=True, exist_ok=True)
    return root


async def save_avatar_file(user_id: str, file: UploadFile) -> str:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Formato não suportado. Usa: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    content = await file.read()
    if len(content) > MAX_AVATAR_BYTES:
        raise ValueError("Avatar demasiado grande (máximo 5 MB).")

    safe_name = f"{user_id}_{uuid.uuid4().hex[:8]}{suffix}"
    path = get_upload_root() / safe_name
    path.write_bytes(content)

    return f"/uploads/avatars/{safe_name}"
