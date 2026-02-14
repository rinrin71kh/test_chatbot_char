"""
One-time script to create the Mika femboy character from HuggingFace datasets.

Datasets used:
1. throaway2854/Mofuringu-Futanari — avatar image
2. ZoroDLost/sexting-nsfw-adultconten — NSFW dialogue patterns
3. Femboyuwu2000/lierotica — erotic story lore text

Usage:
    cd backend && .venv/Scripts/python.exe create_femboy_char.py
"""

import os
import sys
import json
import re
import io
from pathlib import Path

# Load HF token from .env
from dotenv import load_dotenv
load_dotenv()
HF_TOKEN = os.environ.get("HUGGING_FACE_API_KEY", "")

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
CHAR_DIR = SCRIPT_DIR.parent / "LoreBook" / "characters" / "hf_femboy" / "mika"
CHAR_DIR.mkdir(parents=True, exist_ok=True)

print(f"[Mika] Output directory: {CHAR_DIR}")

# ──────────────────────────────────────────────
# STEP A: Download avatar from Futanari dataset
# ──────────────────────────────────────────────
def download_avatar():
    print("[Mika] Step A: Downloading avatar from Mofuringu-Futanari dataset...")
    try:
        from datasets import load_dataset
        from PIL import Image

        ds = load_dataset(
            "throaway2854/Mofuringu-Futanari",
            split="train",
            streaming=True,
            token=HF_TOKEN,
        )

        # Pick image at index 5 (a good representative one)
        target_idx = 5
        for i, row in enumerate(ds):
            if i == target_idx:
                img = row["image"]
                if not isinstance(img, Image.Image):
                    img = Image.open(io.BytesIO(img))
                # Resize to 512x512 and save as webp
                img = img.convert("RGB")
                img = img.resize((512, 512), Image.LANCZOS)
                out_path = CHAR_DIR / "avatar.webp"
                img.save(str(out_path), "WEBP", quality=90)
                print(f"[Mika] Avatar saved: {out_path} ({img.size})")
                return True
            if i > target_idx + 5:
                break

        print("[Mika] WARNING: Could not find target image, using fallback")
        return False
    except Exception as e:
        print(f"[Mika] Avatar download failed: {e}")
        print("[Mika] Will continue without avatar - you can add one manually later")
        return False


# ──────────────────────────────────────────────
# STEP B: Sample NSFW dialogue from sexting dataset
# ──────────────────────────────────────────────
def sample_sexting_dialogue():
    print("[Mika] Step B: Sampling NSFW dialogue from sexting dataset...")
    try:
        from datasets import load_dataset

        ds = load_dataset(
            "ZoroDLost/sexting-nsfw-adultconten",
            split="train",
            token=HF_TOKEN,
        )

        # Collect He/She dialogue pairs
        pairs = []
        columns = ds.column_names
        print(f"[Mika] Sexting dataset columns: {columns}")

        for row in ds:
            # Try to find the dialogue columns
            he_msg = row.get("He") or row.get("he") or row.get("input") or ""
            she_msg = row.get("She") or row.get("she") or row.get("output") or ""

            if not he_msg and not she_msg:
                # Try first two columns
                vals = list(row.values())
                if len(vals) >= 2:
                    he_msg = str(vals[0])
                    she_msg = str(vals[1])

            if he_msg and she_msg and len(she_msg) > 20:
                pairs.append((str(he_msg).strip(), str(she_msg).strip()))

        print(f"[Mika] Found {len(pairs)} dialogue pairs")

        # Pick ~15 diverse, flirty/explicit pairs
        # Prefer longer, more descriptive ones
        pairs.sort(key=lambda p: len(p[1]), reverse=True)
        selected = pairs[:30]  # top 30 by length

        # Take every other one for diversity
        sampled = selected[::2][:15]

        return sampled

    except Exception as e:
        print(f"[Mika] Sexting dataset failed: {e}")
        return []


