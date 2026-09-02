# Shirorekha

A Devanagari reading-speed trainer for someone who already speaks Hindi, and a
Sanskrit tutor from zero, in one offline page. Every question is multiple
choice; nothing here asks you to type or draw. The app holds **10,243 Hindi
words split into what you already know by ear (5,070) and the written register
you do not (5,173)**, plus **10,976 Sanskrit words, 1,500 of them with a full
case paradigm**, and it treats those as two tracks over one shared word graph —
because a तत्सम Hindi word *is* a Sanskrit word, so studying one pays down the
other. 2,823 of those cross-links resolve to a real Sanskrit card.

Hindi glosses, register and Sanskrit paradigms come from English Wiktionary via
kaikki.org; example sentences from Tatoeba; frequency rank from OpenSubtitles.
See **Data sources** below.

शिरोरेखा is the headline stroke across the top of a Devanagari word — the line
your eye actually tracks when reading the script at speed.

## Run it

Open `index.html` (or `hind.html` directly) — `file://` works, no build step, no
server, no dependencies. Nothing is fetched after the page loads.

Served over http(s) it installs as a PWA and works with no connection
afterwards. `file://` skips the service worker entirely (no secure context) and
just runs.

### Regenerating the data

Only needed when an upstream source changes. Python for data, never for serving;
the product is committed, so nothing below runs at page load.

```
python3 -m venv build/.venv
build/.venv/bin/python build/build_data.py
```

It rewrites the three blocks between the `GENERATED` marker comments inside
`hind.html`. Everything outside those markers is hand-written and survives a
regeneration untouched — verified by re-running and diffing, not assumed. The
six source files (~470 MB) are not committed; `build/sources/README.md` lists
where each one comes from.

## The files

| File | What it is |
|---|---|
| `hind.html` | The app. One self-contained 6.2 MB document |
| `build/build_data.py` | Turns three upstream sources into the three generated blocks |
| `index.html` | The launcher, and where the service worker registers |
| `PLAN-hind.md` | The plan, its findings, and what changed during the build |

## Views

| View | What it does |
|---|---|
| Home | Due count, streak, the four session launchers, and what the data does and does not cover |
| Decode | Timed. A word flashes, then hides; pick its meaning |
| Formation | Untimed. Confusable letter families, matra placement, conjuncts |
| तत्सम | Untimed. The Sanskrit-derived written register, with its Sanskrit source on the answer |
| Sanskrit | Grammar-laddered. Parse a form's case, or choose the form for a case |
| Gate | 30 questions, 80% to open the next stem class |
| Script | The formation rules, families, matras and conjuncts as a reference |
| Progress | Cards per day over 12 weeks, per-drill accuracy, ladder distribution |
| Settings | Day boundary, flash-window scale, backup/restore, CSV export, and what's assumed |

## The things most language apps get wrong

**A drill that mixes two problems measures neither.** "I read Hindi slowly" has
two unrelated causes: the letterforms not resolving, and the word being one you
have never met. A single mixed drill produces one accuracy number that cannot
tell them apart. So the decode drill draws **only** from the 5,070 words a Hindi
speaker already knows by ear, and it is timed, because for those words the only
thing that can fail is the script. The vocabulary drill draws from the 5,173
words of the written register and is **untimed**, because there the only thing
that can fail is knowledge. Two pools, two questions, two numbers that mean
something.

**Frequency outranks etymology when deciding what you already know.** The pools
started as a pure etymology split — तद्भव and Perso-Arabic in one, तत्सम in the
other — and that put कर in the vocabulary drill as a word you supposedly would
not say, when कर is the stem of करना and ranks **#5 in the corpus**. Etymology
is indirect evidence about a learner; corpus frequency is direct. So a तत्सम
word that appears in the 2,968-word everyday list is drilled as a decoding word
instead: 89 of them, including समय and कारण, which are Sanskrit-derived and
completely ordinary speech. The card still shows the तत्सम register, because
that is true — only the claim "you would not say this" is withdrawn.

**The register is copied, never guessed.** Which pool a word belongs to is
decided by Wiktionary's own etymology template — `inh` from Prakrit makes घर
तद्भव, `lbor` from Sanskrit makes विश्व तत्सम — and never by how a word looks.
This matters because the guess is *easy* and wrong often enough to poison the
whole design: half of Hindi Wiktionary (17,836 headwords) carries no etymology
at all, and those words ship in no drill rather than being filed by vibe. Home
prints that number.

**A word in two registers at once is dropped from both.** काम is तत्सम in the
sense "desire, Kāma" and तद्भव in the "work" sense every speaker uses daily.
183 headwords are like this. Neither pool's claim is true of them, so they enter
neither — 1.6% of the classifiable vocabulary, traded for a distinction that
stays honest.

