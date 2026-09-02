# Hind — Hindi script literacy and Sanskrit acquisition as one system

Written 2026-09-02, against an empty `hind/`. Greenfield: there is no code to
audit, so Part A audits the **data** instead — every source the design leans on,
checked by downloading and parsing it rather than by trusting its documentation.

**Method:** 25 MB of the kaikki.org Hindi dump pulled by range request and
parsed (4,474 entries, 3,718 unique headwords); 20 MB of the kaikki.org Sanskrit
dump likewise (1,676 entries, 1,072 headwords); HTTP checks on Tatoeba's Hindi
and Sanskrit exports and on four FrequencyWords paths; a Wikimedia Commons API
census of Devanagari stroke-order files. Every count below is measured from that
sample. Totals marked *extrapolated* are sample-scaled by file size and say so.

**Approved 2026-09-02.** A1 resolved in favour of formation rules and confusable
letter families; no stroke-order diagrams will be authored or shipped. Every
other finding stands as written. Build status is tracked against Part B; each
step notes its own outcome inline once it lands, and this document is otherwise
kept as written — the findings and the reasoning are the record of what was
decided and why.

---

## Part 0 — confirmed intent

Established by interview 2026-09-02 and confirmed explicitly. Recorded here
because the build's shape follows from it and the reasoning is worth keeping.

| | |
|---|---|
| **Outcome** | One offline app, MCQ throughout, holding Hindi and Sanskrit as two tracks over a shared Devanagari script module and a shared word graph |
| **User** | You — Hindi-fluent by ear, slow on the page, weak at writing; Sanskrit from zero |
| **Why now** | Two gaps a vocabulary SRS does not touch: decoding a script whose language you already speak, and the Sanskritised written register that speech never taught you |
| **Success — Hindi** | Three drills that each measure exactly one thing (below) |
| **Success — Sanskrit** | Full acquisition scale, levels defined by **grammar** — declension classes, verb classes, sandhi, compound types — not word frequency |
| **Constraint** | MCQ everywhere, no free-text or handwriting input. Single file, offline, `localStorage` with a versioned schema, no build step, both themes |
| **Out of scope** | Graded handwriting; passage-comprehension reading; speaking practice; any frequency-derived Sanskrit ladder |

The three Hindi drills, and what a failure in each one means:

| Drill | Timed? | Word pool | A wrong answer means |
|---|---|---|---|
| Script decoding | Yes, shrinking window | Words you know by ear | The letterforms failed you |
| Formal vocabulary | No | तत्सम / literary register | You don't know the word |
| Writing recognition | No | Conjuncts, matras, confusables | You would have formed it wrong |

Splitting these is the whole point. One mixed drill produces a single number
that cannot distinguish "I couldn't parse the glyphs" from "I don't know that
word", which are the two separate problems this app exists to tell apart.

---

## Part A — findings, ranked

### A1 · DESIGN RISK (high): the stroke-order reference has no data to stand on

The confirmed intent includes an ungraded stroke-order reference beside the
writing drill. **The data for it does not exist.** A Commons API search for
`intitle:"Devanagari" intitle:"stroke order"` in the File namespace returns
**13 files, total, covering 12 of the 44 core letters** — and it is the wrong
12: अ आ इ ई उ ऊ ऋ ए ऐ ओ औ and one more, i.e. the vowels. Every consonant is
missing: क ख ग घ ङ च छ ज झ ञ ट ठ ड ढ ण त थ द ध न प फ ब भ म य र ल व श ष स ह.
The `Category:Devanagari stroke order` listing returns zero members.

There is no Devanagari equivalent of Make Me a Hanzi or KanjiVG. Authoring the
missing 32 letters by hand is possible — it is a bounded set — but it would mean
**inventing stroke data and presenting it as reference**. That is the same
failure class Filin refused for Russian stress: a field the learner cannot check
for themselves, where a guess installs an error that takes years to unlearn.

**Fix:** ship **formation rules and letter families** instead of per-letter
stroke animations. Devanagari's formation is systematic in a way Chinese is not
— the शिरोरेखा headline is drawn last, most consonants are a vertical stem plus
a distinguishing left-side element, and the letters group into families that
differ by one stroke (ब/व, घ/ध, ख/रव, भ/म, प/ष, ट/ठ, ड/ढ, द/ढ). Teaching those
five or six rules plus the confusable families is checkable, needs no per-letter
data, and drills directly as MCQ — "which of these four is the correctly formed
घ" — which is the format already chosen.

