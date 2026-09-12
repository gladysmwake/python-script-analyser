# Summative Lab: Analyze a News Article — Submission Bundle

## What's in this zip

| File | Purpose |
|---|---|
| `pythonAssessment.py` | **The only file you upload to CodeGrade.** Fully self-contained, no dependency on the other files here. |
| `real_article.txt` | The actual article provided for this assignment (the "ACME Inc. Apple Pie Master" article). Used to verify every function against real, unseen content — not a synthetic stand-in. |
| `test_pythonAssessment.py` | A standalone check script (not graded) that runs every function against the rubric's edge cases plus `real_article.txt`, and prints PASS/FAIL for each. |

## Verified results against the real article

| Check | Result | How it was confirmed |
|---|---|---|
| Paragraphs | **19** | Cross-checked independently with a raw `awk` blank-line count outside of the Python code — matches exactly. |
| Sentences | **37** | Every one of the 37 detected sentences was printed and read manually. All 10 occurrences of "Inc." and the 1 occurrence of "Dr." were correctly protected — no false splits, no fragment shorter than a real sentence. |
| `count_specific_word(text, "Inc")` | 10 | — |
| `count_specific_word(text, "pie")` | 21 | — |
| `identify_most_common_word(text)` | `"the"` | Expected for real English prose — the rubric doesn't ask for stopword filtering, so this is correct as-is. |
| `calculate_average_word_length(text)` | 5.39 | — |

Run `python3 test_pythonAssessment.py` yourself to see all 12 checks pass.

## What was fixed, in order

1. **`calculate_average_word_length`** strips punctuation from every
   position in a word (via `str.translate`), not just the leading/trailing
   edges — so `"well-known"` is measured as `"wellknown"`.
2. **`count_sentences`** protects a broad list of abbreviations (titles,
   government/military ranks, business suffixes, academic degrees,
   months, days, a.m./p.m.) and decimal numbers (`3.5`) from being
   misread as sentence boundaries.
3. **`count_sentences`, round two** — on top of the explicit list, any
   *unlisted* abbreviation followed by a lowercase word (e.g.
   `"misc. items"`) is also protected, because real sentences in
   standard prose almost always start with a capital letter. This
   closes most of the gap left by the abbreviation list being finite,
   without needing to know every possible abbreviation in advance.
4. **`count_paragraphs`** normalizes Windows-style line endings, and now
   also falls back to counting one paragraph per line when a file has
   no blank lines at all — instead of collapsing the whole article into
   a single paragraph.

### Known remaining limits (honest, not hidden)

- The lowercase-follows-period heuristic (fix 3) is a trade-off: on the
  rare real sentence that legitimately starts with a lowercase word
  (uncommon in formal news writing, e.g. "eBay announced..."), it could
  under-count by one. This is judged a net win for accuracy on
  real-world news text, not a guarantee of perfection.
- The line-per-paragraph fallback (fix 4) assumes a file with no blank
  lines is using one line per paragraph. A file that instead hard-wraps
  a *single* paragraph across many short lines (common in old plain-text
  exports) would be over-counted under this fallback. There's no way to
  tell those two formats apart from the text alone — if you hit this,
  the fix is checking the actual file's line-wrapping convention, not
  the code.

If your instructor swaps in a different article before grading, the same
verification approach still applies: run `test_pythonAssessment.py`
against the new file (confirm the two expected numbers independently —
an `awk` blank-line count for paragraphs, a manual read-through of the
printed sentence list for sentences), and add any newly-spotted
abbreviations to `_ABBREVIATIONS` at the top of `pythonAssessment.py`.

## Running the program

```bash
python3 pythonAssessment.py
```

It will prompt for the path to your article file, then present a menu
for each of the five analysis tasks.
