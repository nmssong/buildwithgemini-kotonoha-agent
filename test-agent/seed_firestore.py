#!/usr/bin/env python3
"""Seed script for Japanese Webnovel & Light Novel Translation Agent Firestore backend.

Hardcodes the GCP project ID string to prevent Agent Platform project number mismatch.
"""
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-f382b3dbe525"
COLLECTION_NAME = "ln_glossary"

SEEDED_ITEMS = [
    {
        "series_id": "slime_taiketsu",
        "term_jp": "リムル＝テンペスト",
        "term_en": "Rimuru Tempest",
        "category": "character",
        "honorific_pref": "none",
        "notes": "Main protagonist. Former human Satoru Mikami. Reincarnated as a slime."
    },
    {
        "series_id": "slime_taiketsu",
        "term_jp": "大賢者",
        "term_en": "Great Sage",
        "category": "skill",
        "honorific_pref": "n/a",
        "notes": "Unique Skill. Distinct emotionless, analytical system voice."
    },
    {
        "series_id": "slime_taiketsu",
        "term_jp": "ジュラ・テンペスト連邦国",
        "term_en": "Jura Tempest Federation",
        "category": "location",
        "honorific_pref": "n/a",
        "notes": "Monster nation founded in the Great Jura Forest."
    },
    {
        "series_id": "roshidere",
        "term_jp": "アリサ・ミハイロヴナ・九条",
        "term_en": "Alisa Mikhailovna Kujou",
        "category": "character",
        "honorific_pref": "preserve (-san / Alya-san)",
        "notes": "Nicknamed 'Alya' (アーリャ). Russian-Japanese silver-haired high schooler."
    },
    {
        "series_id": "roshidere",
        "term_jp": "久世政近",
        "term_en": "Masachika Kuze",
        "category": "character",
        "honorific_pref": "preserve (-kun)",
        "notes": "Male protagonist. Secretly understands Russian natively."
    },
    {
        "series_id": "mushoku_tensei",
        "term_jp": "無詠唱魔術",
        "term_en": "Silent Spellcasting (Incantation-less Magic)",
        "category": "magic_concept",
        "honorific_pref": "n/a",
        "notes": "Rare ability to manipulate mana directly without vocal incantations."
    }
]


def seed():
    print(f"Connecting to Firestore with hardcoded project ID: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in SEEDED_ITEMS:
        doc_id = f"{item['series_id']}_{item['term_jp']}"
        collection.document(doc_id).set(item)
        print(f"Seeded [{item['category']}] {item['term_jp']} -> {item['term_en']}")

    print(f"\nSuccessfully seeded {len(SEEDED_ITEMS)} glossary entries into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