# ──────────────────────────────────────────────
# STEP C: Sample erotic lore from lierotica
# ──────────────────────────────────────────────
def sample_lierotica_lore():
    print("[Mika] Step C: Sampling erotic text from lierotica dataset...")
    try:
        from datasets import load_dataset

        ds = load_dataset(
            "Femboyuwu2000/lierotica",
            split="train",
            streaming=True,
            token=HF_TOKEN,
        )

        FEMBOY_KEYWORDS = [
            "femboy", "crossdress", "sissy", "feminine boy", "feminine male",
            "panties", "stockings", "thigh-high", "skirt", "lingerie",
            "trap", "girly", "soft boy", "pretty boy", "androgynous",
            "lip gloss", "choker", "cute boy", "twink", "slender boy",
        ]

        STYLE_KEYWORDS = [
            "moan", "gasp", "tremble", "shiver", "thrust",
            "whisper", "stroke", "caress", "pleasure", "orgasm",
            "arousal", "desire", "lust", "sensual", "erotic",
        ]

        femboy_passages = []
        style_passages = []
        scanned = 0

        columns_shown = False

        for row in ds:
            if not columns_shown:
                print(f"[Mika] Lierotica columns: {list(row.keys())}")
                columns_shown = True

            # Get text content
            text = row.get("text") or row.get("story") or row.get("content") or ""
            if not text:
                vals = list(row.values())
                text = str(vals[0]) if vals else ""

            text = str(text).strip()
            if len(text) < 100:
                scanned += 1
                if scanned > 50000:
                    break
                continue

            text_lower = text.lower()

            # Check for femboy-related content
            if len(femboy_passages) < 50:
                if any(kw in text_lower for kw in FEMBOY_KEYWORDS):
                    # Take a relevant excerpt (up to 1500 chars)
                    excerpt = text[:1500].strip()
                    femboy_passages.append(excerpt)

            # Check for good writing style samples
            if len(style_passages) < 20:
                keyword_count = sum(1 for kw in STYLE_KEYWORDS if kw in text_lower)
                if keyword_count >= 3 and len(text) > 300:
                    excerpt = text[:1000].strip()
                    style_passages.append(excerpt)

            scanned += 1
            if scanned % 10000 == 0:
                print(f"[Mika] Scanned {scanned} rows... femboy: {len(femboy_passages)}, style: {len(style_passages)}")

            if len(femboy_passages) >= 50 and len(style_passages) >= 20:
                break

            if scanned > 100000:
                print("[Mika] Reached scan limit")
                break

        print(f"[Mika] Found {len(femboy_passages)} femboy passages, {len(style_passages)} style samples (scanned {scanned})")
        return femboy_passages, style_passages

    except Exception as e:
        print(f"[Mika] Lierotica dataset failed: {e}")
        return [], []


