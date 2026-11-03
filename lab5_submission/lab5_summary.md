# Lab 5 – Static Code Analysis: Summary

**Student repo:** Kailash-3010/PES1UG24CS211_Public_bus_Live_tracking
**File analysed:** `game.py` (Treasure Hunt, pygame)
**Branch:** `feature/lab5-static-code-analysis`
**Environment:** Python 3.11.9, pygame-ce 2.5.8, Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1 (Windows 11)

## Commands

```
python -m pylint game.py > pylint_before.txt / pylint_after.txt
python -m bandit game.py -f txt -o bandit_before.txt / bandit_after.txt
python -m flake8 game.py > flake8_before.txt / flake8_after.txt
```

Before reports were generated from the unmodified `game.py` (commit `4562aef`). They match
the reports produced on 2026-10-15, apart from the Bandit timestamp and Pylint's
"previous run" note.

## Results

| Check | Before | After |
|-------|--------|-------|
| Pylint score | 4.01/10 | **10.00/10** |
| Pylint messages | 36 (13 E1101, 8 C0116, 7 C0321, 2 C0115, 2 C0301, 1 C0114, 1 C0411, 1 R0902, 1 R0914) | **0** |
| Bandit issues | 4 (Low 4 / Medium 0 / High 0), all B311 | **0** (4 skipped by `# nosec B311`) |
| Flake8 violations | 116 (75 E231, 22 E225, 7 E701, 6 E501, 3 E302, 2 E305, 1 E275) | **0** (`flake8_after.txt` is empty) |
| `python -m py_compile game.py` | n/a | Pass |
| Map generation, old vs new, 500 seeds | n/a | Identical |
| Headless scripted gameplay, old vs new, 40 seeds | n/a | Identical state and rendered frames |
| `python game.py` (real window, 6 s) | n/a | Started and ran without errors |

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | `56a399b9674072fa96366bbbfa6ca2d316ab6890` | fix: improve Python code quality with Pylint |
| 2 | `36e09114acb60a2e722bdbd74db86a8977836a1a` | fix: address Bandit security findings |
| 3 | `5b35d5023509229e228bfcc5165a7a7aca0a0fc6` | style: resolve Flake8 formatting violations |

A fourth commit adds the after-reports and documentation (this file, the issue table and
the reflection).

**Overlap between commits:** splitting the one-line `if` statements in commit 1 (Pylint
C0321) also removed all 7 Flake8 E701 violations and 3 of the 6 E501 violations (lines
69, 109 and 136). Replacing `self.big_font` with the longer `self.fonts["title"]`
temporarily pushed two lines past 79 characters. All 5 remaining E501 violations were
fixed in commit 3.

## Justified suppressions or configuration

* `.pylintrc` sets `extension-pkg-allow-list=pygame` because the pygame `E1101` reports
  were false positives (pygame's members are defined in a C extension). No Pylint checks
  are disabled.
* `# nosec B311` on the 4 `random.randint()` lines in `_carve_rooms()`, because the
  randomness only lays out the game map and is not used for security. B311 stays active
  everywhere else.

## Limitations

Bandit reporting no issues does not mean the game is secure; it only means none of
Bandit's known patterns matched. The game was not played through by hand. Gameplay was
checked with a scripted headless comparison against the original plus a short windowed
launch.
