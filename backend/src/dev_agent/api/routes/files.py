from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict
import zipfile
import io
import base64

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict:
    """Recebe um ficheiro (zip, image, text) e devolve um resumo/extracção básica."""
    content = await file.read()
    name = file.filename or "uploaded"
    lower = name.lower()

    result_files: List[Dict] = []

    # ZIP: extract text files
    if lower.endswith(".zip"):
        try:
            z = zipfile.ZipFile(io.BytesIO(content))
            for info in z.infolist()[:50]:
                if info.is_dir():
                    continue
                try:
                    with z.open(info) as fp:
                        data = fp.read()
                        if info.filename.lower().endswith((".md", ".txt", ".py", ".js", ".ts", ".java", ".go")):
                            text = data.decode("utf-8", errors="ignore")
                            result_files.append({"name": info.filename, "content": text[:4000]})
                        else:
                            result_files.append({"name": info.filename, "content": f"[binary {len(data)} bytes]"})
                except Exception:
                    continue
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Ficheiro zip inválido")

    elif lower.endswith((".png", ".jpg", ".jpeg", ".gif")):
        # Return base64 placeholder (processing/OCR optional)
        b64 = base64.b64encode(content).decode("ascii")
        result_files.append({"name": name, "content": f"[IMAGE base64:{len(b64)}]"})

    else:
        # Try decode as text
        try:
            text = content.decode("utf-8", errors="ignore")
            result_files.append({"name": name, "content": text[:8000]})
        except Exception:
            result_files.append({"name": name, "content": f"[binary {len(content)} bytes]"})

    return {"files": result_files}
