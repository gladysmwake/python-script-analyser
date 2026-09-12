"""
pythonAssessment.py
--------------------
Summative Lab: Analyze a News Article

Reads a news article from a text file and performs five text-analysis
tasks on it:

    1. Count how many times a specific word appears in the article.
    2. Identify the most common word in the article.
    3. Calculate the average length of the words in the article.
    4. Count the number of paragraphs in the article.
    5. Count the number of sentences in the article.

Author: Echo (Gladys Mwangi)
"""

import re                          # regex: word extraction, sentence/paragraph splitting
import string                      # provides string.punctuation for cleaning words
from collections import Counter    # efficient way to find the most frequent word


# Punctuation-removal table, built once and reused by every function that
# needs to strip punctuation from a word (avoids rebuilding it on every call).
_PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)

# Common abbreviations whose trailing period should NOT be treated as the
# end of a sentence (e.g. "Mr. Smith" is one sentence, not two). This list
# is deliberately broad -- titles, honorifics, business suffixes, months,
# and academic degrees are the categories most likely to show up in a
# news article.
_ABBREVIATIONS = [
    # Personal titles
    "Mr", "Mrs", "Ms", "Mx", "Dr", "Prof", "Sr", "Jr", "St", "Rev", "Fr",
    # Government / military / official titles
    "Gov", "Sen", "Rep", "Pres", "Hon", "Gen", "Col", "Lt", "Sgt", "Capt",
    "Cpl", "Maj", "Adm",
    # Business suffixes
    "Inc", "Ltd", "Co", "Corp", "LLC", "LLP",
    # Academic degrees
    "Ph.D", "M.D", "B.A", "M.A", "B.Sc", "M.Sc",
    # Common Latin / general abbreviations
    "vs", "etc", "e.g", "i.e", "cf", "approx", "est", "misc", "no",
    "vol", "pg", "pp",
    # Countries / regions
    "U.S", "U.K", "U.N", "E.U",
    # Months
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Sept",
    "Oct", "Nov", "Dec",
    # Days
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
    # Time
    "a.m", "p.m",
]


