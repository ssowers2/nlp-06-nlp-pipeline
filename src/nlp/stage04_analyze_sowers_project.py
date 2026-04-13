# ============================================================
# Section 1. Setup and Imports
# ============================================================

# Counter helps count how many times each token appears.
from collections import Counter

# logging lets us write progress messages to the terminal/log file.
import logging

# Path helps us work with file paths like data/processed.
from pathlib import Path

# matplotlib is used to create and save figures.
import matplotlib.pyplot as plt

# pandas is used because this stage receives a DataFrame.
import pandas as pd

# squarify creates treemap charts.
import squarify

# WordCloud creates a word cloud visualization from text.
from wordcloud import WordCloud

# ============================================================
# Section 2. Define Helper Functions
# ============================================================


def _plot_top_tokens(
    tokens: list[str],
    top_n: int,
    output_path: Path,
    title: str,
    LOG: logging.Logger,
) -> None:
    """
    Create and save a treemap of the top N most frequent tokens.

    Args:
        tokens: List of cleaned tokens from the text.
        top_n: Number of top tokens to show.
        output_path: File path where the treemap image will be saved.
        title: Title shown on the figure.
        LOG: Logger used to print progress messages.
    """

    # Count how many times each token appears.
    counter = Counter(tokens)

    # Keep only the top N most common tokens.
    # Example: [("guitar", 8), ("repair", 5), ...]
    most_common = counter.most_common(top_n)

    # If there are no tokens, stop here and log a warning.
    if not most_common:
        LOG.warning("No tokens to plot.")
        return

    # Build labels for the treemap boxes.
    # Each box will show the word and its count on two lines.
    labels = [f"{word}\n{count}" for word, count in most_common]

    # Extract only the counts because treemap box size is based on frequency.
    counts = [count for _, count in most_common]

    # Create a figure and axis for the treemap.
    fig, ax = plt.subplots(figsize=(12, 7))

    # Create a purple color gradient for the treemap boxes.
    # The values must be between 0 and 1, so we normalize them.
    max_count = max(counts)
    colors = plt.cm.Purples([count / max_count for count in counts])

    # Draw the treemap.
    # sizes controls box size, label shows the text inside each box.
    squarify.plot(
        sizes=counts,
        label=labels,
        alpha=0.8,
        color=colors,
        edgecolor="black",
        linewidth=2,
        ax=ax,
    )

    # Add a bold title to the figure.
    ax.set_title(title, fontweight="bold", fontsize=14)

    # Turn off axes because treemaps do not need x/y axes.
    ax.axis("off")

    # Tight layout helps prevent labels and title from getting cut off.
    plt.tight_layout()

    # Save the image to the output path.
    plt.savefig(output_path, dpi=150)

    # Close the figure to free memory and prevent blank/overlapping future plots.
    plt.close()

    # Log where the treemap was saved.
    LOG.info(f"  Saved treemap to {output_path}")


def _plot_wordcloud(
    text: str,
    output_path: Path,
    title: str,
    LOG: logging.Logger,
) -> None:
    """
    Generate and save a word cloud from cleaned text.

    Args:
        text: Space-joined cleaned text.
        output_path: File path where the word cloud image will be saved.
        title: Title shown on the figure.
        LOG: Logger used to print progress messages.
    """

    # If there is no usable text, stop here.
    if not text or text == "unknown":
        LOG.warning("No text available for word cloud.")
        return

    # Create the word cloud object.
    # width/height control image size.
    # background_color sets the background.
    # max_words limits how many words appear.
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        max_words=80,
        colormap="viridis",
    ).generate(text)

    # Create the figure that will hold the word cloud image.
    fig, ax = plt.subplots(figsize=(12, 6))

    # Display the generated word cloud.
    ax.imshow(wc, interpolation="bilinear")

    # Hide axes for a cleaner image.
    ax.axis("off")

    # Add a title to the figure.
    ax.set_title(title, fontsize=14)

    # Adjust spacing to avoid clipping.
    plt.tight_layout()

    # Save the image.
    plt.savefig(output_path, dpi=150)

    # Close the figure to free memory.
    plt.close()

    # Log where the word cloud was saved.
    LOG.info(f"  Saved word cloud to {output_path}")


