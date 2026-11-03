# Lab 5 – Reflection

> **Note:** The Lab 5 handout asks for "answers to reflection questions provided in the lab"
> but does not list any questions. The headings below are a self-chosen reflection
> outline, **not** questions supplied by the instructor.

## 1. What is static code analysis?

Static code analysis checks source code **without running it**. Tools parse the code and
compare it against rules for style, likely bugs, design smells and insecure patterns. It runs
quickly and covers every line, including code paths that are rarely executed, so problems
are caught before the program is run or deployed.

## 2. Pylint vs. Bandit vs. Flake8

| Tool | Focus | What it found in `game.py` |
|------|-------|----------------------------|
| **Pylint** | Code quality, likely errors and design (docstrings, complexity, naming, imports) | Missing docstrings, one-line `if` statements, a function with 20 locals, a class with 8 attributes, wrong import order, and `E1101` reports for pygame members. Score 4.01/10. |
| **Bandit** | Security: dangerous functions and insecure patterns, by severity and confidence | 4 × `B311`, use of the standard `random` PRNG (Low severity) |
| **Flake8** | PEP 8 layout and simple logical errors (pycodestyle + pyflakes + mccabe) | 116 layout violations, mostly missing spaces after commas and around operators |

The three tools overlap only a little. For example, one-line `if` statements were reported
both by Pylint (`C0321`) and Flake8 (`E701`), and long lines by both, but with different
limits (100 and 79 characters).

## 3. Most important issues found

* **Pylint's 13 `E1101` "errors"** looked the most serious because they suggested the code
  would crash. Investigation showed they were **false positives**.
* **Structure:** `generate_world()` had too many responsibilities (R0914) and
  `GameEngine` had too many attributes (R0902).
* **Readability:** no docstrings, compound one-line statements, and dense code without
  spacing made the game harder to read and maintain.
* **Bandit B311:** the only security finding, and not a real vulnerability in this context.

## 4. How the issues were fixed

1. **Pylint commit:** added docstrings, split compound statements, fixed import order,
   split `generate_world()` into `_carve_rooms()` and `_connect_rooms()`, grouped the
   fonts into a dict, and added `.pylintrc` with `extension-pkg-allow-list=pygame` so
   Pylint can inspect pygame's C extension. Score: 4.01 to 10.00.
2. **Bandit commit:** after confirming the randomness only drives map layout, added a
   targeted `# nosec B311` to the 4 affected lines with an explanatory comment instead of
   disabling B311 globally or switching to `secrets` (which would also break seed-based
   reproducibility).
3. **Flake8 commit:** applied PEP 8 spacing, blank lines and line wrapping. Formatting
   only: `git diff -w` shows no logic changes. 116 to 0.

## 5. How static analysis improves quality and maintainability

* Gives a consistent, objective baseline that a team can enforce automatically (for
  example in CI or a pre-commit hook).
* Complexity warnings such as R0914 point to functions that should be split. After the
  split, the map generator is easier to read, test and extend (for example to add the
  traps or the guard from the README tasks).
* Docstrings and consistent formatting make the code faster for a new reader to
  understand and produce smaller, cleaner diffs during review.
* Security linters raise risky patterns early, while they are cheap to fix.

## 6. Limitations and false positives

* **False positives:** 13 of Pylint's 36 original messages (`E1101`) and all 4 Bandit
  findings did not describe real defects. Following the tools blindly would have meant
  deleting working pygame code or replacing `random` for no benefit.
* **Context is required:** Bandit cannot know whether a random number is a password or a
  room width. A developer has to judge this and should record the reason next to any
  suppression.
* **Scores can be gamed:** a perfect score can be reached by disabling checks, so the
  method matters as much as the number. Here no checks were disabled globally.
* **Not complete:** "No issues identified" from Bandit does **not** mean the program is
  secure. Static tools cannot detect wrong game logic, poor performance or most runtime
  behaviour.

## 7. Why runtime testing is still necessary

Static tools prove nothing about behaviour. Because the fixes included refactoring
(splitting `generate_world()`, regrouping fonts), I also checked runtime behaviour:

* `python -m py_compile game.py` passed.
* For the same random seed, the original and refactored `generate_world()` produced
  identical maps for 500 seeds.
* A headless test (SDL dummy video driver) ran both versions with the same scripted
  keyboard input for 40 seeds. Player positions, key and chest state, status text and the
  **rendered frames** were byte-identical. The test also covered: the chest does not
  count before the key, picking up the key and then the chest wins, movement freezes
  after a win, R restarts, and closing the window quits.
* `python game.py` opened the real window and ran for 6 s without errors.

What could not be checked automatically is how the game feels to play by hand, which
needs a manual play-through.