This is the smallest correct fix because it requires **no new data source at
all**, and it targets the thing that actually goes wrong when you write
Devanagari badly, which is not stroke sequence but choosing the wrong member of
a letter family and misplacing matras.

**This one needs your call**, since it narrows something you explicitly asked
for. The alternative is that I hand-author 32 stroke diagrams and label the
whole reference as unverified.

### A2 · MODEL GAP (high) — resolved: "words you already know spoken" is machine-derivable

The interview left the decoding drill's word pool undefined. It cannot be "all
Hindi words", because then a wrong answer might mean you didn't know the word,
which is the exact confusion the split was meant to remove.

Wiktionary solves it. Hindi's vocabulary is three historical strata, and the
kaikki dump tags every one of them **structurally** — the etymology template
*name* is the classifier, so this is parsed, not regexed out of English prose:

| Stratum | Template | Sample count (of 3,718 headwords) | Know it by ear? |
|---|---|---|---|
| तद्भव — inherited, usually via Prakrit | `inh`, `inh+` | 638 (17%) | Yes — घर ← गृह, क्या ← किम्, पीना |
| Perso-Arabic — the Urdu-shared everyday layer | `bor` from `fa`/`ar` | 657 (18%) | Yes — नाम, करना, पलक |
| तत्सम — learned borrowing from Sanskrit | `lbor`, `bor` from `sa` | 974 (26%) | **No** — विश्व, समुद्र, संस्कृत |

2,406 etymology templates in the sample carry an `sa` language-code argument.
The decoding pool is तद्भव + Perso-Arabic; the vocabulary pool is तत्सम. And
because a तत्सम word *is* a Sanskrit word, one card serves both tracks — which
is the shared word graph, now with a precise definition rather than an
aspiration.

**No fix needed — this is a finding that makes the design cheaper.** Recorded
because the whole two-pool design rests on it and it was verified, not assumed.

### A3 · MODEL GAP (high) — resolved: the Sanskrit grammar ladder has a machine-readable spine

Grammar-driven levels were chosen over frequency because no CEFR-graded,
redistributable Sanskrit word list exists to borrow a ladder from. That left the
question of where the grammar ladder itself comes from — hand-curating a
syllabus was the expected answer.

It does not need curating. Every kaikki Sanskrit entry carries the grammar as
tags. In the sample: 1,674 of 1,676 entries have inflected forms, **median 35
forms per entry, maximum 281**. All eight cases are tagged by name (nominative
7,939, accusative 7,327, instrumental 7,206, genitive 6,674, ablative 6,441,
locative 6,397, dative 6,042, vocative 7,992) across singular/dual/plural, and
verbs carry voice, mood and person. Critically, two fields name the difficulty
axis directly: `class` (`a-stem`, …) and `inflection-template`
(`sa-decl-adj-mfn`, …), present on 2,141 form-rows in the sample.

**Fix:** derive levels from `class` + `inflection-template` — level *n* is the
set of stem classes and paradigm templates you can parse — and gate progression
on parsing questions drawn from real form tables. Smallest correct approach
because the ladder is read out of the data rather than authored, so it cannot
drift from what the cards actually contain.

### A4 · DESIGN RISK (medium): Sanskrit gets no example sentences from Tatoeba

Filin gave 9,734 of 10,500 words a human-written Tatoeba sentence. That does not
transfer. Measured, by decompressing both exports:

| Language | Tatoeba sentences |
|---|---|
| Hindi | 16,475 |
| **Sanskrit** | **166** |

166 is nothing. Hindi's 16,475 is modest but real — enough to attach sentences
to the common core, not to 27,000 headwords.

**Fix:** do not promise sentences the sources cannot supply. Hindi cards get a
Tatoeba sentence where one exists and render an explicit empty slot where it
does not, the way Inkstone marks its 10,897 imported cards rather than quietly
showing a shorter card. For Sanskrit the honest substitute is **real text
lines**, not invented ones — the Digital Corpus of Sanskrit is lemmatised
classical text and is the candidate, but I have **not** verified its licence or
its bulk-download format yet, so it is listed as unconfirmed and B5 is the step
where it gets checked before anything depends on it.

