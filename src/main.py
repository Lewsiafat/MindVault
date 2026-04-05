import os
import re
import json
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

BASE_PATH = os.environ.get("BASE_PATH", "mind-vault").strip("/")
root_path = f"/{BASE_PATH}" if BASE_PATH else ""

app = FastAPI(title="MindVault", root_path=root_path)

DATA_DIR = Path(__file__).parent.parent / "data"
NOTES_FILE = DATA_DIR / "notes.md"

# Sub-folders to scan
SUBFOLDERS = {
    "articles": "📰 文章",
    "saves": "💾 儲存",
    "conversations": "💬 對話記錄",
}

_gemini_key = os.environ.get("GEMINI_API_KEY", "")
if _gemini_key:
    genai.configure(api_key=_gemini_key)
_model = genai.GenerativeModel("gemini-2.0-flash-lite") if _gemini_key else None

# ─── helpers ───────────────────────────────────────────────

def load_notes() -> str:
    if not NOTES_FILE.exists():
        return ""
    return NOTES_FILE.read_text(encoding="utf-8")


def load_all_docs() -> list[dict]:
    """Load all documents from data/ and sub-folders."""
    docs = []

    # notes.md (root)
    if NOTES_FILE.exists():
        docs.append({
            "name": "notes.md",
            "label": "📋 個人筆記",
            "folder": "root",
            "content": NOTES_FILE.read_text(encoding="utf-8"),
            "path": str(NOTES_FILE),
        })

    # sub-folders
    for folder, label in SUBFOLDERS.items():
        folder_path = DATA_DIR / folder
        if not folder_path.exists():
            continue
        for f in sorted(folder_path.glob("*.md")):
            try:
                content = f.read_text(encoding="utf-8")
                docs.append({
                    "name": f.name,
                    "label": label,
                    "folder": folder,
                    "content": content,
                    "path": str(f),
                })
            except Exception:
                pass

    return docs


def parse_sections(text: str) -> list[dict]:
    """Parse markdown into sections by ## headings."""
    sections = []
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                sections.append(current)
            current = {"title": line[3:].strip(), "content": "", "items": []}
        elif line.startswith("### ") and current:
            current["content"] += line + "\n"
        elif current:
            current["content"] += line + "\n"
            m = re.match(r"^[-*]\s+(.+)", line)
            if m:
                current["items"].append(m.group(1).strip())
    if current:
        sections.append(current)
    return sections


def extract_all_items(text: str) -> list[dict]:
    items = []
    current_h2 = ""
    current_h3 = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current_h2 = line[3:].strip()
            current_h3 = ""
        elif line.startswith("### "):
            current_h3 = line[4:].strip()
        else:
            m = re.match(r"^[-*]\s+(.+)", line)
            if m:
                items.append({
                    "text": m.group(1).strip(),
                    "category": current_h2,
                    "subcategory": current_h3,
                })
    return items


