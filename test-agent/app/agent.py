# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import Any, Dict, List, Optional
from google.cloud import firestore

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

try:
    from .a2ui_prompt import INSTRUCTION as instruction
except ImportError:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )
    instruction = schema_manager.generate_system_prompt(
        role_description="You are Kotonoha (言の葉), an expert Japanese Light Novel and Webnovel translation agent.",
        include_schema=True,
        include_examples=True,
    )
from .a2ui_utils import a2ui_callback


MODEL = "gemini-3.8-flash"
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-f382b3dbe525"
COLLECTION_NAME = "ln_glossary"

# Initialize Firestore client with hardcoded project ID
db = firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_glossary_terms(series_id: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List translation glossary terms from Firestore, optionally filtered by series or category.

    Args:
        series_id: Optional series identifier (e.g. 'slime_taiketsu', 'roshidere', 'mushoku_tensei').
        category: Optional category filter ('character', 'skill', 'location', 'magic_concept').

    Returns:
        A list of glossary term dictionaries containing term_jp, term_en, category, notes, and honorific preferences.
    """
    col_ref = db.collection(COLLECTION_NAME)
    query = col_ref
    if series_id:
        query = query.where("series_id", "==", series_id)
    if category:
        query = query.where("category", "==", category)

    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_glossary_term(term_jp: str, series_id: Optional[str] = None) -> Dict[str, Any]:
    """Look up an existing translation and translation notes for a specific Japanese term.

    Args:
        term_jp: The Japanese name, skill, or terminology to look up.
        series_id: Optional series identifier to narrow down the search.

    Returns:
        The matching glossary entry dictionary, or a message indicating the term is not yet registered.
    """
    col_ref = db.collection(COLLECTION_NAME)
    if series_id:
        doc_ref = col_ref.document(f"{series_id}_{term_jp}")
        doc = doc_ref.get()
        if doc.exists:
            res = doc.to_dict()
            res["id"] = doc.id
            return res

    # Fallback to query by term_jp across collections
    query = col_ref.where("term_jp", "==", term_jp)
    matches = [d.to_dict() for d in query.stream()]
    if matches:
        return matches[0]

    return {"status": "not_found", "message": f"No glossary entry found for term: {term_jp}"}


def save_glossary_term(
    term_jp: str,
    term_en: str,
    series_id: str,
    category: str = "character",
    honorific_pref: str = "preserve",
    notes: str = ""
) -> Dict[str, Any]:
    """Add or update a translation glossary term in Firestore.

    Args:
        term_jp: The Japanese name, word, or phrase (e.g., 'ミリム・ナーヴァ').
        term_en: Established English translation (e.g., 'Milim Nava').
        series_id: Identifier for the series (e.g., 'slime_taiketsu').
        category: 'character', 'skill', 'location', 'magic_concept', or 'item'.
        honorific_pref: Style rule, such as 'preserve' (-san, -kun), 'localize', or 'none'.
        notes: Context, character traits, tone notes, or explanation for translators.

    Returns:
        Confirmation dictionary with the saved term details.
    """
    col_ref = db.collection(COLLECTION_NAME)
    doc_id = f"{series_id}_{term_jp}"
    entry = {
        "series_id": series_id,
        "term_jp": term_jp,
        "term_en": term_en,
        "category": category,
        "honorific_pref": honorific_pref,
        "notes": notes,
    }
    col_ref.document(doc_id).set(entry)
    return {"status": "success", "id": doc_id, "data": entry}


import urllib.request
from bs4 import BeautifulSoup


def fetch_webnovel_chapter(url: str) -> Dict[str, Any]:
    """Fetch and extract raw Japanese text and metadata from a webnovel chapter URL.

    Supports Syosetu (Shousetsuka ni Narou - ncode.syosetu.com), Kakuyomu (kakuyomu.jp),
    and general web pages.

    Args:
        url: The webnovel chapter URL (e.g. 'https://ncode.syosetu.com/n6316bn/1/').

    Returns:
        A dictionary containing chapter title, series title, character count, and the raw Japanese text.
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch URL: {str(e)}"}

    soup = BeautifulSoup(html, "html.parser")

    chapter_title = ""
    series_title = ""
    content_text = ""

    # Syosetu (Shousetsuka ni Narou) parsing
    if "syosetu.com" in url:
        title_elem = soup.select_one(".p-novel__title, .novel_subtitle")
        if title_elem:
            chapter_title = title_elem.get_text(strip=True)

        series_elem = soup.select_one(".p-novel__series-title, .novel_title")
        if series_elem:
            series_title = series_elem.get_text(strip=True)

        body_elem = soup.select_one(".p-novel__body, #novel_honbun")
        if body_elem:
            # Preserve paragraph breaks
            paragraphs = [p.get_text() for p in body_elem.select("p")]
            content_text = "\n".join(paragraphs) if paragraphs else body_elem.get_text()

    # Kakuyomu parsing
    elif "kakuyomu.jp" in url:
        title_elem = soup.select_one(".widget-episodeTitle, header h1")
        if title_elem:
            chapter_title = title_elem.get_text(strip=True)

        body_elem = soup.select_one(".widget-episodeBody, .js-episode-body")
        if body_elem:
            paragraphs = [p.get_text() for p in body_elem.select("p")]
            content_text = "\n".join(paragraphs) if paragraphs else body_elem.get_text()

    # Generic fallback
    if not content_text:
        article = soup.select_one("article, main, .content, #content")
        if article:
            content_text = article.get_text(separator="\n", strip=True)
        else:
            content_text = soup.get_text(separator="\n", strip=True)

    char_count = len(content_text.replace("\n", "").replace(" ", "").replace("　", ""))

    return {
        "status": "success",
        "url": url,
        "chapter_title": chapter_title or "Untitled Chapter",
        "series_title": series_title or "Webnovel",
        "character_count": char_count,
        "raw_japanese_text": content_text.strip(),
    }


import re
from google.cloud import storage

BUCKET_NAME = "kotonoha-novels-qwiklabs-gcp-04-f382b3dbe525"
storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)


