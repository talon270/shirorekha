# Shirorekha — suggestions

Written 2026-10-19, against commit `87e119d` (working tree clean before this
pass).
Method: headless Chromium on `hind.html` via `file://`, light and dark, at
390, 1440 and 1920 px, with a click-through. An unreadable-data probe on
`hind.state.v1`. The service worker run on one local origin next to `vis`.
A read of `Store` (load, save, importJSON) and the restore UI.

**One fix applied in this pass (A1). Everything else is a suggestion and is
not implemented.** `sw.js` was clean in git, so git is the backup.

## Result

Zero page errors and console errors, both themes, all three widths. No
sideways scroll at 390 px. An unreadable save is handled properly: it is
copied to `hind.state.v1.corrupt.<ms>` and a toast says so. Date keys honour
the day boundary in local time.

## Part A — findings, ranked

### A1 · BUG (high): the service worker deleted every other app's offline cache — FIXED

The site is live at `talon270.github.io/shirorekha/`, the same origin as vis,
Study, Docket, attendance-budget, epok, inkstone, filin and fowler, which
share one CacheStorage. On activate, `sw.js` deleted every cache except
`shirorekha-v1`, so each Shirorekha update wiped the others' offline copies,
and their updates wiped this one. Reproduced with one of them: `vis` opened
offline afterwards returns 504 "Offline, and this file was never cached."
**Fix (applied):** delete only names starting `shirorekha-`. That is one line
plus a comment. Checked on one local origin: `vis-shell-3` survives, a planted
`shirorekha-stale-old` is deleted, and `shirorekha-v1` installs.

### A2 · DESIGN RISK (medium, unconfirmed here): a second open tab can erase the first's progress

There is no `storage` listener, so a stale tab's next save writes its old
`state` over the other tab's reviews. The same shape was reproduced in Study
(1 logged session → 0) and Ledger (1 expense → 0) and fixed there. Not
reproduced in this app. **Suggested fix:** Ferm's version, which is 5 lines:
on `storage` for this key, `Store.load()` then `Router.show()`. Not applied,
because a re-render mid-review would reset the card on screen. Decide whether
you'd rather adopt silently and repaint on the next navigation.

### A3 · DESIGN RISK (low): "Restore from the box" has no undo

`Store.importJSON()` replaces everything and saves at once. Inkstone keeps the
replaced state under `.pre-import` with an Undo button in Settings. Port it if
you ever paste the wrong backup.

### A4 · NOISE (low): `PLAN-hind.md` has no status line

Every other plan here says whether it shipped. Add one.
