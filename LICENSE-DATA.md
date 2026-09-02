# Data licences

The code in this repository is mine. The linguistic data is not, and two of the
four sources are **share-alike** — the dictionary data derived from them here
carries the same terms.

| Source | Licence | Used for |
|---|---|---|
| [English Wiktionary](https://en.wiktionary.org) via [kaikki.org](https://kaikki.org) | **CC BY-SA 4.0** | Hindi glosses, etymology and register; Sanskrit glosses, stem classes and every inflected form |
| [Tatoeba](https://tatoeba.org) | **CC BY 2.0 FR** | Hindi example sentences and their English translations |
| [FrequencyWords](https://github.com/hermitdave/FrequencyWords) (OpenSubtitles 2018) | MIT | Hindi frequency rank |

## What that means here

**The generated data blocks inside `hind.html` are derived from Wiktionary and
are therefore CC BY-SA 4.0.** Anyone redistributing this app redistributes that
data under the same licence, with attribution. The two blocks are marked
`GENERATED:HI` and `GENERATED:SA` and are the only part of the file this
applies to; everything outside those markers is hand-written.

**Tatoeba sentences require attribution and are sentence-level CC BY 2.0 FR.**
They appear on card answer screens and the app names Tatoeba in its footer.

**No source here is non-commercial.** Filin's KELLY list is CC BY-NC-SA and
constrains that app; nothing equivalent applies to this one.

## What is not from these sources

The formation rules, the confusable letter families, the matra placement notes
and the conjunct list in the Script view are **hand-written**. No machine-readable
source describes which Devanagari letters get confused for which — Wikimedia
Commons holds stroke-order art for 13 letters, all vowels — so that material is
mine, and the app labels it as assumed rather than sourced.