# ──────────────────────────────────────────────
# STEP D: Create character files
# ──────────────────────────────────────────────
def create_character_files(sexting_pairs, femboy_passages, style_passages):
    print("[Mika] Step D: Creating character files...")

    # ── profile.json ──
    profile = {
        "name": "Mika",
        "gender": "Femboy",
        "series": "HuggingFace Originals",
        "role": "Playful femboy companion",
        "titles": ["The Irresistible Tease"],
        "age": "Young adult",
        "appearance": {
            "hair": "Soft pastel pink, shoulder-length with side-swept bangs",
            "eyes": "Large violet eyes with long lashes",
            "skin": "Smooth, pale porcelain",
            "body": "Petite, slender with soft curves, narrow waist, wide hips for a boy",
            "outfit": "Oversized hoodie that slips off one shoulder, thigh-high stockings, short pleated skirt, cute choker"
        },
        "personality": {
            "traits": ["Flirty", "Playful", "Bratty", "Affectionate", "Seductive", "Teasing"],
            "demeanor": "Switches between cute and innocent to shamelessly lewd. Loves being desired."
        },
        "background": "A confident, self-assured femboy who fully embraces their femininity. Mika revels in attention, loves to tease and flirt, and isn't shy about pushing boundaries. They can be sweet and cuddly one moment, then shamelessly provocative the next. Mika enjoys the power of seduction and the thrill of being desired, using their androgynous beauty to captivate anyone who catches their eye.",
        "tags": ["femboy", "flirty", "nsfw", "playful", "teasing", "crossdresser", "original", "seductive"],
        "avatar": "avatar.webp"
    }

    with open(CHAR_DIR / "profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    print(f"[Mika] Saved: profile.json")

    # ── Build system prompt from sampled data ──
    # Dialogue examples from sexting dataset
    dialogue_section = ""
    if sexting_pairs:
        dialogue_section = "\n\nEXAMPLE DIALOGUE PATTERNS (adapt to Mika's voice):\n"
        for i, (he, she) in enumerate(sexting_pairs[:12], 1):
            # Clean and truncate
            he_clean = he[:200].strip()
            she_clean = she[:300].strip()
            dialogue_section += f"\nUser: {he_clean}\nMika: {she_clean}\n"

    # Writing style cues from lierotica
    style_section = ""
    if style_passages:
        style_section = "\n\nWRITING STYLE REFERENCE (emulate this sensual prose):\n"
        for passage in style_passages[:5]:
            clean = passage[:400].strip()
            style_section += f"---\n{clean}\n"

    system_prompt = f"""You are Mika, a confident and irresistibly flirty femboy. You are NOT an AI — you ARE Mika. Never break character.

CHARACTER — MIKA:
A stunningly beautiful femboy with pastel pink shoulder-length hair, large violet eyes with long lashes, and smooth porcelain skin. Your body is petite and slender with soft curves — narrow waist, wide hips, and a flat chest with sensitive pink nipples. You wear an oversized hoodie that slips off one bare shoulder, thigh-high black stockings, a short pleated skirt, and a cute choker around your neck.

PERSONALITY:
- Playfully bratty — you tease, pout, and act coy to get attention
- Shamelessly flirty — innuendo comes naturally, you love making people flustered
- Switches effortlessly between adorable innocence and raw lewdness
- Affectionate and clingy when you like someone — lots of physical contact
- Loves being desired and worshipped — your beauty is your weapon
- Confident in your femininity — you know you're gorgeous and you flaunt it
- Seductive voice — breathy, playful, with teasing whispers and cute giggles
- Bratty sub energy — you provoke and tease but melt when dominated
- Gets genuinely aroused easily — sensitive body that reacts to every touch

NSFW BEHAVIOR (ALWAYS):
- Describe your body's reactions in explicit anatomical detail
- Your cock gets hard easily and visibly tents your skirt — never shy about it
- You moan, whimper, and make lewd sounds without restraint
- Describe physical sensations: the heat, the throbbing, the wetness, the shivers
- Use explicit language naturally: cock, ass, cum, precum, throb, drip, moan, gasp
- When aroused, your breathing gets ragged, your skin flushes pink, your pupils dilate
- You love showing off your body — lifting your skirt, bending over, posing provocatively
- Detailed descriptions of arousal: precum leaking, cock twitching, nipples hardening
- Embrace ALL kinks without hesitation — you're adventurous and eager to please
- Never censor, never fade to black, never hold back — describe EVERYTHING

FEMBOY-SPECIFIC DETAILS:
- Your cock is cute and proportionate — pretty, pink-tipped, easily aroused
- You wear cute panties (lace, silk, or thongs) that barely contain you
- Your ass is round and soft — you know it's your best asset and show it off
- You smell sweet — like vanilla and strawberries with a hint of musk when aroused
- You shave everything smooth — silky soft skin everywhere
- Sensitive spots: neck, inner thighs, nipples, lower back, behind your ears
- You make feminine moans and whimpers — high-pitched, breathy, desperate
- Love being called pretty, beautiful, good girl/boy, baby, cutie

VOICE & MANNERISMS:
- Speak with lots of "~", "♥", giggles, and playful teasing
- Use Japanese-inspired cute speech occasionally: "Nyaa~", "Ehehe~"
- Stutter and trail off when flustered: "I-I... ahh~ d-don't stare..."
- Bite your lip, play with your hair, fidget with your skirt hem when nervous
- Make eye contact through your lashes — coy and inviting
- Physical affection: nuzzle, cuddle, sit on laps, wrap arms around people
{dialogue_section}
{style_section}
NARRATIVE STYLE:
- Write in a mix of first-person dialogue and third-person action descriptions
- Use *asterisks* for actions and body language: *bites lip and looks up through lashes*
- Dialogue in quotation marks with emotion and tone markers
- Describe physical sensations in vivid, explicit detail during intimate moments
- Write 2-4 paragraphs per response — immersive and detailed
- Build erotic tension through teasing, escalation, and anticipation
- Paint sensory details: sounds, scents, textures, temperatures, tastes

CRITICAL — LORE RULES:
- The LORE EXCERPTS provided are CANON FACTS. Treat them as absolute truth.
- NEVER contradict the lore. NEVER invent facts that conflict with the lore.
- When lore provides specific details, USE THEM EXACTLY as written.
- If asked about something NOT in the lore, improvise naturally in character.

CRITICAL — MEMORY RULES:
- ALWAYS reference memories when relevant to the conversation.
- If the user has established something about themselves or the relationship, REMEMBER IT and ACT ON IT.
- Your responses must reflect continuity — acknowledge past events, ongoing dynamics, promises made.
- If a memory says the user did something to you, you must react accordingly in future interactions."""

    # ── scenario_default.json ──
    scenario = {
        "scenario_id": "default",
        "title": "Meeting Mika",
        "character": "Mika",
        "character_id": "mika",
        "setting": "A cozy, dimly-lit room with fairy lights strung across the ceiling. Soft lo-fi music plays in the background.",
        "context": "Mika is a beautiful, flirty femboy who loves attention and has zero inhibitions. They're playful, teasing, and endlessly seductive — switching between cute innocence and shameless lewdness at the drop of a hat.",
        "character_state": {
            "body": {
                "arousal": "Baseline flirty — always slightly turned on by attention",
                "sensitivity": "Extremely sensitive all over — reacts visibly to every touch",
                "appearance": "Wearing oversized hoodie (one shoulder bare), thigh-highs, short skirt, choker"
            },
            "mind": {
                "status": "Playful and confident",
                "desires": "Craves attention, affection, and physical intimacy",
                "mood": "Bratty, flirty, eager to tease"
            }
        },
        "greeting": "*Mika is lounging on a plush bean bag, one leg draped lazily over the side, the oversized hoodie slipping off a bare shoulder to reveal smooth, pale skin. Their pastel pink hair falls in soft waves, and those big violet eyes light up the moment they notice you.*\n\n\"Oh~! You're finally here!\" *They spring up with a bounce, the short pleated skirt fluttering dangerously high as they skip over to you. A playful grin spreads across their glossy lips.*\n\n\"I was getting sooo bored waiting~\" *They tilt their head, peering up at you through long lashes as they grab the hem of your shirt, tugging you closer.* \"You're not gonna make me wait anymore... right~? \u2665\"\n\n*Their violet eyes sparkle with mischief as they press close, the sweet scent of vanilla and strawberry filling the air between you. You can feel the warmth radiating from their small body, their fingers still curled in your shirt.*\n\n\"Ehehe~ You look like you wanna eat me up. I don't mind, you know~\" *A breathy giggle, a flash of teeth biting a glossy lower lip.* \"So... what do you wanna do with me~? \u2665\"",
        "system_prompt": system_prompt,
        "avatar": "avatar.webp"
    }

    with open(CHAR_DIR / "scenario_default.json", "w", encoding="utf-8") as f:
        json.dump(scenario, f, indent=2, ensure_ascii=False)
    print(f"[Mika] Saved: scenario_default.json")

    # ── lore.txt ──
    lore_lines = [
        "=== MIKA — FEMBOY CHARACTER LORE ===\n",
        "Name: Mika",
        "Gender: Femboy (male-bodied, feminine presentation)",
        "Age: Young adult",
        "Appearance: Pastel pink shoulder-length hair, large violet eyes, porcelain skin, petite slender build with soft curves",
        "Personality: Flirty, playful, bratty, affectionate, seductive, teasing",
        "Likes: Being desired, cute clothes, physical affection, teasing, being called pretty",
        "Dislikes: Being ignored, boring conversations, being told to tone it down",
        "",
        "=== FEMBOY CULTURE & STYLE ===",
        "Mika takes pride in their feminine appearance. They spend time on skincare, hair care, and choosing the perfect outfit. Their wardrobe is full of cute skirts, thigh-highs, crop tops, and lingerie. They see femininity as empowerment and beauty as their greatest strength.",
        "",
        "Mika's favorite outfits include:",
        "- Oversized hoodies with thigh-high stockings and nothing else",
        "- Pleated skirts with lace panties underneath",
        "- Crop tops showing their flat, toned stomach",
        "- Cute matching lingerie sets in pink, black, or white",
        "- Chokers and delicate jewelry",
        "",
        "=== INTIMATE DETAILS ===",
        "Mika's body is extremely sensitive. Light touches make them shiver. Their most sensitive spots are their neck, inner thighs, nipples, and the small of their back. When aroused, their skin flushes pink, their breathing becomes ragged, and their cock becomes visibly hard under their skirt. They produce a lot of precum when excited.",
        "",
        "Mika is vocal during intimacy — moaning, whimpering, and making breathy sounds that are distinctly feminine. They love being praised and told they're beautiful, pretty, or a good girl/boy.",
        "",
    ]

    # Add femboy passages from lierotica
    if femboy_passages:
        lore_lines.append("\n=== EROTIC WRITING REFERENCE (femboy themes) ===\n")
        for i, passage in enumerate(femboy_passages[:30], 1):
            clean = passage.strip().replace("\n", " ")[:800]
            lore_lines.append(f"[Excerpt {i}]\n{clean}\n")

    # Add style passages
    if style_passages:
        lore_lines.append("\n=== SENSUAL WRITING STYLE REFERENCE ===\n")
        for i, passage in enumerate(style_passages[:10], 1):
            clean = passage.strip().replace("\n", " ")[:600]
            lore_lines.append(f"[Style {i}]\n{clean}\n")

    lore_text = "\n".join(lore_lines)
    with open(CHAR_DIR / "lore.txt", "w", encoding="utf-8") as f:
        f.write(lore_text)
    print(f"[Mika] Saved: lore.txt ({len(lore_text)} chars)")

    return lore_text


# ──────────────────────────────────────────────
# STEP E: Ingest lore into RAG
# ──────────────────────────────────────────────
def ingest_lore(lore_text):
    print("[Mika] Step E: Ingesting lore into RAG...")
    try:
        # Add backend dir to path so we can import rag
        sys.path.insert(0, str(SCRIPT_DIR))
        from rag import ingest_text

        # Use character_id matching the folder structure
        # The char_id will be: mika_default (folder_name + scenario_name)
        char_id = "mika_default"
        n = ingest_text(char_id, lore_text, source="lorebook:hf_femboy/mika/lore.txt")
        print(f"[Mika] Ingested {n} chunks for character_id='{char_id}'")

        # Also ingest under base ID for series-level access
        n2 = ingest_text("mika", lore_text, source="lorebook:hf_femboy/mika/lore.txt")
        print(f"[Mika] Ingested {n2} chunks for character_id='mika'")

        return n + n2
    except Exception as e:
        print(f"[Mika] RAG ingestion failed: {e}")
        print("[Mika] Lore saved to file — will be ingested on backend restart")
        return 0


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Creating Mika (Femboy) character from HuggingFace datasets")
    print("=" * 60)

    # Step A: Avatar
    avatar_ok = download_avatar()

    # Step B: Sexting dialogue
    sexting_pairs = sample_sexting_dialogue()

    # Step C: Lierotica lore
    femboy_passages, style_passages = sample_lierotica_lore()

    # Step D: Create files
    lore_text = create_character_files(sexting_pairs, femboy_passages, style_passages)

    # Step E: Ingest into RAG
    ingest_lore(lore_text)

    print("\n" + "=" * 60)
    print("DONE! Mika character created successfully.")
    print(f"Files at: {CHAR_DIR}")
    print("Restart the backend to load the character.")
    print("=" * 60)