Nothing in this app will ever compose its own Sanskrit sentence. Filin's rule —
"there is no mode in which Filin writes Russian" — applies with more force here,
because sandhi means a wrong join is not a typo but a different word.

### A5 · NOISE (low): the Hindi frequency list is at the 2016 path, not 2018

`content/2018/hi/hi_50k.txt` returns 404; `content/2016/hi/hi_50k.txt` returns
200. Noted so the build does not rediscover it. Same jsdelivr mirror Filin uses,
for the same reason — `raw.githubusercontent.com` was unreachable from this
machine when Filin was built.

### A6 · Scale, extrapolated

Sample-scaled by file size, so these are estimates and are marked as such
wherever they appear:

| | Dump | Sample | *Extrapolated* headwords |
|---|---|---|---|
| Hindi | 153 MB | 4,474 entries in 25 MB | ~27,000 |
| Sanskrit | 133 MB | 1,676 entries in 20 MB | ~11,000 |

For comparison: Inkstone holds 10,961 words, Filin 10,500. Hindi at ~27,000 is
larger than either and will need trimming to a defensible core rather than
shipping every Wiktionary headword — frequency rank from A5 is what does the
trimming. The ~7,000 extrapolated तत्सम words are the vocabulary drill's real
ceiling, and that is the number that matters for the Hindi track.

---

## Part B — the build

Each step is independently shippable and ends in something runnable. Nothing
after B1 begins until B1 runs.

**B1 · Skeleton.** One `hind.html`, `"use strict"` + IIFE + a single
`window.Hind` namespace. Storage under one key with `SCHEMA_VERSION = 1`, the
router, the view registration, both themes as tokens, empty states, and one
hard-coded fake card per drill so every screen renders end to end with no data.
Lifted from `Helth/js/core.js` per the reusable-assets table — storage, local
date keys, router, toasts, timer. Run it before anything else lands.

**B2 · The data pipeline.** `build/build_data.py`, Python for data and never for
serving, product committed, `GENERATED` marker comments exactly as Inkstone and
Filin do it. Reads the two kaikki dumps and the frequency list; emits the Hindi
word table with its stratum tag, the तत्सम↔Sanskrit edge list, the Sanskrit
entries with their form tables, and the `class`/`inflection-template` ladder.
`build/sources/README.md` lists every URL and byte size, sources uncommitted.

> **Done 2026-09-02.** 59/59 checks pass; regeneration is byte-identical and
> leaves hand-written code outside the markers untouched, verified rather than
> asserted. Four things came out differently from the estimates above:
>
> - **A6's extrapolation was low for Hindi.** 35,653 headwords, not ~27,000.
>   Sanskrit was close: 11,538 against ~11,000.
> - **Only 31% of Hindi can be assigned a stratum.** 17,836 headwords (50%)
>   carry no etymology template at all. The shipped set is the 10,413 words that
>   can be classified; the rest enter no drill, because a guessed stratum would
>   corrupt the exact distinction the app exists to make. Home states the number.
> - **The paradigm budget is a real trade.** Carrying all 6,536 Sanskrit case
>   tables made the page 14.6 MB. 1,500 ship, chosen by a principle rather than a
>   quota — a word with a Hindi तत्सम descendant first, since it pays down both
>   tracks at once (1,199 of the 1,500), then a floor of 60 per stem class so no
>   ladder rung lacks worked examples. Final page 5.91 MB, loading in 0.22 s.
> - **Two data bugs found by running, not reading.** 14% of paradigm cells had a
>   footnote digit welded to the glyphs (विश्वेभिः**1**), and 36% of case+number
>   slots collided. The collisions were not gender — gender lives on the entry —
>   but Vedic variants sharing a slot with the classical form. Digits are now
>   stripped, the classical form is primary, and 25,054 variants are preserved
>   separately so an MCQ never offers two correct answers in one question.
>
> **A5 was understated.** `hi_50k.txt` holds 2,968 lines, not 50,000 — the Hindi
> OpenSubtitles corpus is a twelfth of the advertised size. It still ranks the
> decode pool, which is all it is asked to do, but it cannot rank the dictionary.

**B3 · The script module.** The shared Devanagari layer both tracks sit on:
letters, matras, the conjunct inventory, and the confusable families from A1.
This is the piece that makes one app out of two languages.

