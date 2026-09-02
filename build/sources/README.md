# Source files

Not committed — together about 470 MB, and every one is a published download
that can be fetched again. `build/build_data.py` expects these exact filenames
in this directory.

| File | Bytes | Where it comes from |
|---|---|---|
| `kaikki-hi.jsonl` | 160 MB | `https://kaikki.org/dictionary/Hindi/kaikki.org-dictionary-Hindi.jsonl` |
| `kaikki-sa.jsonl` | 139 MB | `https://kaikki.org/dictionary/Sanskrit/kaikki.org-dictionary-Sanskrit.jsonl` |
| `hi_50k.txt` | 30 KB | `https://cdn.jsdelivr.net/gh/hermitdave/FrequencyWords@master/content/2016/hi/hi_50k.txt` |
| `hin_sentences.tsv.bz2` | 179 KB | `https://downloads.tatoeba.org/exports/per_language/hin/hin_sentences.tsv.bz2` |
| `eng_sentences.tsv.bz2` | 25 MB | `https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2` |
| `links.tar.bz2` | 149 MB | `https://downloads.tatoeba.org/exports/links.tar.bz2` |

Two traps worth writing down, both found by downloading rather than by reading
the documentation:

**`hi_50k.txt` is not 50,000 words — it is 2,968.** The Hindi OpenSubtitles
corpus is small, and the filename follows the project's naming convention rather
than its own contents. It is still the right spine for the decode drill, because
those 2,968 words are the ones a Hindi speaker actually hears, but it cannot
rank a 35,653-word dictionary and the generator does not pretend it can.

**The 2018 path 404s; Hindi is only under `content/2016/`.** Russian in Filin is
at 2018. Same jsdelivr mirror, for the same reason as Filin — plain
`raw.githubusercontent.com` was unreachable from this machine.

The kaikki dumps support range requests, so `curl -C -` resumes a broken
download rather than restarting.

Licences for every source are in `../../LICENSE-DATA.md`.
