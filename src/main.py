import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai as genai_sdk

BASE_PATH = os.environ.get("BASE_PATH", "mind-vault").strip("/")
root_path = f"/{BASE_PATH}" if BASE_PATH else ""

app = FastAPI(title="MindVault", root_path=root_path)

DATA_DIR = Path(__file__).parent.parent / "data"
NOTES_FILE = DATA_DIR / "notes.md"
WIKI_DIR = DATA_DIR / "wiki"

# Sub-folders to scan
SUBFOLDERS = {
    "articles": "📰 文章",
    "saves": "💾 儲存",
    "conversations": "💬 對話記錄",
}

_gemini_key = os.environ.get("GEMINI_API_KEY", "")
_client = genai_sdk.Client(api_key=_gemini_key) if _gemini_key else None

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
    if not _client:
        raise ValueError("GEMINI_API_KEY not configured")
    resp = _client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
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
    other_titles = []
    for d in docs:
        if d["folder"] == "root":
            continue
        m = re.search(r"^#+ (.+)", d["content"], re.MULTILINE)
        other_titles.append(m.group(1) if m else d["name"].replace(".md", ""))

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


# ─── wiki helpers ───────────────────────────────────────────

def wiki_ensure_dirs():
    (WIKI_DIR / "summaries").mkdir(parents=True, exist_ok=True)
    (WIKI_DIR / "pages").mkdir(parents=True, exist_ok=True)


