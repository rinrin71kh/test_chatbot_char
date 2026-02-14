"""
Ingest bluuwhale/nsfwstory dataset into RAG to improve NSFW writing quality
across all characters.

Strategy:
- Scan stories for category keywords (femboy, dominant, submissive, futa, etc.)
- Extract the best explicit passages (not full stories — they're ~30K chars each)
- Ingest categorized excerpts under each relevant character_id
- Also ingest a general "nsfw_style" corpus available to all characters

Usage:
    cd backend && .venv/Scripts/python.exe ingest_nsfwstory.py
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()
HF_TOKEN = os.environ.get("HUGGING_FACE_API_KEY", "")

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from rag import ingest_text

# ── Category keyword maps ──
# Each category maps to keywords that identify relevant stories,
# and a list of character_ids that should receive those excerpts.
CATEGORIES = {
    "femboy": {
        "keywords": ["femboy", "crossdress", "sissy", "trap", "feminine boy",
                      "panties on him", "his skirt", "pretty boy", "girly boy",
                      "stockings", "thigh-high", "femme", "androgynous"],
        "char_ids": ["mika_default", "mika"],
    },
    "dominant": {
        "keywords": ["dominate", "dominant", "master", "mistress", "kneel",
                      "obey", "command", "slave", "submit", "collar",
                      "leash", "punish", "discipline", "worship"],
        "char_ids": [],  # will be auto-populated from loaded characters
    },
    "submissive": {
        "keywords": ["submissive", "obedient", "helpless", "beg", "please master",
                      "on my knees", "at her mercy", "at his mercy", "surrender",
                      "whimper", "tremble"],
        "char_ids": [],
    },
    "futa": {
        "keywords": ["futanari", "futa", "her cock", "her dick", "she thrust",
                      "girl with a cock", "hermaphrodite", "dickgirl"],
        "char_ids": [],
    },
    "explicit_general": {
        "keywords": ["moan", "orgasm", "cum", "thrust", "fuck", "cock",
                      "pussy", "dripping", "climax", "ecstasy"],
        "char_ids": [],  # general — ingested under nsfw_style
    },
}

# Passages we want to extract: find the most explicit/well-written sections
QUALITY_MARKERS = [
    "moan", "gasp", "tremble", "shiver", "thrust", "stroke", "caress",
    "pleasure", "orgasm", "climax", "ecstasy", "desire", "lust",
    "writhe", "arch", "clench", "pulse", "throb", "drip", "ache",
    "whimper", "pant", "scream", "beg", "deeper", "harder", "faster",
]


def extract_best_passages(story_text, max_passages=3, passage_len=1200):
    """Extract the most explicit/well-written passages from a story."""
    # Split into paragraphs
    paragraphs = [p.strip() for p in story_text.split("\n\n") if len(p.strip()) > 100]

    if not paragraphs:
        # Fallback: split by sentences
        paragraphs = [story_text[i:i+passage_len] for i in range(0, len(story_text), passage_len)]

    # Score each paragraph by quality markers
    scored = []
    for para in paragraphs:
        lower = para.lower()
        score = sum(1 for kw in QUALITY_MARKERS if kw in lower)
        # Bonus for longer, more descriptive passages
        if len(para) > 300:
            score += 2
        if len(para) > 600:
            score += 2
        scored.append((score, para))

    # Sort by score descending, take top passages
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, para in scored[:max_passages]:
        if score < 2:
            break  # not enough quality markers
        # Trim to passage_len
        text = para[:passage_len].strip()
        results.append(text)

    return results


def categorize_story(story_text):
    """Return list of category names that match this story."""
    lower = story_text.lower()
    matched = []
    for cat_name, cat_info in CATEGORIES.items():
        if any(kw in lower for kw in cat_info["keywords"]):
            matched.append(cat_name)
    return matched


def main():
    from datasets import load_dataset

    print("=" * 60)
    print("Ingesting bluuwhale/nsfwstory into RAG")
    print("=" * 60)

    # First, discover existing character_ids from the database
    try:
        from rag import _db
        conn = _db()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT character_id FROM chunks")
        existing_ids = {row[0] for row in cur.fetchall()}
        conn.close()
        print(f"[NSFW] Found {len(existing_ids)} existing character_ids in RAG: {existing_ids}")
    except Exception as e:
        print(f"[NSFW] Could not read existing IDs: {e}")
        existing_ids = set()

    # Auto-populate character_ids for categories based on existing characters
    for char_id in existing_ids:
        cid_lower = char_id.lower()
        # Dominant characters
        if any(kw in cid_lower for kw in ["ingrid", "mesu", "slave", "broken"]):
            CATEGORIES["dominant"]["char_ids"].append(char_id)
            CATEGORIES["submissive"]["char_ids"].append(char_id)
        # Futa characters
        if any(kw in cid_lower for kw in ["futa", "kirael", "kirara"]):
            CATEGORIES["futa"]["char_ids"].append(char_id)

    ds = load_dataset("bluuwhale/nsfwstory", split="train", streaming=True, token=HF_TOKEN)

    # Collect passages by category
    category_passages = defaultdict(list)
    general_passages = []

    TARGET_PER_CATEGORY = 60  # passages per category
    TARGET_GENERAL = 100      # general explicit writing samples
    MAX_SCAN = 2000           # max stories to scan

    scanned = 0
    matched = 0

    for row in ds:
        story = row.get("story", "")
        if len(story) < 500:
            scanned += 1
            continue

        categories = categorize_story(story)
        passages = extract_best_passages(story, max_passages=2, passage_len=1200)

        if passages:
            for cat in categories:
                if len(category_passages[cat]) < TARGET_PER_CATEGORY:
                    category_passages[cat].extend(passages)
                    matched += 1

            # Always collect for general if good quality
            if len(general_passages) < TARGET_GENERAL:
                general_passages.extend(passages[:1])

        scanned += 1
        if scanned % 200 == 0:
            cat_counts = {k: len(v) for k, v in category_passages.items()}
            print(f"[NSFW] Scanned {scanned}... matched {matched}, general: {len(general_passages)}, categories: {cat_counts}")

        # Check if we have enough
        all_full = all(
            len(category_passages.get(cat, [])) >= TARGET_PER_CATEGORY
            for cat in CATEGORIES
        ) and len(general_passages) >= TARGET_GENERAL

        if all_full or scanned >= MAX_SCAN:
            break

    print(f"\n[NSFW] Scan complete: {scanned} stories scanned")
    print(f"[NSFW] General passages: {len(general_passages)}")
    for cat, passages in category_passages.items():
        print(f"[NSFW] Category '{cat}': {len(passages)} passages")

    # ── Ingest into RAG ──
    total_chunks = 0

    # 1. Ingest general NSFW style corpus for ALL characters
    if general_passages:
        general_text = "\n\n=== NSFW WRITING STYLE REFERENCE ===\n\n" + "\n\n---\n\n".join(general_passages)
        print(f"\n[NSFW] Ingesting {len(general_passages)} general passages as 'nsfw_style'...")
        n = ingest_text("nsfw_style", general_text, source="dataset:bluuwhale/nsfwstory:general")
        total_chunks += n
        print(f"[NSFW] Ingested {n} chunks for 'nsfw_style'")

        # Also ingest general writing reference for ALL existing character IDs
        for char_id in existing_ids:
            # Only ingest a subset for each character to avoid bloating
            subset = general_passages[:20]
            subset_text = "\n\n---\n\n".join(subset)
            n = ingest_text(char_id, subset_text, source="dataset:bluuwhale/nsfwstory:style")
            total_chunks += n
            print(f"[NSFW] Ingested {n} style chunks for '{char_id}'")

    # 2. Ingest category-specific passages for matching characters
    for cat_name, passages in category_passages.items():
        if not passages:
            continue

        cat_info = CATEGORIES[cat_name]
        char_ids = cat_info.get("char_ids", [])

        if not char_ids:
            # If no specific chars, just ingest under category name
            cat_text = "\n\n---\n\n".join(passages)
            n = ingest_text(f"nsfw_{cat_name}", cat_text, source=f"dataset:bluuwhale/nsfwstory:{cat_name}")
            total_chunks += n
            print(f"[NSFW] Ingested {n} chunks for category 'nsfw_{cat_name}'")
        else:
            cat_text = "\n\n---\n\n".join(passages)
            for char_id in char_ids:
                n = ingest_text(char_id, cat_text, source=f"dataset:bluuwhale/nsfwstory:{cat_name}")
                total_chunks += n
                print(f"[NSFW] Ingested {n} chunks for '{char_id}' (category: {cat_name})")

    print(f"\n{'='*60}")
    print(f"DONE! Ingested {total_chunks} total chunks from nsfwstory dataset.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