def analyze_chapter_metadata(text: str) -> Dict[str, Any]:
    """Analyze Japanese raw text or novel chapter for translation planning and stylistic metrics.

    Computes character count, dialogue percentage, estimated English word count,
    token estimate, and detects recurring honorifics and speech indicators.

    Args:
        text: The raw Japanese chapter text to analyze.

    Returns:
        A dictionary with linguistic metrics, dialogue vs narration ratios,
        detected honorifics, and estimated translation effort.
    """
    clean_text = text.replace(" ", "").replace("　", "").replace("\r", "")
    char_count = len(clean_text.replace("\n", ""))
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    total_lines = len(lines)

    # Dialogue lines typically start with Japanese quotation marks 「 or 『
    dialogue_lines = [l for l in lines if l.startswith("「") or l.startswith("『") or l.startswith("【")]
    dialogue_ratio = round((len(dialogue_lines) / total_lines * 100), 1) if total_lines > 0 else 0.0

    # Common honorifics and sentence-final tone markers
    honorifics_found = {}
    for h in ["様", "さま", "さん", "君", "くん", "ちゃん", "殿", "どの", "先輩", "先生"]:
        cnt = clean_text.count(h)
        if cnt > 0:
            honorifics_found[h] = cnt

    # Token and English word estimations
    est_input_tokens = int(char_count * 1.2) + 200
    est_english_words = int(char_count * 0.45)
    est_reading_time_mins = round(est_english_words / 220, 1)

    return {
        "status": "success",
        "japanese_char_count": char_count,
        "total_lines": total_lines,
        "dialogue_lines_count": len(dialogue_lines),
        "dialogue_percentage": f"{dialogue_ratio}%",
        "narrative_percentage": f"{round(100.0 - dialogue_ratio, 1)}%",
        "detected_honorifics": honorifics_found,
        "estimated_english_words": est_english_words,
        "estimated_reading_time_minutes": est_reading_time_mins,
        "estimated_input_tokens": est_input_tokens,
    }


def export_translated_chapter(
    series_id: str,
    chapter_num: int,
    chapter_title: str,
    english_translation: str,
    raw_japanese: Optional[str] = None
) -> Dict[str, Any]:
    """Export a completed English translation (Markdown format) to Google Cloud Storage.

    Uploads the translated chapter to the public project bucket, providing a permanent
    shareable URL for offline reading, archiving, or publishing.

    Args:
        series_id: Slug or name of the novel series (e.g., 'slime_taiketsu', 'roshidere').
        chapter_num: Chapter number (e.g., 1, 2).
        chapter_title: Title of the chapter in English or bilingual.
        english_translation: The translated English prose content.
        raw_japanese: Optional raw Japanese text to include as side-by-side reference.

    Returns:
        A dictionary containing the Cloud Storage destination path and public download URL.
    """
    safe_series = re.sub(r'[^a-zA-Z0-9_\-]', '_', series_id)
    filename = f"{safe_series}/chapter_{chapter_num:03d}.md"

    # Assemble formatted Markdown document
    doc_lines = [
        f"# {series_id.replace('_', ' ').title()}",
        f"## Chapter {chapter_num}: {chapter_title}",
        "",
        "---",
        "",
        "### English Translation",
        "",
        english_translation,
        "",
    ]

    if raw_japanese:
        doc_lines.extend([
            "---",
            "",
            "### Original Japanese Text",
            "",
            raw_japanese,
            "",
        ])

    content = "\n".join(doc_lines)

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(content, content_type="text/markdown; charset=utf-8")
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "bucket": BUCKET_NAME,
            "filename": filename,
            "public_url": public_url,
            "bytes_written": len(content.encode("utf-8")),
            "message": f"Chapter successfully exported to Cloud Storage: {public_url}"
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to upload to Cloud Storage: {str(e)}"}


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


SANDBOX_RESOURCE_NAME = (
    "projects/99258717776/locations/us-central1/reasoningEngines/2563191677153968128/sandboxEnvironments/795246248922710016"
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        fetch_webnovel_chapter,
        analyze_chapter_metadata,
        list_glossary_terms,
        get_glossary_term,
        save_glossary_term,
        export_translated_chapter,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)



