# ============================================================
# Section 1. Setup and Imports
# ============================================================

# logging is used to print messages during the pipeline run
import logging

# re is used for cleaning text (removing extra spaces, etc.)
import re

# string helps remove punctuation
import string

# BeautifulSoup helps parse HTML, Tag represents HTML elements
from bs4 import BeautifulSoup, Tag

# pandas is used to create the final DataFrame
import pandas as pd

# spaCy is used for NLP tasks like tokenization and stopword removal
import spacy

# Load the English language model (used in cleaning)
nlp = spacy.load("en_core_web_sm")


# ============================================================
# Section 2. Define Helper Functions
# ============================================================


def _get_text(element: Tag | None, separator: str = " ") -> str:
    """
    Get text from an HTML element.
    If the element is missing, return "unknown".
    """
    # If the HTML element does not exist, return a default value
    if element is None:
        return "unknown"

    # Extract text from the element and clean spacing
    return element.get_text(separator=separator, strip=True)


def _clean_text(text: str, nlp_model: spacy.language.Language) -> str:
    """
    Clean text so it is ready for NLP analysis.
    """

    # Step 1: Convert all text to lowercase
    text = text.lower()

    # Step 2: Remove punctuation (commas, periods, etc.)
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Step 3: Normalize whitespace (remove extra spaces/newlines)
    text = re.sub(r"\s+", " ", text).strip()

    # Step 4: Use spaCy to remove stopwords (common words like "the", "and")
    doc = nlp_model(text)
    text = " ".join(
        [token.text for token in doc if token.is_alpha and not token.is_stop]
    )

    return text


# ============================================================
# Section 3. Define Run Transform Function
# ============================================================


def run_transform(
    soup: BeautifulSoup,
    LOG: logging.Logger,
) -> pd.DataFrame:
    """
    Convert raw HTML into a clean DataFrame ready for analysis.
    """

    # Log that the transform stage is starting
    LOG.info("========================")
    LOG.info("STAGE 03: TRANSFORM starting...")
    LOG.info("========================")

    LOG.info("Extracting content from website HTML")

    # ============================================================
    # PHASE 3.1: Extract raw fields from HTML
    # ============================================================

    LOG.info("========================")
    LOG.info("PHASE 3.1: Extract raw fields from HTML")
    LOG.info("========================")

    # Find the main title of the webpage (usually in <h1>)
    title_tag: Tag | None = soup.find("h1")

    # Extract the text from the title
    page_title: str = _get_text(title_tag)
    LOG.info(f"Extracted title: {page_title}")

    # Find all paragraph tags (<p>) on the page
    paragraph_tags: list[Tag] = soup.find_all("p")

    # Extract text from each paragraph
    paragraphs: list[str] = [p.get_text(" ", strip=True) for p in paragraph_tags]

    # Combine all paragraph text into one long string
    content_raw: str = " ".join(paragraphs) if paragraphs else "unknown"

    LOG.info(f"Extracted paragraph count: {len(paragraph_tags)}")
    LOG.info(f"Extracted content preview: {content_raw[:120]}...")

    # ============================================================
    # PHASE 3.2: Clean and normalize text fields
    # ============================================================

    LOG.info("========================")
    LOG.info("PHASE 3.2: Clean and normalize text fields")
    LOG.info("========================")

    # Clean the raw text using the helper function
    content_clean: str = (
        _clean_text(content_raw, nlp) if content_raw != "unknown" else "unknown"
    )

    # Log before and after cleaning to show changes
    LOG.info(f"  content (raw):   {content_raw[:120]}...")
    LOG.info(f"  content (clean): {content_clean[:120]}...")

    # Show how much text was removed during cleaning
    LOG.info(
        f"  characters removed: {len(content_raw) - len(content_clean)} "
        f"({100 * (1 - len(content_clean) / max(len(content_raw), 1)):.1f}%)"
    )

    # ============================================================
    # PHASE 3.3: Engineer derived features
    # ============================================================

    LOG.info("========================")
    LOG.info("PHASE 3.3: Engineer derived features")
    LOG.info("========================")

    # Count total words in raw content
    content_word_count: int = (
        len(content_raw.split()) if content_raw != "unknown" else 0
    )

    # Split cleaned text into tokens (words)
    tokens: list[str] = content_clean.split() if content_clean != "unknown" else []

    # Count total number of tokens
    token_count: int = len(tokens)

    # Count unique tokens (vocabulary size)
    unique_token_count: int = len(set(tokens))

    # Calculate type-token ratio (vocabulary richness)
    type_token_ratio: float = (
        round(unique_token_count / token_count, 4) if token_count > 0 else 0.0
    )

    # Log all computed metrics
    LOG.info(f"  content_word_count: {content_word_count}")
    LOG.info(f"  token_count:        {token_count}")
    LOG.info(f"  unique_token_count: {unique_token_count}")
    LOG.info(f"  type_token_ratio:   {type_token_ratio}")

    # Show a preview of tokens
    LOG.info(f"  top 10 tokens:      {tokens[:10]}")

    # ============================================================
    # PHASE 3.4: Build record and create DataFrame
    # ============================================================

    LOG.info("========================")
    LOG.info("PHASE 3.4: Build record and create DataFrame")
    LOG.info("========================")

    # Create a dictionary (one row of data)
    record = {
        "page_title": page_title,
        "content_raw": content_raw,
        "content_clean": content_clean,
        "tokens": " ".join(tokens),
        "content_word_count": content_word_count,
        "token_count": token_count,
        "unique_token_count": unique_token_count,
        "type_token_ratio": type_token_ratio,
    }

    # Convert the dictionary into a pandas DataFrame
    df = pd.DataFrame([record])

    # Log DataFrame details
    LOG.info(f"Created DataFrame with {len(df)} row and {len(df.columns)} columns")
    LOG.info(f"Columns: {list(df.columns)}")

    LOG.info("Sink: Pandas DataFrame created")
    LOG.info("Transformation complete.")

    # Return the DataFrame for the next stage (Analyze)
    return df
