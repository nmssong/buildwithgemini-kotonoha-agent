# Kotonoha (言の葉) - User & Translator Guide

Welcome to **Kotonoha (言の葉)**, an AI agent crafted specifically for webnovel and light novel readers, editors, and translators. 

This guide covers everything you can do with Kotonoha, including supported workflows, example prompts, tool behaviors, and how to get the most natural translations preserving character voice.

---

## 🌟 Core Capabilities Overview

| Feature | Description | Underlying Tool / Tech |
| :--- | :--- | :--- |
| **🌐 Webnovel Chapter Scraping** | Extract clean Japanese novel text and chapter metadata from web URLs. | `fetch_webnovel_chapter` (Syosetu & Kakuyomu) |
| **📊 Chapter Linguistic Metrics** | Inspect raw character counts, dialogue vs. narration ratios, and honorific distributions. | `analyze_chapter_metadata` |
| **📚 Multi-Series Glossary** | Register, lookup, and manage character names, skills, and terminology. | `save_glossary_term`, `get_glossary_term`, `list_glossary_terms` (Firestore) |
| **💬 Nuanced Dialogue Translation** | Translate Japanese prose into fluid English while respecting specific character voices. | Gemini 2.5 LLM + A2UI Cards |
| **☁️ Markdown Archiving & Export** | Export completed translations directly to Cloud Storage with permanent shareable links. | `export_translated_chapter` (Google Cloud Storage) |
| **🧠 Memory & Tone Adaptation** | Remembers user translation preferences across sessions. | Vertex AI Memory Bank |

---

## 🚀 How to Use Kotonoha

You can interact with Kotonoha through either:
1. **The Custom Dialogue Web UI** (`http://localhost:8080`)
2. **The ADK Web Playground** (`uv run adk web . --port 8080 --reload_agents`)

---

## 📖 Workflows & Example Prompts

### 1. Fetching & Analyzing a Webnovel Chapter
Kotonoha can scrape chapters directly from **Syosetu (`ncode.syosetu.com`)** and **Kakuyomu (`kakuyomu.jp`)**, strip out site ads and HTML boilerplates, and analyze the difficulty and metrics before translation.

**Example Prompts:**
- *"Fetch and analyze chapter from Syosetu: https://ncode.syosetu.com/n6316bn/1/"*
- *"Can you inspect this Kakuyomu chapter and tell me the dialogue-to-narration ratio? https://kakuyomu.jp/works/1177354054880205594/episodes/1177354054880205694"*

---

### 2. Managing Series Glossaries
To prevent character names and magic terminology from changing between chapters, Kotonoha uses a persistent Firestore database categorized by series slug (e.g. `slime_taiketsu`, `roshidere`, `mushoku_tensei`).

#### A. Viewing Terms
- *"Show me all glossary terms for slime_taiketsu"*
- *"List all registered characters in the slime_taiketsu glossary"*

#### B. Adding or Updating Terms
- *"Add a glossary term for series 'slime_taiketsu': Japanese 'リムル＝テンペスト', English 'Rimuru Tempest', category 'character', honorific preference 'preserve', notes 'Main protagonist, friendly and relaxed slime leader.'"*
- *"Register a magic skill: '黒炎獄' -> 'Black Flame Prison' (Hell Flare) for slime_taiketsu under category 'skill'."*

#### C. Looking Up Terms
- *"How do we translate 'ミリム・ナーヴァ' in slime_taiketsu?"*

---

### 3. Translating Prose & Preserving Character Voice
Kotonoha is attuned to Japanese light novel nuance, including Tsundere speech patterns, Chuunibyou phrasing, Kansai dialect, honorific suffixes (`-sama`, `-san`, `-dono`, `-kun`, `-chan`), and sentence-ending particles (`のだ`, `わよ`, `ぜ`).

**Example Prompts:**
- *"Translate this dialogue preserving character voice: 「お前、本当にバカだな……でも、助けてくれてありがとう、リムル様」"*
- *"Translate this fight scene. Make the narration punchy and keep Japanese honorifics intact: 「魔王クレイマン、貴様の企みはここまでだ！」"*
- *"Translate this chapter with a side-by-side Japanese and English comparison."*

---

### 4. Exporting Translations for Readers
Once a chapter translation is refined, Kotonoha can compile it into a formatted Markdown document and upload it to Google Cloud Storage.

**Example Prompts:**
- *"Export our translation of Slime Taiketsu Chapter 1 to Cloud Storage with title 'The Encounter in the Cave'."*
- *"Compile the translated chapter into Markdown and give me the public download link."*

---

## 🎨 Dialogue UI Tips

If using the **Custom Dialogue UI**:
- **Prompt Chips**: Click the pill buttons right above the input bar for instant 1-click test actions.
- **A2UI Rich Cards**: For complex responses (such as welcome dashboards or structured glossary lists), Kotonoha renders interactive card components instead of plain text.
- **Continuous Turns**: Kotonoha retains your conversation state across turns. You can say *"Make the last paragraph more dramatic"* or *"Rephrase line 4 to be more informal"* without re-pasting the text.

---

## 💡 Best Practices for Translators

1. **Seed Your Terms Early**: Before translating Chapter 1 of a novel, register the main characters in the glossary. Kotonoha will check the glossary before generating prose.
2. **Specify Tone Rules**: You can tell Kotonoha:
   - *"Keep Japanese honorifics (-sama, -dono)"* or *"Localize into English equivalents (Lord, Lady)"*.
   - *"Translate sound effects (SFX) as italicized descriptions like (rumble) or (thud)"*.
3. **Memory Bank Persistence**: If you repeatedly request a specific translation rule (e.g. *"always keep Japanese honorifics"*), Vertex AI Memory Bank will store this preference and apply it automatically to future sessions!