# ============================================================
# Section 3. Define Run Analyze Function
# ============================================================


def run_analyze(
    df: pd.DataFrame,
    LOG: logging.Logger,
    output_dir: Path = Path("data/processed"),
    top_n: int = 10,
) -> None:
    """
    Analyze the transformed DataFrame and create visual outputs.

    Args:
        df: The cleaned and analysis-ready DataFrame from Transform.
        LOG: Logger used to print progress messages.
        output_dir: Folder where output images will be saved.
        top_n: Number of most frequent tokens to show.
    """

    # Log the start of the Analyze stage.
    LOG.info("========================")
    LOG.info("STAGE 04: ANALYZE starting...")
    LOG.info("========================")

    # Make sure the output folder exists.
    output_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # Phase 4.1: Extract token list and summary stats from DataFrame
    # ============================================================

    LOG.info("========================")
    LOG.info("PHASE 4.1: Extract tokens and summary statistics")
    LOG.info("========================")

    # Get the first row of the DataFrame.
    # This project uses one webpage/document, so there is only one row.
    row = df.iloc[0]

    # Read values from the DataFrame.
    # If a column is missing, use a safe fallback value.
    title: str = str(row.get("page_title", "unknown"))
    tokens_str: str = str(row.get("tokens", ""))
    token_count: int = int(row.get("token_count", 0))
    unique_token_count: int = int(row.get("unique_token_count", 0))
    type_token_ratio: float = float(row.get("type_token_ratio", 0.0))
    content_word_count: int = int(row.get("content_word_count", 0))

    # The tokens were stored as one long string in the CSV.
    # Split them back into a list so we can count them.
    tokens: list[str] = tokens_str.split() if tokens_str else []

    # Log the main summary statistics.
    LOG.info(f"  Page title:                   {title}")
    LOG.info(f"  Content word count (raw):     {content_word_count}")
    LOG.info(f"  Token count (clean):          {token_count}")
    LOG.info(f"  Unique token count:           {unique_token_count}")
    LOG.info(f"  Type-token ratio:             {type_token_ratio}")

    # ============================================================
    # Phase 4.2: Top token frequency - treemap
    # ============================================================

    LOG.info("========================")
    LOG.info(f"PHASE 4.2: Top {top_n} token frequency - treemap")
    LOG.info("========================")

    # Create and save the treemap image.
    _plot_top_tokens(
        tokens=tokens,
        top_n=top_n,
        output_path=output_dir / "sowers_top_tokens_treemap.png",
        title=f"Top {top_n} Tokens: {title}",
        LOG=LOG,
    )

    # ============================================================
    # Phase 4.3: Word cloud
    # ============================================================

    LOG.info("========================")
    LOG.info("PHASE 4.3: Word cloud")
    LOG.info("========================")

    # Create and save the word cloud image.
    _plot_wordcloud(
        text=tokens_str,
        output_path=output_dir / "sowers_wordcloud_project.png",
        title=f"Word Cloud: {title}",
        LOG=LOG,
    )

    # ============================================================
    # Phase 4.4: Log top tokens for quick inspection
    # ============================================================

    LOG.info("========================")
    LOG.info("PHASE 4.4: Top token summary (inline)")
    LOG.info("========================")

    # Count tokens again so we can print the top ones in ranked order.
    counter = Counter(tokens)
    top_tokens = counter.most_common(top_n)

    # Log the ranked list.
    LOG.info(f"  Top {top_n} tokens by frequency:")
    for rank, (word, count) in enumerate(top_tokens, start=1):
        LOG.info(f"    {rank:>3}. {word:<30} {count}")

    # Final log messages for the Analyze stage.
    LOG.info("Sink: visualizations saved to data/processed/")
    LOG.info("Analysis complete.")