def wiki_append_log(entry: str):
    log_path = WIKI_DIR / "log.md"
    if not log_path.exists():
        log_path.write_text("# Wiki Log\n\n", encoding="utf-8")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def wiki_rebuild_index():
    timestamp = datetime.now().isoformat(timespec="seconds")
    summaries_dir = WIKI_DIR / "summaries"
    pages_dir = WIKI_DIR / "pages"
    summaries = sorted(summaries_dir.glob("*.md")) if summaries_dir.exists() else []
    pages = sorted(pages_dir.glob("*.md")) if pages_dir.exists() else []

    lines = [f"# Wiki Index\n_Last updated: {timestamp}_\n\n## Pages\n",
             "| slug | title | type | updated |",
             "|------|-------|------|---------|"]

    for p in summaries:
        first = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
        mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
        lines.append(f"| {p.stem} | {first} | summary | {mtime} |")

    for p in pages:
        first = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
        mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
        lines.append(f"| {p.stem} | {first} | concept | {mtime} |")

    (WIKI_DIR / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def wiki_parse_index() -> list[dict]:
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        return []
    rows = []
    in_table = False
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| slug"):
            in_table = True
            continue
        if line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 4:
                rows.append({"slug": parts[0], "title": parts[1],
                              "type": parts[2], "updated": parts[3]})
        elif in_table:
            break
    return rows


# ─── wiki routes ────────────────────────────────────────────

@app.get("/api/wiki/status")
def wiki_status():
    summaries_dir = WIKI_DIR / "summaries"
    pages_dir = WIKI_DIR / "pages"
    summaries = list(summaries_dir.glob("*.md")) if summaries_dir.exists() else []
    pages = list(pages_dir.glob("*.md")) if pages_dir.exists() else []
    ingested_slugs = {p.stem for p in summaries}

    docs = load_all_docs()
    pending = [
        {"folder": d["folder"], "name": d["name"], "slug": d["name"].replace(".md", "")}
        for d in docs
        if d["folder"] != "root" and d["name"].replace(".md", "") not in ingested_slugs
    ]

    return {
        "wiki_exists": WIKI_DIR.exists(),
        "total_summaries": len(summaries),
        "total_pages": len(pages),
        "pending_ingest": pending,
        "pending_count": len(pending),
    }


@app.get("/api/wiki/pages")
def wiki_list_pages():
    return {"pages": wiki_parse_index()}


@app.get("/api/wiki/page")
def wiki_get_page(slug: str, type: str = "summary"):
    if type == "summary":
        path = WIKI_DIR / "summaries" / f"{slug}.md"
    else:
        path = WIKI_DIR / "pages" / f"{slug}.md"
    if not path.exists() or not path.is_relative_to(WIKI_DIR):
        from fastapi import HTTPException
        raise HTTPException(404, "Wiki page not found")
    content = path.read_text(encoding="utf-8")
    return {"slug": slug, "type": type, "content": content}


@app.get("/api/wiki/log")
def wiki_get_log():
    log_path = WIKI_DIR / "log.md"
    if not log_path.exists():
        return {"log": "", "entries": 0}
    content = log_path.read_text(encoding="utf-8")
    entries = content.count("\n## ")
    return {"log": content, "entries": entries}


class IngestRequest(BaseModel):
    folder: str
    name: str
    force: bool = False


def _do_ingest(folder: str, name: str, force: bool = False) -> dict:
    """Core ingest logic — shared by single and batch endpoints."""
    if folder == "root":
        path = DATA_DIR / name
    else:
        path = DATA_DIR / folder / name

    if not path.exists() or not path.is_relative_to(DATA_DIR):
        return {"status": "error", "reason": "not found", "slug": name.replace(".md", "")}

    slug = name.replace(".md", "")
    wiki_ensure_dirs()
    summary_path = WIKI_DIR / "summaries" / f"{slug}.md"

    if summary_path.exists() and not force:
        return {"status": "skipped", "reason": "already ingested", "slug": slug}

    content = path.read_text(encoding="utf-8")
    m = re.search(r"^#+ (.+)", content, re.MULTILINE)
    title = m.group(1) if m else name.replace(".md", "")
    timestamp = datetime.now().isoformat(timespec="seconds")
    word_count = len(content.split())

    prompt = f"""你正在建立個人知識 Wiki。請為以下文件生成一個 Wiki 摘要頁面。

用繁體中文，嚴格按照以下結構輸出（不要加任何其他文字、不要用 code fence）：

## 這是什麼
（1 段話：這份文件在講什麼）

## 重點整理
- （重點 1）
- （重點 2）
- （最多 8 個重點）

## 涉及概念
（逗號分隔的概念名稱，例如：Claude Code、prompt engineering、AI 工具）

## 值得保存的段落
> （從原文直接引用一段最有價值的文字）

文件標題：{title}
文件內容：
{content[:4000]}"""

    try:
        body = gemini(prompt)
    except Exception as e:
        return {"status": "error", "reason": str(e), "slug": slug}

    # Extract concepts from response for log
    concepts = ""
    for line in body.splitlines():
        if line.startswith("## 涉及概念"):
            continue
        if concepts == "" and "## 涉及概念" in "".join(body.splitlines()[:body.splitlines().index(line) if line in body.splitlines() else 0]):
            concepts = line.strip()
            break

    header = f"""# {title}

> 來源：`{folder}/{name}`
> 匯入時間：{timestamp}
> 字數：{word_count}

"""
    summary_path.write_text(header + body + "\n\n---\n_由 MindVault Wiki 生成_\n", encoding="utf-8")

    log_entry = f"""
## {timestamp} — ingest
- 來源：{folder}/{name}
- 動作：{'更新' if summary_path.exists() else '建立'}摘要頁
- 頁面：wiki/summaries/{slug}.md

"""
    wiki_append_log(log_entry)
    wiki_rebuild_index()

    return {"status": "ok", "slug": slug, "title": title}


@app.post("/api/wiki/ingest")
def wiki_ingest(req: IngestRequest):
    return _do_ingest(req.folder, req.name, req.force)


@app.post("/api/wiki/ingest-all")
def wiki_ingest_all():
    docs = load_all_docs()
    summaries_dir = WIKI_DIR / "summaries"
    ingested_slugs = {p.stem for p in summaries_dir.glob("*.md")} if summaries_dir.exists() else set()
    pending = [d for d in docs if d["folder"] != "root" and d["name"].replace(".md", "") not in ingested_slugs]

    results = {"ingested": [], "skipped": [], "errors": []}
    for d in pending:
        r = _do_ingest(d["folder"], d["name"])
        if r["status"] == "ok":
            results["ingested"].append(r["slug"])
        elif r["status"] == "skipped":
            results["skipped"].append(r["slug"])
        else:
            results["errors"].append({"slug": r["slug"], "reason": r.get("reason", "")})

    return results


def _extract_concepts_from_summary(content: str) -> list[str]:
    """Parse the '## 涉及概念' section from a summary page."""
    lines = content.splitlines()
    in_concepts = False
    for line in lines:
        if "涉及概念" in line and line.startswith("##"):
            in_concepts = True
            continue
        if in_concepts:
            if line.startswith("##"):
                break
            if line.strip():
                # Split by comma or Chinese comma
                raw = re.split(r"[,，、]", line.strip())
                return [c.strip().lstrip("-• ").strip() for c in raw if c.strip()]
    return []


def _concept_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\u4e00-\u9fff\-]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "concept"


