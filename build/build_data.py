"""Turn the upstream dumps into the data blocks inside `hind.html`.

Python for data, never for serving: this runs on a laptop when a source changes,
and its product is committed. Nothing here executes at page load.

What the output *means*, since that is the part worth stating:

  · A Hindi word's **stratum** decides which drill may use it. तद्भव and
    Perso-Arabic words are the ones a Hindi speaker already knows by ear, so a
    miss in the timed decode drill is evidence the script slowed them down.
    तत्सम words are the written-register vocabulary a speaker often does *not*
    know, so those are drilled untimed and a miss means the word is unknown.
    Mixing the two would produce one number that measures neither.

  · A stratum is only ever **copied from Wiktionary's etymology templates**,
    never guessed from the shape of a word. Half of Hindi Wiktionary carries no
    etymology at all; those words are dictionary-only and enter no drill. A
    plausible guess here would quietly poison the one distinction the app is
    built on.

  · A Sanskrit **level is a grammar level** — which stem classes and paradigms
    you can parse — because no CEFR-graded, redistributable Sanskrit word list
    exists to borrow a lexical ladder from. Ranking by corpus frequency would
    have produced a ladder that looks like the Mandarin and Russian apps and
    measures the wrong thing: a hard Sanskrit word is usually a common word in a
    case form you cannot resolve.

Run:
    python3 -m venv build/.venv
    build/.venv/bin/python build/build_data.py
"""
from __future__ import annotations

import bz2
import collections
import json
import pathlib
import re
import sys
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "sources"
APP = HERE.parent / "hind.html"

# --- classification ---------------------------------------------------------

# Wiktionary's donor-language codes, grouped into the strata the drills need.
# `fa-cls` is Classical Persian and is the code that actually appears — plain
# `fa` is rare enough to be a rounding error, and missing it drops 2,300 words.
SANSKRIT_SRC = {"sa"}
PRAKRIT_SRC = {"pra", "pra-sau", "pra-pro", "psu", "inc-ohi", "inc-ash"}
PERSO_ARABIC_SRC = {"fa", "fa-cls", "ar", "ota", "pal"}
EUROPEAN_SRC = {"en", "pt", "fr", "nl", "de"}

# Templates that assert a borrowing (learned or otherwise) versus inheritance.
# `lbor` is Wiktionary's explicit "learned borrowing" — the textbook definition
# of तत्सम. `bor`/`bor+` from Sanskrit is the same relationship recorded with a
# less specific template, so both count.
BORROW_TMPL = {"bor", "bor+", "lbor", "slbor", "der"}
INHERIT_TMPL = {"inh", "inh+"}

STRATA = ("tatsama", "tadbhava", "perso-arabic", "european")


def stratum_of(entry: dict) -> str | None:
    """The first classifying etymology template wins.

    Order matters: Wiktionary lists the immediate ancestor first, so a word
    inherited via Prakrit reads `inh pra` before any deeper `sa` cognate. Taking
    the first hit is what keeps घर (inherited, spoken) out of the तत्सम pool
    even though its ultimate source is Sanskrit गृह.
    """
    for t in entry.get("etymology_templates") or []:
        name = t.get("name") or ""
        src = str((t.get("args") or {}).get("2", ""))
        if name in BORROW_TMPL and src in SANSKRIT_SRC:
            return "tatsama"
        if name in INHERIT_TMPL and (src in SANSKRIT_SRC or src in PRAKRIT_SRC):
            return "tadbhava"
        if name in BORROW_TMPL and src in PERSO_ARABIC_SRC:
            return "perso-arabic"
        if name in BORROW_TMPL and src in EUROPEAN_SRC:
            return "european"
    return None


def sanskrit_source(entry: dict) -> str | None:
    """The Sanskrit headword a तत्सम word was borrowed from.

    This is the edge that makes one word graph out of two tracks: the Sanskrit
    card and the formal-Hindi card are the same lexeme seen from two sides.
    """
    for t in entry.get("etymology_templates") or []:
        args = t.get("args") or {}
        if (t.get("name") or "") in BORROW_TMPL and str(args.get("2", "")) in SANSKRIT_SRC:
            word = str(args.get("3", "")).strip()
            # Strip Wiktionary's inline qualifiers: "गृह<pos:...>" and bare markup.
            word = re.split(r"[<|]", word)[0].strip()
            if word and re.search(r"[ऀ-ॿ]", word):
                return word
    return None