**A frequency rank counts spellings, not senses, and the card says so.** कर
ranks #5 in the corpus — but that is कर the stem of करना, "to do", not the
literary कर meaning "hand" that the तत्सम card teaches. The corpus cannot tell
them apart and neither can this app, so the card reads "#5 of 2,968 — by
spelling, not by sense" instead of implying a precision it does not have. Tatoeba
sentences carry the same caveat for the same reason.

**A Sanskrit level is a grammar level.** No CEFR-graded, redistributable
Sanskrit word list exists, so there is no lexical ladder to borrow. Ranking by
corpus frequency would have produced something shaped like an HSK level and
measuring the wrong thing — a hard Sanskrit word is usually a *common* word in a
case form you cannot resolve. So a level is a set of stem classes: `a-stem`
first because it covers 8,009 words, down through `ā-stem`, `ī-stem`, `i-stem`
to `is-stem`, fifteen rungs. Five further classes (`us-stem`, `añc-stem`,
`au-stem`, `o-stem`, `vāṃs-stem`) had fewer than ten worked examples and are
**not** rungs — a level you cannot practise is not a level.

**A question with two right answers is a broken question.** कमलौ is both the
nominative and the accusative dual, so "what case is कमलौ?" cannot be asked. The
parse drill only draws forms that occupy exactly one slot in their own paradigm.
Going the other way, कमला is a genuine Vedic nominative dual beside classical
कमलौ, so it is never offered as a *wrong* answer. Both guards were verified over
1,200 generated questions each, not reasoned about.

**Nothing here inflects a Sanskrit word.** Every one of the 36,000 paradigm
cells is a form Wiktionary published. Constructing an ending would be the app
teaching an error, and sandhi means a wrong join is not a typo but a different
word.

**Stroke-order diagrams are not shipped, because the data does not exist.**
There is no Devanagari equivalent of Make Me a Hanzi or KanjiVG: Wikimedia
Commons holds 13 stroke-order files covering 12 of the 44 core letters, and all
12 are vowels. Hand-authoring the 32 missing consonants would mean inventing
reference material a learner cannot check — the same failure class as a guessed
stress mark. What ships instead is **formation rules and confusable families**:
the शिरोरेखा is drawn last, most consonants are a stem plus a left-hand element,
ि is written before its consonant but read after it, and ब/व, घ/ध, ट/ठ, ड/ढ
differ by one stroke. That is a narrower claim, and it holds.

**A misclick is reversible.** A wrong answer offers an undo that restores the
card's exact prior schedule from a snapshot rather than approximating it. There
is no `alert()` or `confirm()` anywhere in the app.

**A projection is a window with its sample count, or a refusal.** Under five
logged days Home says it does not know yet, instead of extrapolating a finish
date from noise.

## What's assumed vs. what's solid

| | |
|---|---|
| **Solid** | Vocabulary register — copied from Wiktionary etymology templates, never inferred from a word's shape |
| **Solid** | Every Sanskrit inflected form. 36,000 cells, all published by Wiktionary; footnote markers stripped, 25,054 Vedic variants kept separate from the classical forms |
| **Solid** | Hindi glosses for all 10,243 shipped words |
| **Solid** | Leitner intervals (0, 1, 3, 7, 16, 35, 75 days) — a fixed ladder, not adaptive per-card difficulty |
| **Solid** | Frequency rank for 2,968 words — as a rank of *spellings* |
| **Assumed** | Sanskrit levels — stem classes ordered by corpus coverage. No graded word list exists to borrow a ladder from |
| **Assumed** | Gate thresholds (60% to attempt, 80% to pass) — hand-picked, not tuned against real learners |
| **Assumed** | The confusable letter families and formation rules — hand-written; no machine-readable source describes them |
| **Assumed** | Flash windows (2.6 s down to 0.85 s across the ladder) — picked by feel, and scalable in Settings |
| **Not shipped** | Stroke-order diagrams. 13 of 44 letters exist upstream, all vowels |
| **Not shipped** | Passage reading, handwriting input, audio. Out of scope by decision, not by accident |

## Data & privacy

Everything — schedule, streak, log, settings — lives in one `localStorage` key
(`hind.state.v1`) on the device that used it. Nothing is sent anywhere; there is
no analytics, no telemetry and no remote of any kind. Settings exports a full
JSON backup and a CSV of the schedule, and restores from either. Nothing in this
repository is personal.

A corrupt save is **kept**, not overwritten — it is moved to a side key and a
fresh profile starts beside it, because an unreadable save is a reason to
preserve data, not delete it.

## Data sources

| Source | Licence | Used for |
|---|---|---|
| [English Wiktionary](https://en.wiktionary.org) via [kaikki.org](https://kaikki.org) | **CC BY-SA 4.0** | Glosses, etymology, register, stem classes, every inflected form |
| [Tatoeba](https://tatoeba.org) | **CC BY 2.0 FR** | Example sentences and translations |
| [FrequencyWords](https://github.com/hermitdave/FrequencyWords) | MIT | Hindi frequency rank |

Wiktionary is share-alike: the generated data blocks carry the same licence.
See `LICENSE-DATA.md`.
