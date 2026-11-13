# My agent: Kotonoha (言の葉) - Light Novel & Webnovel Translation Agent

One-liner: A conversational agent that helps webnovel and light novel readers and translators translate Japanese chapters into fluent, nuanced English with a catalog of novels, chapters, and persistent glossaries.

Tool coverage:
- Memory: Remembers series-specific terminology (character names, honorific preferences, skill/magic names, kingdom/location names, pronouns/tones) and user stylistic translation preferences across sessions.
- Tools:
  - fetch_webnovel_chapter: Fetches raw Japanese text from a web novel URL (e.g., Syosetu/Kakuyomu) or accepts raw text.
  - query_glossary_and_style: Retrieves naming rules, character voice guides, and previously established translations from Firestore / long-term memory.
  - analyze_chapter_metadata: Scans Japanese text for characters, novel vocabulary, and scene breaks.
- Catalog/UI: Catalog of novels, chapters, translation history, and interactive character glossary cards rendered via A2UI.
- Image gen: n/a
- Sandbox: Chapter chunking, token/word count analysis, reading time estimation, and exporting translated chapters to formatted Markdown/EPUB.

Recommended for every project: memory, storage, tools, A2UI
Agent-specific / stretch (pick what fits):
- Vertex AI RAG Engine (using previous volume/chapter translations as reference context for few-shot translation consistency and author voice matching).
- Code sandbox for text chunking, alignment, and EPUB packaging.