@app.post("/api/wiki/synthesize")
def wiki_synthesize(force: bool = False):
    """Extract concepts from all summaries and generate cross-document concept pages."""
    summaries_dir = WIKI_DIR / "summaries"
    if not summaries_dir.exists():
        return {"status": "error", "reason": "No summaries found. Run ingest first."}

    summary_files = list(summaries_dir.glob("*.md"))
    if not summary_files:
        return {"status": "error", "reason": "No summaries found. Run ingest first."}

    wiki_ensure_dirs()

    # Step 1: Extract concepts from every summary
    concept_sources: dict[str, list[dict]] = {}  # concept_name -> list of {slug, title, excerpt}
    for sf in summary_files:
        content = sf.read_text(encoding="utf-8")
        concepts = _extract_concepts_from_summary(content)
        title_m = re.search(r"^#+ (.+)", content, re.MULTILINE)
        title = title_m.group(1).replace(" — Summary", "").replace(" — 摘要", "").strip() if title_m else sf.stem
        # Grab a short excerpt (first non-header, non-metadata line)
        excerpt = ""
        for line in content.splitlines():
            if line.startswith(">") or line.startswith("#") or not line.strip():
                continue
            excerpt = line.strip()[:200]
            break
        for c in concepts:
            if c:
                concept_sources.setdefault(c, []).append({"slug": sf.stem, "title": title, "excerpt": excerpt})

    # Step 2: Only synthesize concepts appearing in 2+ summaries
    multi_source = {c: srcs for c, srcs in concept_sources.items() if len(srcs) >= 2}

    if not multi_source:
        # If no cross-doc concepts, still create single-source concept pages for rich concepts
        multi_source = {c: srcs for c, srcs in concept_sources.items() if len(srcs) >= 1}

    pages_dir = WIKI_DIR / "pages"
    existing_slugs = {p.stem for p in pages_dir.glob("*.md")} if pages_dir.exists() else set()

    created = []
    skipped = []
    errors = []

    timestamp = datetime.now().isoformat(timespec="seconds")

    for concept_name, sources in multi_source.items():
        slug = _concept_slug(concept_name)
        page_path = pages_dir / f"{slug}.md"

        if page_path.exists() and not force:
            skipped.append(slug)
            continue

        # Build context for Gemini
        sources_text = "\n\n".join([
            f"### 來自《{s['title']}》\n{s['excerpt']}"
            for s in sources[:5]  # cap at 5 sources
        ])

        prompt = f"""你正在建立個人知識 Wiki。請為以下概念生成一個跨文件的綜合概念頁面。

概念名稱：{concept_name}

這個概念出現在以下 {len(sources)} 份文件中：
{sources_text}

用繁體中文，嚴格按照以下結構輸出（不要加任何其他文字、不要用 code fence）：

## 定義
（2-3 句話說明這個概念是什麼）

## 在知識庫中的意義
（這個概念對這個知識庫的主人有什麼具體意義？結合上面的文件內容說明）

## 出現在以下文件
{chr(10).join(f'- [[{s["slug"]}]]（{s["title"]}）' for s in sources)}

## 相關延伸
（提出 2-3 個值得進一步探討的問題或方向）"""

        try:
            body = gemini(prompt)
        except Exception as e:
            errors.append({"slug": slug, "reason": str(e)})
            continue

        header = f"""# {concept_name}

> 類型：概念頁
> 最後更新：{timestamp}
> 出現在 {len(sources)} 份文件

"""
        page_path.write_text(header + body + "\n\n---\n_由 MindVault Wiki 合成_\n", encoding="utf-8")

        wiki_append_log(f"""
## {timestamp} — synthesize
- 概念：{concept_name}
- 來源文件數：{len(sources)}
- 頁面：wiki/pages/{slug}.md

""")
        created.append({"slug": slug, "concept": concept_name, "sources": len(sources)})

    wiki_rebuild_index()

    return {
        "status": "ok",
        "total_concepts_found": len(concept_sources),
        "synthesized": len(created),
        "skipped": len(skipped),
        "errors": errors,
        "pages": created,
    }


# ─── static frontend ───────────────────────────────────────

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
