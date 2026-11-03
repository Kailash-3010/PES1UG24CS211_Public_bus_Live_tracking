# Lab 5 – Issue Documentation (`game.py`)

Line numbers refer to the **original** `game.py` (commit `4562aef`), as reported in
`pylint_before.txt`, `bandit_before.txt` and `flake8_before.txt`.
Tool versions: Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1, Python 3.11.9, pygame-ce 2.5.8.

| Issue | Type | Line(s) | Description | Fix Approach | Verification |
|-------|------|---------|-------------|--------------|--------------|
| `B311` blacklisted pseudo-random generator (×4) | Security (Bandit, Low severity / High confidence) | 13, 14, 15, 16 | `random.randint()` used for room width, height, x and y. Bandit flags the standard PRNG as unsuitable for security or cryptography. | **False positive.** The values only lay out the dungeon; no secret, token, password or key is derived from them, so predictability is not a risk. Kept `random` (switching to `secrets` would also break seed-based reproducibility) and added `# nosec B311` to those 4 lines only, with a comment giving the reason. B311 is not disabled anywhere else. | `bandit_after.txt`: "No issues identified", 0 Low/Medium/High, 4 issues skipped by `#nosec B311`. |
| `E1101` no-member for pygame (×13) | Pylint error (false positive) | 60–63, 87, 108, 109, 161 | Pylint said `pygame` has no `K_LEFT`, `K_a`, `QUIT`, `KEYDOWN`, `K_r`, `init`, `quit`, … | **False positive.** These names exist at runtime (checked with `hasattr`). They are defined in pygame's compiled C extension, which Pylint does not load by default. Added `.pylintrc` with `extension-pkg-allow-list=pygame` so Pylint inspects the real module. No `disable=` was used. | `pylint_after.txt`: no E1101; score 10.00/10. |
| Missing docstrings (×11) | Pylint convention (C0114, C0115, C0116) | 1, 9, 52, 58, 75, 85, 95, 106, 112, 128, 154 | No module docstring; `Player` and `GameEngine` had no class docstrings; 8 functions/methods had no docstrings. | Wrote docstrings for the module, both classes and every public function/method, describing what each does (for example, the return value of `generate_world()`). | `pylint_after.txt`: no C0114/C0115/C0116. |
| Multiple statements on one line (×7) | Pylint convention C0321 + Flake8 E701 | 60, 61, 62, 63, 108, 109, 113 | e.g. `if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx=-SPEED` and `if self.won: return`. | Put each body on its own indented line. Control flow is unchanged. | No C0321 in `pylint_after.txt`; no E701 in `flake8_after.txt` (empty). |
| Too many local variables (20/15) | Pylint refactor R0914 | 9 | `generate_world()` both carved rooms and dug corridors, so it had 20 locals. | Moved room carving into `_carve_rooms()` and corridor digging into `_connect_rooms()`; `generate_world()` now calls them. The `random` calls run in the same order, so a given seed still gives the same map. | No R0914. The original and new `generate_world()` returned identical grids for 500 seeds. |
| Too many instance attributes (8/7) | Pylint refactor R0902 | 85 | `GameEngine` held `font` and `big_font` as two separate attributes, plus 6 others. | Grouped the two fonts into one `self.fonts` dict (`"hud"`, `"title"`) and updated the 3 places that use them. | No R0902. The headless test produced pixel-identical frames to the original. |
| Line too long | Pylint C0301 (>100) + Flake8 E501 (>79) | 69, 78, 109, 136, 138, 142 | The longest line was the corner-list loop in `_try_move` (115 chars). | Pulled long expressions into named variables (`corners`, `center`, `marker`) or wrapped arguments inside brackets. | No C0301 or E501 in the after reports. |
| Wrong import order | Pylint C0411 | 2 | Standard-library `random` was imported after third-party `pygame`. | Put `import random` first, then a blank line, then `import pygame`. | No C0411. |
| Missing whitespace after `,` (×75) and around operators (×22) | Flake8 E231 / E225 | 13–14, 18, 46–49, 55, 59–73, 78, 118, 129–157 | e.g. `random.randint(3,6)`, `dx=dy=0`, `0<=r<rows`. | Added PEP 8 spacing. `git diff -w` for this commit shows only line wraps and one extracted variable. | `flake8_after.txt` is empty. |
| Missing whitespace after keyword | Flake8 E275 | 71 | `if not(0<=r<rows ...)` | Changed it to `if not (0 <= r < rows ...)`. | `flake8_after.txt` is empty. |
| Blank lines around top-level definitions | Flake8 E302 (×3) / E305 (×2) | 9, 45, 52, 85, 163 | Top-level `def`/`class` statements and the code after them had only 1 blank line. | Used 2 blank lines around each top-level definition. | `flake8_after.txt` is empty. |

## Totals

| Tool | Before | After |
|------|--------|-------|
| Pylint score | 4.01/10 (36 messages) | **10.00/10** (0 messages) |
| Bandit | 4 issues (Low 4, Medium 0, High 0) | **0 issues** (4 skipped via targeted `# nosec B311`) |
| Flake8 | 116 violations | **0** |
