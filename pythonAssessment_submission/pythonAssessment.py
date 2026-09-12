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

Author: Echo (Gladys Mwake)
"""

import os                          # file path handling
import re                          # regex: word extraction, sentence/paragraph splitting
import string                      # provides string.punctuation for cleaning words
from collections import Counter    # efficient way to find the most frequent word

# Optional native GUI file picker via Tkinter (Python standard library).
# Falls back gracefully to standard console input if unavailable or headless.
try:
    import tkinter as tk
    from tkinter import filedialog
    _TKINTER_AVAILABLE = True
except ImportError:
    _TKINTER_AVAILABLE = False


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
    # block but the text clearly has more than one line, we try to decide
    # whether each line is its own paragraph OR whether the text is simply
    # hard-wrapped at a fixed column width.
    #
    # Heuristic: in a one-paragraph-per-line file, each line tends to END
    # with sentence-closing punctuation (. ! ? or a closing quote/bracket).
    # In a hard-wrapped file, most lines end mid-sentence (no punctuation)
    # and only the LAST line of the paragraph ends with punctuation.
    # If more than half the lines end with closing punctuation we treat
    # each line as its own paragraph; otherwise we assume hard-wrapped text
    # and return 1 (a single paragraph) instead of over-counting.
    if len(paragraphs) <= 1 and "\n" in stripped_text:
        line_based_paragraphs = [
            line for line in stripped_text.split("\n") if line.strip()
        ]
        if len(line_based_paragraphs) > 1:
            ends_with_punct = sum(
                1 for line in line_based_paragraphs
                if re.search(r'[.!?"\u2019\u201d]\s*$', line.strip())
            )
            fraction = ends_with_punct / len(line_based_paragraphs)
            if fraction > 0.5:
                # Most lines close with punctuation -> one paragraph per line.
                return len(line_based_paragraphs)
            # else: hard-wrapped text -> fall through and return 1.

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
        - A period after a SHORT token (1-5 chars) followed by a lowercase
          word, e.g. "misc. items".  Only SHORT tokens are protected here
          because real abbreviations are almost always short (misc, dept,
          est, vs) while words that genuinely end a sentence (technology,
          closed, market) are long.  This avoids the previous weakness
          where a period after any word followed by a lowercase sentence
          starter (e.g. "...closed. eBay then...") was falsely protected.
    This is a heuristic, not a full grammar parser -- it covers the vast
    majority of real news-article cases without requiring a complete
    abbreviation list.

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

    # Protect a SHORT token (1-5 chars) followed by a period then a
    # lowercase word, e.g. "misc. items" -> "misc<PERIOD> items".
    # Capped at 5 chars so long words like "closed" or "market" still
    # act as genuine sentence boundaries even when the next word starts
    # lowercase (e.g. "...market. eBay then announced...").
    working_text = re.sub(r"\b(\w{1,5})\.(?=\s+[a-z])", r"\1<PERIOD>", working_text)

    sentences = re.split(r"[.!?]+", working_text)
    sentences = [s for s in sentences if s.strip()]

    return len(sentences) if sentences else 1


# --------------------------------------------------------------------------- #
# Menu-driven program (multi-file edition)
# --------------------------------------------------------------------------- #
MENU_OPTIONS = [
    ("1", "Count how many times a specific word appears"),
    ("2", "Identify the most common word"),
    ("3", "Calculate the average word length"),
    ("4", "Count the number of paragraphs"),
    ("5", "Count the number of sentences"),
    ("6", "Compare this result with another loaded article"),
    ("7", "Switch active article"),
    ("8", "Load an additional article"),
    ("9", "Show all loaded articles"),
    ("0", "Exit"),
]


def display_menu(active_label):
    """Print the list of available text-analysis options."""
    print(f"\n--- News Article Analyzer  [Active: {active_label}] ---")
    for option_number, description in MENU_OPTIONS:   # for loop (rubric)
        print(f"{option_number}. {description}")


def browse_for_files(title="Select article file(s)"):
    """
    Open a native OS file dialog allowing single or multi-file selection.

    Returns:
        list[str]: Selected file paths, or an empty list if cancelled / unavailable.
    """
    if not _TKINTER_AVAILABLE:
        return []
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askopenfilenames(
            title=title,
            filetypes=[
                ("Text files (*.txt)", "*.txt"),
                ("All files (*.*)", "*.*"),
            ],
        )
        root.destroy()
        return list(selected) if selected else []
    except Exception:
        return []


def browse_for_file(title="Select an article file"):
    """
    Open a native OS file dialog to pick a single file.

    Returns:
        str: Selected file path, or empty string if cancelled / unavailable.
    """
    files = browse_for_files(title=title)
    return files[0] if files else ""


def load_articles_at_startup():
    """
    Ask the user how many articles to load, then collect a file path
    (and optional label) for each one. Supports selecting files directly
    from File Explorer via a native GUI dialog, as well as typing paths.

    Returns:
        list[dict]: Each element is {"label": str, "text": str}.
                    The list contains only successfully loaded articles.
    """
    articles = []

    # If GUI file picker is available, offer it upfront
    if _TKINTER_AVAILABLE:
        print("Choose how to load article files:")
        print("  1. Browse and select file(s) using File Explorer")
        print("  2. Type file path(s) manually")
        entry_method = input("Enter your choice (1 or 2, default: 1): ").strip()
        if entry_method in ("", "1"):
            print("Opening File Explorer dialog... (you can select multiple files with Ctrl/Shift)")
            chosen_paths = browse_for_files("Select one or more article text files")
            if chosen_paths:
                print(f"\nSelected {len(chosen_paths)} file(s) from File Explorer.")
                for path in chosen_paths:
                    filename = os.path.basename(path)
                    label_input = input(
                        f"  Short label for '{filename}' (press Enter to keep '{filename}'): "
                    ).strip()
                    label = label_input if label_input else filename
                    text = read_article(path)
                    if text:                           # if/else (rubric)
                        articles.append({"label": label, "text": text})
                        print("  Loaded successfully.")
                    else:
                        print(f"  Could not load file '{path}' - skipping.")
                if articles:
                    return articles
                print("None of the selected files could be read. Falling back to manual entry.\n")
            else:
                print("No files were selected. Falling back to manual entry.\n")

    # Manual path entry (or fallback)
    while True:                                        # while loop (rubric)
        raw = input("How many article files do you want to load? ").strip()
        if raw.isdigit() and int(raw) >= 1:
            count = int(raw)
            break
        print("Please enter a whole number of 1 or more.")

    for i in range(1, count + 1):                     # for loop (rubric)
        print(f"\n--- Article {i} of {count} ---")
        prompt = "  File path (or type 'B' to browse): " if _TKINTER_AVAILABLE else "  File path: "
        file_path = input(prompt).strip()
        if _TKINTER_AVAILABLE and file_path.lower() == "b":
            file_path = browse_for_file(f"Select article {i} of {count}")
            if file_path:
                print(f"  Selected: {file_path}")
            else:
                file_path = input("  No file selected. Please enter file path manually: ").strip()

        default_label = os.path.basename(file_path) if file_path else f"Article {i}"
        label_input = input(
            f"  Short label (press Enter to use '{default_label}'): "
        ).strip()
        label = label_input if label_input else default_label

        text = read_article(file_path)
        if text:                                       # if/else (rubric)
            articles.append({"label": label, "text": text})
            print("  Loaded successfully.")
        else:
            print("  Could not load file - skipping.")

    return articles


def pick_article(articles, prompt="Choose an article by number: "):
    """
    Show a numbered list of loaded articles and return the chosen one.

    Args:
        articles (list[dict]): The loaded articles.
        prompt (str): The input prompt to display.

    Returns:
        dict | None: The chosen article dict, or None if the choice was invalid.
    """
    for idx, article in enumerate(articles, 1):        # for loop
        print(f"  {idx}. {article['label']}")
    raw = input(prompt).strip()
    if raw.isdigit() and 1 <= int(raw) <= len(articles):
        return articles[int(raw) - 1]
    print("Invalid selection.")
    return None


def compare_result(func, articles, active_article, func_name, **kwargs):
    """
    Run func on the active article AND a user-chosen second article,
    then print both results side-by-side.

    Args:
        func: One of the five analysis functions.
        articles (list[dict]): All loaded articles.
        active_article (dict): The currently active article.
        func_name (str): Human-readable name for the display line.
        **kwargs: Extra keyword arguments forwarded to func.
    """
    others = [a for a in articles if a is not active_article]
    if not others:                                     # if/else
        print("Only one article is loaded - nothing to compare with.")
        return

    print("\nChoose the article to compare against:")
    second = pick_article(others)
    if second is None:
        return

    result_a = func(active_article["text"], **kwargs)
    result_b = func(second["text"], **kwargs)

    label_a = active_article["label"]
    label_b = second["label"]
    width = max(len(label_a), len(label_b), 40)
    print(f"\n  {func_name}")
    print(f"  {label_a:<{width}}  {result_a}")
    print(f"  {label_b:<{width}}  {result_b}")


def main():
    """Run the interactive multi-article news analyzer."""
    print("=== News Article Analyzer ===\n")
    articles = load_articles_at_startup()

    if not articles:                                   # if/else (rubric)
        print("No articles could be loaded. Exiting.")
        return

    active = articles[0]
    print(f"\nActive article set to: '{active['label']}'")

    running = True
    while running:                                     # while loop (rubric)
        display_menu(active["label"])
        choice = input("Choose an option (0-9): ").strip()

        if choice == "1":                              # if/elif/else (rubric)
            word = input("Enter the word to search for: ").strip()
            result = count_specific_word(active["text"], word)
            print(f"  The word appears {result} time(s).")

        elif choice == "2":
            result = identify_most_common_word(active["text"])
            print(f"  Most common word: {result}")

        elif choice == "3":
            result = calculate_average_word_length(active["text"])
            print(f"  Average word length: {result:.2f} characters")

        elif choice == "4":
            result = count_paragraphs(active["text"])
            print(f"  Paragraph count: {result}")

        elif choice == "5":
            result = count_sentences(active["text"])
            print(f"  Sentence count: {result}")

        elif choice == "6":
            print("\nWhat would you like to compare?")
            compare_options = [
                ("1", "Word count for a specific word"),
                ("2", "Most common word"),
                ("3", "Average word length"),
                ("4", "Number of paragraphs"),
                ("5", "Number of sentences"),
            ]
            for opt, desc in compare_options:          # for loop
                print(f"  {opt}. {desc}")
            sub = input("Choose (1-5): ").strip()

            if sub == "1":                             # if/elif/else
                word = input("Enter the word to compare: ").strip()
                compare_result(
                    count_specific_word, articles, active,
                    f"Count of word", word=word,
                )
            elif sub == "2":
                compare_result(
                    identify_most_common_word, articles, active,
                    "Most common word",
                )
            elif sub == "3":
                compare_result(
                    calculate_average_word_length, articles, active,
                    "Average word length",
                )
            elif sub == "4":
                compare_result(
                    count_paragraphs, articles, active,
                    "Paragraph count",
                )
            elif sub == "5":
                compare_result(
                    count_sentences, articles, active,
                    "Sentence count",
                )
            else:
                print("Invalid sub-choice.")

        elif choice == "7":
            print("\nSwitch to which article?")
            chosen = pick_article(articles)
            if chosen:                                 # if/else
                active = chosen
                print(f"  Active article is now: '{active['label']}'")

        elif choice == "8":
            file_path = ""
            if _TKINTER_AVAILABLE:
                method = input("Load via File Explorer [B]rowse or [T]ype path? (B/t): ").strip().lower()
                if method != "t":
                    file_path = browse_for_file("Select an article file")
                    if file_path:
                        print(f"  Selected: {file_path}")
            if not file_path:
                file_path = input("File path of new article: ").strip()

            default_label = os.path.basename(file_path) if file_path else "New Article"
            label_input = input(
                f"Short label (press Enter to use '{default_label}'): "
            ).strip()
            label = label_input if label_input else default_label
            text = read_article(file_path)
            if text:                                   # if/else
                new_article = {"label": label, "text": text}
                articles.append(new_article)
                print("  Loaded. Switching to it as active.")
                active = new_article
            else:
                print("  Could not load that file.")

        elif choice == "9":
            print(f"\n  {len(articles)} article(s) loaded:")
            for idx, article in enumerate(articles, 1):  # for loop
                marker = " <- active" if article is active else ""
                print(f"    {idx}. {article['label']}{marker}")

        elif choice == "0":
            print("Goodbye!")
            running = False

        else:
            print("Invalid choice. Please enter a number from 0 to 9.")


if __name__ == "__main__":
    main()
