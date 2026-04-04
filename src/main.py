import os
import re
import json
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import google.generativeai as genai

BASE_PATH = os.environ.get("BASE_PATH", "mind-vault").strip("/")
root_path = f"/{BASE_PATH}" if BASE_PATH else ""

app = FastAPI(title="MindVault", root_path=root_path)

DATA_DIR = Path(__file__).parent.parent / "data"
NOTES_FILE = DATA_DIR / "notes.md"

_gemini_key = os.environ.get("GEMINI_API_KEY", "")
if _gemini_key:
    genai.configure(api_key=_gemini_key)
_model = genai.GenerativeModel("gemini-2.0-flash-lite") if _gemini_key else None

# ─── helpers ───────────────────────────────────────────────

def load_notes() -> str:
    if not NOTES_FILE.exists():
        return ""
    return NOTES_FILE.read_text(encoding="utf-8")


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
            # collect bullet items
            m = re.match(r"^[-*]\s+(.+)", line)
            if m:
                current["items"].append(m.group(1).strip())
    if current:
        sections.append(current)
    return sections


def extract_all_items(text: str) -> list[dict]:
    """Extract all bullet items with their parent heading context."""
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


# ─── cache ─────────────────────────────────────────────────

_ai_cache: dict = {}
_cache_ttl = 3600  # 1 hour


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


@app.get("/api/summary")
def get_summary():
    cached = get_cached("summary")
    if cached:
        return cached

    text = load_notes()
    if not text.strip():
        return {"summary": "No notes found."}

    try:
        if not _model:
            raise ValueError("GEMINI_API_KEY not configured")
        prompt = f"""以下是一份個人筆記文件。請用繁體中文輸出：
1. 一段 3-4 句的整體摘要
2. 主要主題列表（bullet points）

筆記內容：
{text}

只回覆以下 JSON 格式，不要加任何其他文字：
{{"summary": "...", "topics": ["主題1", "主題2", ...]}}"""
        resp = _model.generate_content(prompt)
        text_out = resp.text.strip()
        if text_out.startswith("```"):
            text_out = re.sub(r"^```[a-z]*\n?", "", text_out)
            text_out = re.sub(r"\n?```$", "", text_out)
        result = json.loads(text_out)
    except Exception as e:
        result = {"summary": f"AI 摘要暫時無法使用：{e}", "topics": []}

    set_cached("summary", result)
    return result


@app.get("/api/categorize")
def get_categories():
    cached = get_cached("categorize")
    if cached:
        return cached

    text = load_notes()
    items = extract_all_items(text)
    if not items:
        return {"categories": []}

    items_text = "\n".join([f"- [{i['category']}] {i['text']}" for i in items[:60]])

    try:
        if not _model:
            raise ValueError("GEMINI_API_KEY not configured")
        prompt = f"""以下是一系列筆記項目，格式為 [分類] 內容。
請用繁體中文重新整理，輸出 JSON 格式：將相似主題的項目歸類，給每個類別一個清晰的名稱和表情符號。

筆記項目：
{items_text}

只回覆以下 JSON 格式，不要加任何其他文字：
{{"categories": [{{"name": "類別名稱", "emoji": "🔧", "items": ["項目1", "項目2"]}}]}}"""
        resp = _model.generate_content(prompt)
        text_out = resp.text.strip()
        if text_out.startswith("```"):
            text_out = re.sub(r"^```[a-z]*\n?", "", text_out)
            text_out = re.sub(r"\n?```$", "", text_out)
        result = json.loads(text_out)
    except Exception as e:
        # fallback: use raw sections
        sections = parse_sections(text)
        result = {"categories": [
            {"name": s["title"], "emoji": "📌", "items": s["items"]}
            for s in sections if s["items"]
        ]}

    set_cached("categorize", result)
    return result


@app.get("/api/search")
def search(q: str = ""):
    if not q:
        return {"results": []}
    text = load_notes()
    items = extract_all_items(text)
    q_lower = q.lower()
    results = [i for i in items if q_lower in i["text"].lower()
               or q_lower in i["category"].lower()
               or q_lower in i["subcategory"].lower()]
    return {"results": results[:30]}


@app.get("/api/health")
def health():
    return {"status": "ok", "notes_exists": NOTES_FILE.exists()}


# ─── static frontend ───────────────────────────────────────

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
