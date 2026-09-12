"""
test_pythonAssessment.py
-------------------------
Quick, dependency-free sanity checks for pythonAssessment.py, run
against the ACTUAL article provided for this assignment
(real_article.txt), plus the empty-string edge cases the rubric
requires.

This is NOT part of the graded submission -- it exists so you (Echo) can
confirm every function behaves correctly before you upload
pythonAssessment.py to CodeGrade.

The expected paragraph count (19) was independently verified with a
raw blank-line count outside of pythonAssessment.py, and the expected
sentence count (37) was verified by printing and manually reading
every detected sentence to confirm none of the "Inc." or "Dr."
abbreviations caused a false split.

Run it with:
    python3 test_pythonAssessment.py
"""

from pythonAssessment import (
    read_article,
    count_specific_word,
    identify_most_common_word,
    calculate_average_word_length,
    count_paragraphs,
    count_sentences,
)

passed = 0
failed = 0


def check(label, actual, expected):
    """Compare `actual` to `expected`, print the result, and tally it."""
    global passed, failed
    if actual == expected:
        print(f"PASS  {label}")
        passed += 1
    else:
        print(f"FAIL  {label}  (expected {expected!r}, got {actual!r})")
        failed += 1


# --------------------------------------------------------------------------- #
# Edge cases required by the rubric (empty-string behavior)
# --------------------------------------------------------------------------- #
check("count_specific_word('', 'x') == 0", count_specific_word("", "x"), 0)
check("identify_most_common_word('') is None", identify_most_common_word(""), None)
check("calculate_average_word_length('') == 0", calculate_average_word_length(""), 0)
check("count_paragraphs('') == 1", count_paragraphs(""), 1)
check("count_sentences('') == 1", count_sentences(""), 1)

# --------------------------------------------------------------------------- #
# Fix 1: average word length strips punctuation from EVERY position,
# not just the leading/trailing edges.
# --------------------------------------------------------------------------- #
# "well-known" -> "wellknown" (9 chars), "example," -> "example" (7 chars)
# average = (9 + 7) / 2 = 8.0
check(
    "calculate_average_word_length strips internal punctuation",
    calculate_average_word_length("well-known example,"),
    8.0,
)

# --------------------------------------------------------------------------- #
# Fix 2: sentence counting is not fooled by abbreviations or decimals.
# --------------------------------------------------------------------------- #
check(
    "count_sentences ignores 'Dr.' as a sentence boundary",
    count_sentences("Dr. Smith arrived. He was late."),
    2,
)
check(
    "count_sentences ignores decimal numbers like '3.5'",
    count_sentences("The price is 3.5 dollars. It was expensive."),
    2,
)

# --------------------------------------------------------------------------- #
# Fix 3: an UNLISTED abbreviation followed by a lowercase word is still
# protected, via the generic lowercase-follows-period heuristic.
# --------------------------------------------------------------------------- #
check(
    "count_sentences ignores unlisted abbreviations before a lowercase word",
    count_sentences("The misc. items were sorted. Then we left."),
    2,
)

# --------------------------------------------------------------------------- #
# Fix 4: paragraph counting falls back to one-paragraph-per-line when a
# file has no blank lines at all, instead of undercounting as 1.
# --------------------------------------------------------------------------- #
check(
    "count_paragraphs falls back to line-based counting with no blank lines",
    count_paragraphs("First paragraph here.\nSecond paragraph here.\nThird one too."),
    3,
)
check(
    "count_paragraphs still returns 1 for a genuine single-line single paragraph",
    count_paragraphs("Just one paragraph, no newlines."),
    1,
)

# --------------------------------------------------------------------------- #
# Full run against the ACTUAL assignment article
# --------------------------------------------------------------------------- #
article_text = read_article("real_article.txt")

# 19 blank-line-separated blocks, confirmed independently with:
#   awk 'BEGIN{RS="";ORS="\n===\n"} {print}' real_article.txt | grep -c "==="
check("real article: count_paragraphs == 19", count_paragraphs(article_text), 19)

# 37 sentences, confirmed by printing every split and manually reading each
# one -- all 10 "Inc." occurrences and the 1 "Dr." occurrence were correctly
# protected, with no fragment shorter than a real sentence.
check("real article: count_sentences == 37", count_sentences(article_text), 37)

check(
    'real article: count_specific_word(text, "Inc") == 10',
    count_specific_word(article_text, "Inc"),
    10,
)
check(
    'real article: count_specific_word(text, "pie") == 21',
    count_specific_word(article_text, "pie"),
    21,
)

most_common = identify_most_common_word(article_text)
print(f"INFO  identify_most_common_word -> {most_common!r} (not asserted, informational)")

avg_length = calculate_average_word_length(article_text)
print(f"INFO  calculate_average_word_length -> {avg_length:.2f} (not asserted, informational)")

# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #
print(f"\n{passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