def first_gloss(entry: dict, limit: int = 3) -> list[str]:
    out: list[str] = []
    for s in entry.get("senses") or []:
        for g in s.get("glosses") or []:
            g = g.strip()
            if g and g not in out:
                out.append(g)
            if len(out) >= limit:
                return out
    return out


def tagged_form(entry: dict, tag: str) -> str | None:
    for f in entry.get("forms") or []:
        if tag in (f.get("tags") or []):
            return f.get("form")
    return None


# --- readers ----------------------------------------------------------------


def read_jsonl(path: pathlib.Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def load_frequency() -> dict[str, int]:
    """Rank from the OpenSubtitles list.

    The file is named `hi_50k` and holds **2,968 lines** — a twelfth of what the
    name implies, because the Hindi OpenSubtitles corpus is small. It is still
    the right spine for the decode drill (those 2,968 are exactly the words a
    speaker hears daily), but it cannot rank the 35,653-word dictionary, so
    everything past it is stored rank-less and the app must not imply otherwise.
    """
    ranks: dict[str, int] = {}
    path = SRC / "hi_50k.txt"
    if not path.exists():
        return ranks
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        word = line.split(" ")[0].strip()
        if word and word not in ranks:
            ranks[word] = i + 1
    return ranks


def load_hindi_sentences(limit_per_word: int = 1) -> dict[str, tuple[str, str]]:
    """Hindi Tatoeba sentences paired to their English translation.

    16,475 Hindi sentences exist against 35,653 headwords, so most words get
    nothing. A word without a sentence renders an explicit empty slot rather
    than a shorter card — the same rule Inkstone applies to its imported words.
    """
    hin_path = SRC / "hin_sentences.tsv.bz2"
    eng_path = SRC / "eng_sentences.tsv.bz2"
    links_path = SRC / "links.tar.bz2"
    if not (hin_path.exists() and eng_path.exists() and links_path.exists()):
        print("  ! Tatoeba sources missing — sentences skipped")
        return {}

    hin: dict[int, str] = {}
    with bz2.open(hin_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                hin[int(parts[0])] = parts[2]

    wanted_eng: set[int] = set()
    pairs: dict[int, int] = {}
    with tarfile.open(links_path, "r:bz2") as tf:
        member = next((m for m in tf.getmembers() if m.name.endswith("links.csv")), None)
        if member is None:
            return {}
        fh = tf.extractfile(member)
        if fh is None:
            return {}
        for raw in fh:
            a, _, b = raw.decode("utf-8", "ignore").partition("\t")
            try:
                sid, tid = int(a), int(b.strip())
            except ValueError:
                continue
            if sid in hin and tid not in hin:
                pairs.setdefault(sid, tid)
                wanted_eng.add(tid)

    eng: dict[int, str] = {}
    with bz2.open(eng_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                sid = int(parts[0])
                if sid in wanted_eng:
                    eng[sid] = parts[2]

    # Index by word so a card can look up a sentence containing it.
    by_word: dict[str, tuple[str, str]] = {}
    for sid, text in hin.items():
        tid = pairs.get(sid)
        if tid is None or tid not in eng:
            continue
        for token in re.findall(r"[ऀ-ॿ]+", text):
            if token not in by_word:
                by_word[token] = (text, eng[tid])
    return by_word


# --- builders ---------------------------------------------------------------


def build_hindi(ranks, sentences):
    words: dict[str, dict] = {}
    counts = collections.Counter()

    # A headword can have entries in more than one stratum: काम is तत्सम in the
    # sense "desire, Kāma" and तद्भव in the sense "work" that every speaker uses
    # daily. Such a word cannot carry the claim either pool makes about it, so it
    # is dropped from both rather than filed under a coin-flip.
    seen_strata: dict[str, set[str]] = collections.defaultdict(set)
    for e in read_jsonl(SRC / "kaikki-hi.jsonl"):
        w = e.get("word")
        if not w or not re.fullmatch(r"[ऀ-ॿ‍\s]+", w):
            continue
        s = stratum_of(e)
        if s:
            seen_strata[w].add(s)
    ambiguous = {w for w, s in seen_strata.items() if len(s) > 1}

    for e in read_jsonl(SRC / "kaikki-hi.jsonl"):
        w = e.get("word")
        if not w or not re.fullmatch(r"[ऀ-ॿ‍\s]+", w):
            continue
        glosses = first_gloss(e)
        if not glosses:
            continue
        strat = stratum_of(e)
        rec = words.get(w)
        # One card per headword. Where a word has several parts of speech, the
        # entry carrying a stratum wins, then the one with more senses — the
        # same "more information wins" heuristic Filin uses, and it is a
        # heuristic, so the dictionary view must show what was picked.
        better = (
            rec is None
            or (strat and not rec.get("s"))
            or (bool(strat) == bool(rec.get("s")) and len(glosses) > len(rec.get("g", [])))
        )
        if not better:
            continue
        rec = {
            "w": w,
            "p": e.get("pos"),
            "g": glosses,
            "s": strat,
            "r": ranks.get(w),
            "ipa": (e.get("sounds") or [{}])[0].get("ipa") if e.get("sounds") else None,
            "lat": tagged_form(e, "romanization"),
            "sa": sanskrit_source(e) if strat == "tatsama" else None,
        }
        sent = sentences.get(w)
        if sent:
            rec["ex"] = [sent[0], sent[1]]
        words[w] = rec

    for r in words.values():
        counts[r["s"] or "unclassified"] += 1

    # Ship only what a drill can use. A word with no stratum cannot enter either
    # pool without a guess, and `european` words (टेबल, स्कूल) are already known
    # to any English speaker so they teach nothing in either drill. Keeping all
    # 35,044 headwords for a dictionary nobody asked for cost 4 MB of the page.
    keep = {
        w: r for w, r in words.items()
        if r["s"] in ("tatsama", "tadbhava", "perso-arabic") and w not in ambiguous
    }

    # Which pool a word belongs to is a claim about what the *learner* knows,
    # and etymology is only indirect evidence of that. Corpus frequency is
    # direct: a word in the 2,968-word everyday list is one you hear, whatever
    # its origin. Plenty of तत्सम words are completely ordinary speech — समय,
    # कारण, प्रश्न — and कर ranks #5 because the corpus cannot separate the
    # literary noun "hand" from the stem of करना.
    #
    # So a ranked तत्सम word is drilled as a decoding word, not as unknown
    # vocabulary. Its register is still recorded and still shown on the card;
    # only the pool changes, because "you would not say this" is false of it.
    moved = 0
    for r in keep.values():
        if r["s"] == "tatsama" and r["r"]:
            r["pool"] = "decode"
            moved += 1
        else:
            r["pool"] = "vocab" if r["s"] == "tatsama" else "decode"
    counts["ambiguous"] = len(ambiguous)
    counts["tatsama_everyday"] = moved
    return keep, counts


# Sanskrit stem classes, ordered into a ladder. Order is by how much of the
# corpus each class covers, so the ladder teaches the paradigm you will meet
# most often first. Counted from the dump, not chosen by taste.
def build_sanskrit():
    words: dict[str, dict] = {}
    class_counts = collections.Counter()

    for e in read_jsonl(SRC / "kaikki-sa.jsonl"):
        w = e.get("word")
        if not w or not re.search(r"[ऀ-ॿ]", w):
            continue
        glosses = first_gloss(e)
        if not glosses:
            continue
        stem = tagged_form(e, "class")
        tmpl = tagged_form(e, "inflection-template")

        # Store the paradigm, but only the cells a drill can ask about: the
        # eight cases across three numbers. Every cell is a form Wiktionary
        # published — nothing here is inflected by this script, because a
        # generated ending would be the app teaching an error.
        # One cell per case+number. Where Wiktionary lists several forms for a
        # slot they are variants (usually Vedic beside classical), not gender
        # columns — gender lives on the entry. The first is the primary form and
        # is what the drill asks for; the rest are recorded so the drill can
        # avoid offering two correct answers in one question, and can accept a
        # variant instead of marking a right answer wrong.
        primary: dict[tuple[int, int], str] = {}
        variants: list[list] = []
        for f in e.get("forms") or []:
            tags = f.get("tags") or []
            if not tags or "inflection-template" in tags or "class" in tags:
                continue
            case = next((t for t in tags if t in CASES), None)
            num = next((t for t in tags if t in NUMBERS), None)
            form = clean_form(f.get("form") or "")
            if not (case and num) or not form or form == "-":
                continue
            key = (CASES.index(case), NUMBERS.index(num))
            if key not in primary:
                primary[key] = form
            elif form != primary[key]:
                variants.append([key[0], key[1], form])

        forms = [[c, n, v] for (c, n), v in sorted(primary.items())]

        rec = words.get(w)
        if rec and len(rec.get("f", [])) >= len(forms) and rec.get("c"):
            continue
        words[w] = {
            "w": w,
            "p": e.get("pos"),
            "g": glosses,
            "c": stem,
            "t": tmpl,
            "gen": gender_of(e, tmpl),
            "lat": tagged_form(e, "romanization"),
            "f": forms,
            "fv": variants,
        }
        if stem:
            class_counts[stem] += 1

    ladder = [c for c, _ in class_counts.most_common()]
    return words, class_counts, ladder


# A full 24-cell paradigm costs roughly 700 bytes of page. Carrying all 6,536 of
# them made the file 14.6 MB — three times Filin and nine times Inkstone, for a
# page that has to parse before it can show a card.
PARADIGM_BUDGET = 1500
PER_CLASS_FLOOR = 60


def choose_paradigms(sa: dict, hindi_sources: set[str]) -> set[str]:
    """Pick which Sanskrit words keep their full case table.

    Priority is a word with a तत्सम descendant in Hindi: learning विश्व pays
    twice, because the same lexeme is sitting in the Hindi vocabulary drill.
    Every stem class then gets a floor of its own examples regardless, so no
    paradigm in the ladder is left without words to teach it — an `ṛ-stem` level
    with no ṛ-stems is a level that cannot be studied.
    """
    by_class: dict[str, list[str]] = collections.defaultdict(list)
    for w, r in sa.items():
        if r["f"] and r.get("c"):
            by_class[r["c"]].append(w)

    def rank(w: str) -> tuple:
        r = sa[w]
        return (0 if w in hindi_sources else 1, -len(r["f"]), w)

    chosen: set[str] = set()
    for cls, members in by_class.items():
        members.sort(key=rank)
        chosen.update(members[:PER_CLASS_FLOOR])

    remaining = sorted(
        (w for w in sa if sa[w]["f"] and w not in chosen), key=rank
    )
    for w in remaining:
        if len(chosen) >= PARADIGM_BUDGET:
            break
        chosen.add(w)
    return chosen


CASES = ["nominative", "accusative", "instrumental", "dative",
         "ablative", "genitive", "locative", "vocative"]
NUMBERS = ["singular", "dual", "plural"]
GENDERS = ["masculine", "feminine", "neuter"]

# Wiktionary marks a secondary form with a footnote reference appended straight
# to the glyphs: विश्वेभिः1 is the Vedic instrumental plural beside classical
# विश्वैः. The digit is apparatus, not Sanskrit, and shipping it would put a
# character into a form the language does not contain.
FOOTNOTE = re.compile(r"[0-9]+$")

# The declension template names the gender; a noun's gender is not optional
# information in Sanskrit, and the dump does not tag it on the cells.
TEMPLATE_GENDER = {
    "sa-decl-noun-m": "masculine",
    "sa-decl-noun-f": "feminine",
    "sa-decl-noun-n": "neuter",
}


def clean_form(raw: str) -> str:
    return FOOTNOTE.sub("", (raw or "").strip())


def gender_of(entry: dict, template: str | None) -> str | None:
    """Gender from the template name, falling back to the canonical form's tags."""
    if template in TEMPLATE_GENDER:
        return TEMPLATE_GENDER[template]
    for f in entry.get("forms") or []:
        tags = f.get("tags") or []
        if "canonical" in tags:
            for g in GENDERS:
                if g in tags:
                    return g
    return None


# --- splice -----------------------------------------------------------------


def splice(name: str, payload: str) -> None:
    """Rewrite one GENERATED block in hind.html, leaving everything else alone."""
    text = APP.read_text(encoding="utf-8")
    start = f"/* GENERATED:{name} */"
    end = f"/* END GENERATED:{name} */"
    i, j = text.find(start), text.find(end)
    if i < 0 or j < 0:
        raise SystemExit(f"marker for {name} not found in {APP.name}")
    text = text[: i + len(start)] + "\n" + payload + "\n" + text[j:]
    APP.write_text(text, encoding="utf-8")


def main() -> int:
    missing = [f for f in ("kaikki-hi.jsonl", "kaikki-sa.jsonl") if not (SRC / f).exists()]
    if missing:
        raise SystemExit(f"missing sources: {missing}. See build/sources/README.md")

    print("frequency list ...")
    ranks = load_frequency()
    print(f"  {len(ranks)} ranked words")

    print("Tatoeba sentences ...")
    sentences = load_hindi_sentences()
    print(f"  {len(sentences)} words carry a sentence")

    print("Hindi ...")
    hi, counts = build_hindi(ranks, sentences)
    # `ambiguous` overlaps the stratum buckets rather than adding to them.
    seen = sum(v for k, v in counts.items() if k not in ("ambiguous", "tatsama_everyday"))
    total = len(hi)
    print(f"  {seen} headwords in the dump; {total} shipped (the rest enter no drill)")
    for k in STRATA + ("unclassified",):
        print(f"    {k:14} {counts[k]:6}  {counts[k]/seen:5.1%}")
    print(f"    {'ambiguous':14} {counts['ambiguous']:6}  dropped from both pools (two strata)")
    print(f"    {'तत्सम everyday':14} {counts['tatsama_everyday']:6}  ranked, so drilled as decoding not vocabulary")
    linked = sum(1 for r in hi.values() if r.get("sa"))
    withex = sum(1 for r in hi.values() if r.get("ex"))
    print(f"  तत्सम linked to a Sanskrit headword: {linked}")
    print(f"  carrying an example sentence:        {withex} ({withex/total:.1%})")

    print("Sanskrit ...")
    sa, class_counts, ladder = build_sanskrit()
    with_forms = sum(1 for r in sa.values() if r["f"])
    print(f"  {len(sa)} headwords, {with_forms} with a case paradigm")
    print(f"  ladder: {ladder[:10]}")

    # Cross-track edge: how many तत्सम words actually resolve to a Sanskrit card
    hindi_sources = {r["sa"] for r in hi.values() if r.get("sa")}
    resolved = sum(1 for r in hi.values() if r.get("sa") and r["sa"] in sa)
    print(f"  तत्सम edges resolving to a real Sanskrit card: {resolved}")

    keep_forms = choose_paradigms(sa, hindi_sources)
    kept_linked = sum(1 for w in keep_forms if w in hindi_sources)
    for w, r in sa.items():
        if w not in keep_forms:
            r["f"] = []          # gloss-only card; still drillable for meaning
            r["fv"] = []
    print(f"  paradigms kept: {len(keep_forms)} of {with_forms} "
          f"({kept_linked} of them with a Hindi descendant)")
    gendered = sum(1 for w in keep_forms if sa[w].get("gen"))
    varcells = sum(len(sa[w]["fv"]) for w in keep_forms)
    print(f"  gender recorded on {gendered} of {len(keep_forms)} shipped paradigms")
    print(f"  variant forms preserved: {varcells} (Vedic/alternative, footnote digits stripped)")
    # A ladder rung needs enough worked examples to be studied. A stem class with
    # three words in it is a fact about those three words, not a level — the same
    # rule Filin applies to morphemes appearing in fewer than three words. Rare
    # classes stay on their cards; they just do not become a level of their own.
    covered = collections.Counter(sa[w]["c"] for w in keep_forms)
    LADDER_FLOOR = 10
    rare = [c for c in ladder if covered[c] < LADDER_FLOOR]
    ladder = [c for c in ladder if covered[c] >= LADDER_FLOOR]
    print(f"  ladder rungs: {len(ladder)} — {ladder}")
    print(f"  too rare to be a rung (kept on cards): {rare or 'none'}")

    blocks = {
        "HI": "const HI_WORDS = " + json.dumps(list(hi.values()), ensure_ascii=False, separators=(",", ":")) + ";",
        "SA": "const SA_WORDS = " + json.dumps(list(sa.values()), ensure_ascii=False, separators=(",", ":")) + ";",
        "META": "const DATA_META = " + json.dumps({
            "hi_total": total,
            "hi_strata": {k: counts[k] for k in STRATA},
            "hi_unclassified": counts["unclassified"],
            "hi_ambiguous": counts["ambiguous"],
            "hi_tatsama_everyday": counts["tatsama_everyday"],
            "hi_pools": {"decode": sum(1 for r in hi.values() if r["pool"] == "decode"),
                         "vocab": sum(1 for r in hi.values() if r["pool"] == "vocab")},
            "hi_ranked": len(ranks),
            "hi_with_example": withex,
            "sa_total": len(sa),
            "sa_with_forms": with_forms,          # paradigms available upstream
            "sa_paradigms": len(keep_forms),      # paradigms actually shipped
            "sa_paradigms_linked": kept_linked,
            "sa_ladder": ladder,
            "sa_class_counts": dict(class_counts.most_common()),
            "cross_edges": resolved,
            "cases": CASES,
            "numbers": NUMBERS,
        }, ensure_ascii=False, separators=(",", ":")) + ";",
    }
    for name, payload in blocks.items():
        splice(name, payload)
        print(f"  spliced {name}: {len(payload)/1024:.0f} KB")

    print(f"\n{APP.name} is now {APP.stat().st_size/1048576:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