# --------------------------------------------------------------------------- #
# Reading the article
# --------------------------------------------------------------------------- #
def read_article(file_path):
    """
    Read the contents of a text file into a single string.

    Args:
        file_path (str): Path to the news article text file.

    Returns:
        str: The full contents of the file, or an empty string if the
             file could not be found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Could not find a file named '{file_path}'.")
        return ""


# --------------------------------------------------------------------------- #
# Task 1: Count Specific Word
# --------------------------------------------------------------------------- #
def count_specific_word(text, word):
    """
    Count how many times `word` appears in `text` (case-insensitive,
    whole-word matches only).

    Args:
        text (str): The text to search through.
        word (str): The word to search for.

    Returns:
        int: The number of occurrences of `word` in `text`.
             Returns 0 if there are no matches (or if either argument
             is empty).
    """
    if not text or not word:
        return 0

    # \b\w+\b pulls out whole words and ignores surrounding punctuation,
    # so "NLP." and "nlp," both match a search for "nlp".
    words = re.findall(r"\b\w+\b", text.lower())
    target = word.lower()

    count = 0
    for current_word in words:            # for loop
        if current_word == target:
            count += 1

    return count


# --------------------------------------------------------------------------- #
# Task 2: Identify Most Common Word (regex-based, per rubric requirement)
# --------------------------------------------------------------------------- #
def identify_most_common_word(text):
    """
    Identify the most frequently occurring word in `text`.

    Args:
        text (str): The text to analyze.

    Returns:
        str | None: The most common word, or None if `text` is empty.
    """
    if not text:
        return None

    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return None

    word_counts = Counter(words)
    most_common_word, _ = word_counts.most_common(1)[0]
    return most_common_word


# --------------------------------------------------------------------------- #
# Task 3: Calculate Average Word Length
# --------------------------------------------------------------------------- #
def calculate_average_word_length(text):
    """
    Calculate the average length of the words in `text`.

    Punctuation and special characters are stripped from EVERY position
    in a word (not just the leading/trailing edges), so "well-known" is
    measured as "wellknown" and "startup," is measured as "startup".

    Args:
        text (str): The text to analyze.

    Returns:
        float: The average word length. Returns 0 if `text` is empty
               or contains no actual words.
    """
    if not text:
        return 0

    words = text.split()
    total_length = 0
    word_count = 0

    for word in words:                                   # for loop
        cleaned_word = word.translate(_PUNCTUATION_TABLE)  # strip ALL punctuation
        if cleaned_word:                                    # skip punctuation-only tokens
            total_length += len(cleaned_word)
            word_count += 1

    if word_count == 0:
        return 0

    return total_length / word_count


# --------------------------------------------------------------------------- #
# Task 4: Count Number of Paragraphs
# --------------------------------------------------------------------------- #
def count_paragraphs(text):
    """
    Count the number of paragraphs in `text`, where paragraphs are
    blocks of text separated by one or more blank lines.

    Args:
        text (str): The text to analyze.

    Returns:
        int: The number of paragraphs. Returns 1 if `text` is empty.
    """
    if not text:
        return 1

    # Normalize Windows/old-Mac line endings to \n before splitting, so
    # the paragraph count doesn't depend on which OS produced the file.
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    stripped_text = normalized_text.strip()

    # Primary rule, per the assignment spec: paragraphs are separated by
    # one or more blank lines.
    paragraphs = re.split(r"\n\s*\n", stripped_text)
    paragraphs = [p for p in paragraphs if p.strip()]

    # Fallback: some article files use one paragraph per line instead of
    # blank-line separation. If the blank-line rule found only a single
    # block but the text clearly has more than one line, treat each
    # non-empty line as its own paragraph instead of undercounting.
    if len(paragraphs) <= 1 and "\n" in stripped_text:
        line_based_paragraphs = [
            line for line in stripped_text.split("\n") if line.strip()
        ]
        if len(line_based_paragraphs) > 1:
            return len(line_based_paragraphs)

    return len(paragraphs) if paragraphs else 1


# --------------------------------------------------------------------------- #
# Task 5: Count Number of Sentences
# --------------------------------------------------------------------------- #
def count_sentences(text):
    """
    Count the number of sentences in `text`, where sentences are
    separated by '.', '!' or '?'.

    Before splitting, three common false-positive cases are neutralized so
    they aren't mistaken for sentence boundaries:
        - Known abbreviations such as "Mr.", "Dr.", "U.S.", "etc." (see
          _ABBREVIATIONS above).
        - Decimal numbers such as "3.5" (a period directly between two
          digits).
        - A period immediately followed by a lowercase word (e.g.
          "misc. items"). Real sentences in standard prose almost always
          start with a capital letter, so this catches many abbreviations
          that aren't explicitly listed above -- without needing to know
          every abbreviation in advance.
    This is a heuristic, not a full grammar parser -- it will not catch
    every abbreviation in every article, but it correctly handles the
    common cases that would otherwise inflate the sentence count.

    Args:
        text (str): The text to analyze.

    Returns:
        int: The number of sentences. Returns 1 if `text` is empty.
    """
    if not text:
        return 1

    working_text = text

    # Protect known abbreviations: turn "Mr." into "Mr<PERIOD>" so the
    # period is no longer visible to the sentence-splitting regex.
    for abbreviation in _ABBREVIATIONS:                 # for loop
        pattern = rf"\b{re.escape(abbreviation)}\."
        working_text = re.sub(pattern, f"{abbreviation}<PERIOD>", working_text)

    # Protect decimal numbers, e.g. "3.5" -> "3<PERIOD>5".
    working_text = re.sub(r"(?<=\d)\.(?=\d)", "<PERIOD>", working_text)

    # Protect unlisted abbreviations followed by a lowercase word, e.g.
    # "misc. items" -> "misc<PERIOD> items". Only applies to '.', since
    # '!' and '?' are essentially never used mid-abbreviation.
    working_text = re.sub(r"\.(?=\s+[a-z])", "<PERIOD>", working_text)

    sentences = re.split(r"[.!?]+", working_text)
    sentences = [s for s in sentences if s.strip()]

    return len(sentences) if sentences else 1


# --------------------------------------------------------------------------- #
# Menu-driven program
# --------------------------------------------------------------------------- #
MENU_OPTIONS = [
    ("1", "Count how many times a specific word appears"),
    ("2", "Identify the most common word"),
    ("3", "Calculate the average word length"),
    ("4", "Count the number of paragraphs"),
    ("5", "Count the number of sentences"),
    ("6", "Exit"),
]


def display_menu():
    """Print the list of available text-analysis options."""
    print("\n--- News Article Analyzer ---")
    for option_number, description in MENU_OPTIONS:   # for loop
        print(f"{option_number}. {description}")


def main():
    """Run the interactive news-article analyzer."""
    file_path = input("Enter the path to the news article text file: ").strip()
    article_text = read_article(file_path)

    if not article_text:
        print("No article text to analyze. Exiting.")
        return

    running = True
    while running:                                      # while loop
        display_menu()
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":                                # if/elif/else conditional
            word = input("Enter the word to search for: ").strip()
            result = count_specific_word(article_text, word)
            print(f'The word "{word}" appears {result} time(s).')

        elif choice == "2":
            result = identify_most_common_word(article_text)
            print(f"The most common word is: {result}")

        elif choice == "3":
            result = calculate_average_word_length(article_text)
            print(f"The average word length is: {result:.2f} characters")

        elif choice == "4":
            result = count_paragraphs(article_text)
            print(f"The article has {result} paragraph(s).")

        elif choice == "5":
            result = count_sentences(article_text)
            print(f"The article has {result} sentence(s).")

        elif choice == "6":
            print("Goodbye!")
            running = False

        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