**B4 · Hindi track.** The three drills of Part 0, in order of how much they
matter: decoding first (it is the headline problem), then writing recognition,
then formal vocabulary. Each drill owns its own scoring, and the decoding
drill's timer is per-word with a visible window, not a session clock.

**B5 · Sanskrit track.** Grammar-laddered SRS over the A3 spine. Begins by
resolving A4's unconfirmed DCS question — licence and bulk format — and if DCS
does not work out, Sanskrit ships without example sentences and says so on the
card, rather than substituting something invented.

**B6 · Progress, level gates, backup/restore, CSV export.** The standing
requirements from `context.md`. Level gates follow the existing apps' shape —
30 questions, 80% to pass, sampling weighted by inverse Leitner box plus lapses.

**B7 · Indie visual pass.** The design constraint, applied once the structure is
settled rather than fought with throughout. Distinctive display type, warm
paper/ink tones, personality over polish — and explicitly *not* Indic motif
work, which was ruled out in the interview.

> **B3–B7 done 2026-09-02.** 56/56 checks in the main harness, plus targeted
> checks on each fix. Nine views, both themes, zero console errors, 6.2 MB
> loading in 0.84 s. Four things are worth recording:
>
> - **A question with two right answers is the failure mode that matters, and
>   both directions had one.** कमलौ is nominative *and* accusative dual, so the
>   parse drill only draws forms unique within their own paradigm; कमला is a real
>   Vedic nominative dual, so it is never offered as a wrong answer. Verified over
>   1,200 generated questions each, 0 violations.
> - **`sample()` was silently broken and took the whole Formation drill with
>   it.** It deduped on `c.w`, which only word records have, so matras, conjuncts
>   and families all hashed to `undefined` and it returned one item — every
>   Formation question failed to build and the view rendered its empty state. The
>   harness caught it as "19 items generated of 600, all one shape". Now
>   shuffle-and-take: 600 of 600, all three shapes.
> - **Etymology was the wrong basis for pool membership, and कर proved it.** A
>   pure register split put कर in the vocabulary drill as a word you supposedly
>   would not say — but कर is the stem of करना and ranks #5 in the corpus. 89
>   तत्सम words are ordinary speech (समय, कारण) and now drill as decoding words.
>   The register still shows on the card; only the "you would not say this" claim
>   is withdrawn. A further 183 headwords sit in two registers at once (काम is
>   तत्सम "desire" and तद्भव "work") and are dropped from both pools.
> - **A frequency rank counts spellings, not senses**, and so does Tatoeba
>   matching. Both are now labelled for what they measured rather than implying a
>   precision the corpus cannot deliver.
>
> Shipped beyond Part B: the PWA shell (`index.html`, `sw.js`,
> `manifest.webmanifest`, `icons/icon.svg`), `README.md` and `LICENSE-DATA.md` —
> Wiktionary is CC BY-SA, so the generated blocks carry that licence.

**Name:** proposing **Shirorekha** (शिरोरेखा) — the headline stroke that runs
across the top of every Devanagari word and ties its letters into a unit. It is
the line your eye actually tracks when reading the script quickly, which is what
this app is for. Folder stays `hind/`. Say if you want something else; Inkstone
and Filin both earned their names, so this one should too.

---

## Out of scope

- **Graded handwriting or any drawn input.** Confirmed in the interview. A1 now
  narrows the ungraded reference too, pending your call.
- **Passage-comprehension reading.** Word and phrase level only. The decoding
  drill measures reading speed; passages measure comprehension, which is a
  different tool and a much larger sourcing job.
- **Speaking, listening and pronunciation.** You already speak Hindi, and
  Sanskrit recitation is a real skill this app is not equipped to grade. No TTS
  view — note that Filin's Listen view exists only because a `ru-RU` voice
  usually exists; Hindi and Sanskrit voice availability is untested and would
  need the same visible-degradation guard before it could ship.
- **Urdu script.** Hindi's Perso-Arabic vocabulary stratum is in scope as
  *vocabulary*; Nastaʿlīq is a second script and a second project.
- **Any frequency-derived Sanskrit level ladder.** Ruled out in the interview,
  and A3 removes the last reason to want one.
- **A wall poster.** Both existing apps ship one. This is deliberately deferred
  to after the app works, not designed alongside it.