def doc_preview(content: str, max_chars: int = 300) -> str:
    """Strip markdown syntax and return a plain text preview."""
    text = re.sub(r"^#+\s+", "", content, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def gemini(prompt: str) -> str:
    if not _model:
        raise ValueError("GEMINI_API_KEY not configured")
    resp = _model.generate_content(prompt)
    text_out = resp.text.strip()
    if text_out.startswith("```"):
        text_out = re.sub(r"^```[a-z]*\n?", "", text_out)
        text_out = re.sub(r"\n?```$", "", text_out)
    return text_out


# ─── cache ─────────────────────────────────────────────────

_ai_cache: dict = {}
_cache_ttl = 3600


def get_cached(key: str):
    entry = _ai_cache.get(key)
    if entry and time.time() - entry["ts"] < _cache_ttl:
        return entry["data"]
    return None


def set_cached(key: str, data):
    _ai_cache[key] = {"data": data, "ts": time.time()}


# ─── routes ────────────────────────────────────────────────

@app.get("/api/notes")
def get_notes():
    text = load_notes()
    sections = parse_sections(text)
    items = extract_all_items(text)
    return {"sections": sections, "items": items, "raw": text}


@app.get("/api/library")
def get_library():
    """Return all documents with metadata and preview."""
    docs = load_all_docs()
    result = []
    for d in docs:
        first_heading = ""
        m = re.search(r"^#+ (.+)", d["content"], re.MULTILINE)
        if m:
            first_heading = m.group(1)
        mtime = Path(d["path"]).stat().st_mtime if Path(d["path"]).exists() else 0
        result.append({
            "name": d["name"],
            "label": d["label"],
            "folder": d["folder"],
            "title": first_heading or d["name"].replace(".md", ""),
            "preview": doc_preview(d["content"]),
            "size": len(d["content"]),
            "mtime": mtime,
        })
    return {"docs": result, "total": len(result)}


@app.get("/api/stats")
def get_stats():
    """Return knowledge base statistics."""
    docs = load_all_docs()
    total_words = sum(len(d["content"].split()) for d in docs)
    notes_text = next((d["content"] for d in docs if d["folder"] == "root"), "")
    notes_items = len(extract_all_items(notes_text))
    folder_counts: dict = {}
    for d in docs:
        label = d["label"]
        folder_counts[label] = folder_counts.get(label, 0) + 1
    return {
        "total_docs": len(docs),
        "total_words": total_words,
        "notes_items": notes_items,
        "folder_counts": folder_counts,
    }


@app.get("/api/doc")
def get_doc(folder: str, name: str):
    """Return full content of a specific document."""
    if folder == "root":
        path = DATA_DIR / name
    else:
        path = DATA_DIR / folder / name
    if not path.exists() or not path.is_relative_to(DATA_DIR):
        from fastapi import HTTPException
        raise HTTPException(404, "Document not found")
    return {
        "name": name,
        "folder": folder,
        "content": path.read_text(encoding="utf-8"),
    }


@app.get("/api/summary")
def get_summary():
    cached = get_cached("summary")
    if cached:
        return cached

    docs = load_all_docs()
    if not docs:
        return {"summary": "No documents found.", "topics": []}

    # Summarize notes.md + titles of other docs
    notes_text = next((d["content"] for d in docs if d["folder"] == "root"), "")
    other_titles = [d["title"] for d in docs if d["folder"] != "root"]

    try:
        prompt = f"""以下是個人知識庫的內容概覽。請用繁體中文輸出：
1. 一段 3-4 句的整體摘要（說明這個知識庫記錄了什麼）
2. 主要主題列表

個人筆記（notes.md）：
{notes_text[:2000]}

其他儲存的文件（{len(other_titles)} 份）：
{chr(10).join(f'- {t}' for t in other_titles[:20])}

只回覆以下 JSON 格式，不要加任何其他文字：
{{"summary": "...", "topics": ["主題1", "主題2", ...]}}"""
        result = json.loads(gemini(prompt))
    except Exception as e:
        result = {"summary": f"AI 摘要暫時無法使用：{e}", "topics": []}

    set_cached("summary", result)
    return result


@app.get("/api/categorize")
def get_categories():
    cached = get_cached("categorize")
    if cached:
        return cached

    # notes.md bullet items
    text = load_notes()
    note_items = extract_all_items(text)
    note_items_text = "\n".join([f"- [筆記/{i['category']}] {i['text']}" for i in note_items[:50]])

    # document titles from all sub-folders
    docs = load_all_docs()
    doc_items = []
    for d in docs:
        if d["folder"] == "root":
            continue
        m = re.search(r"^#+ (.+)", d["content"], re.MULTILINE)
        title = m.group(1) if m else d["name"].replace(".md", "")
        doc_items.append({
            "label": d["label"],
            "folder": d["folder"],
            "name": d["name"],
            "title": title,
        })
    doc_items_text = "\n".join([f"- [{d['label']}] {d['title']}" for d in doc_items])

    all_items_text = note_items_text
    if doc_items_text:
        all_items_text += "\n" + doc_items_text

    if not all_items_text.strip():
        return {"categories": []}

    try:
        prompt = f"""以下是個人知識庫的所有項目（包含筆記條目和已儲存的文件）。
請用繁體中文將它們重新歸類，每個類別給一個清晰名稱和表情符號。

項目清單：
{all_items_text}

只回覆以下 JSON 格式，不要加任何其他文字：
{{"categories": [{{"name": "類別名稱", "emoji": "🔧", "items": [{{"text": "項目文字", "type": "note或doc", "folder": "資料夾或空", "name": "檔名或空"}}]}}]}}"""
        result = json.loads(gemini(prompt))
    except Exception as e:
        # fallback: notes sections + docs as separate categories
        sections = parse_sections(text)
        cats = [{"name": s["title"], "emoji": "📌",
                 "items": [{"text": i, "type": "note", "folder": "", "name": ""} for i in s["items"]]}
                for s in sections if s["items"]]
        if doc_items:
            folder_groups: dict = {}
            for d in doc_items:
                folder_groups.setdefault(d["label"], []).append(
                    {"text": d["title"], "type": "doc", "folder": d["folder"], "name": d["name"]}
                )
            for label, items in folder_groups.items():
                cats.append({"name": label, "emoji": "📄", "items": items})
        result = {"categories": cats}

    # ensure items are always dicts
    for cat in result.get("categories", []):
        normalized = []
        for item in cat.get("items", []):
            if isinstance(item, str):
                normalized.append({"text": item, "type": "note", "folder": "", "name": ""})
            else:
                normalized.append(item)
        cat["items"] = normalized

    # inject doc metadata for items AI may have matched
    doc_map = {d["title"]: d for d in doc_items}
    for cat in result.get("categories", []):
        for item in cat.get("items", []):
            if item.get("type") == "doc" and not item.get("folder"):
                match = doc_map.get(item["text"])
                if match:
                    item["folder"] = match["folder"]
                    item["name"] = match["name"]

    set_cached("categorize", result)
    return result


@app.get("/api/doc-summary")
def get_doc_summary(folder: str, name: str):
    """AI summary of a specific document."""
    cache_key = f"doc_summary_{folder}_{name}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    if folder == "root":
        path = DATA_DIR / name
    else:
        path = DATA_DIR / folder / name

    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(404)

    content = path.read_text(encoding="utf-8")
    try:
        prompt = f"""請用繁體中文為以下文件生成簡潔摘要（3-5 句話）：

{content[:3000]}

只回覆 JSON 格式：{{"summary": "..."}}"""
        result = json.loads(gemini(prompt))
    except Exception as e:
        result = {"summary": f"無法生成摘要：{e}"}

    set_cached(cache_key, result)
    return result


@app.get("/api/search")
def search(q: str = ""):
    if not q:
        return {"results": []}

    q_lower = q.lower()
    results = []

    # search notes.md items
    text = load_notes()
    items = extract_all_items(text)
    for i in items:
        if q_lower in i["text"].lower() or q_lower in i["category"].lower():
            results.append({**i, "source": "notes.md", "type": "note"})

    # search all docs content
    docs = load_all_docs()
    for d in docs:
        if d["folder"] == "root":
            continue
        if q_lower in d["content"].lower() or q_lower in d["name"].lower():
            # find matching lines
            lines = [l.strip() for l in d["content"].splitlines()
                     if q_lower in l.lower() and l.strip()][:3]
            results.append({
                "text": " | ".join(lines) if lines else d["name"],
                "category": d["label"],
                "subcategory": d["name"],
                "source": d["name"],
                "type": "document",
            })

    return {"results": results[:30]}


@app.get("/api/health")
def health():
    docs = load_all_docs()
    return {"status": "ok", "notes_exists": NOTES_FILE.exists(), "total_docs": len(docs)}


# ─── static frontend ───────────────────────────────────────

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
