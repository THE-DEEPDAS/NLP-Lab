"""
Assignment-2 Q2: Frequency distribution and stopword removal plots.

- Input: indiccorp_gu_words.txt (tokenized words, whitespace-separated; UTF-8)
- No predefined frequency libraries (manual dict counting)
- Outputs:
  - freq_top100.png, freq_top100.csv
  - For thresholds T in [5, 10, 20] (configurable):
      freq_after_stop_T_top100.png, freq_after_stop_T_top100.csv

If matplotlib is unavailable, CSVs are still written.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


DEFAULT_INPUT_NAME = "indiccorp_gu_words.txt"
DEFAULT_THRESHOLDS = [5, 10, 20]
TOP_N = 100


def find_input_file() -> Path | None:
    here = Path(__file__).resolve().parent
    candidates = [
        here / DEFAULT_INPUT_NAME,
        here.parent / DEFAULT_INPUT_NAME,
        here.parent / "Lab 1" / DEFAULT_INPUT_NAME,
        here.parent / "Lab 3" / DEFAULT_INPUT_NAME,
        Path.cwd() / DEFAULT_INPUT_NAME,
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def read_tokens(fp: Path) -> Iterable[str]:
    with fp.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # Allow both one-token-per-line and whitespace-separated tokens
            for tok in line.strip().split():
                t = tok.strip()
                if t:
                    yield t


def count_frequencies(tokens: Iterable[str]) -> Dict[str, int]:
    freq: Dict[str, int] = {}
    for t in tokens:
        # manual counting (no Counter)
        if t in freq:
            freq[t] += 1
        else:
            freq[t] = 1
    return freq


def top_k(freq: Dict[str, int], k: int) -> List[Tuple[str, int]]:
    # sort by frequency desc, then lexicographically for stability
    return sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def write_csv(rows: List[Tuple[str, int]], out_path: Path) -> None:
    lines = ["word,frequency"] + [f"{w},{c}" for w, c in rows]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def plot_bar(rows: List[Tuple[str, int]], title: str, out_path: Path) -> bool:
    try:
        import matplotlib.pyplot as plt  # type: ignore

        words = [w for w, _ in rows]
        counts = [c for _, c in rows]
        width = 0.9
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.bar(range(len(words)), counts, width=width, color="#4C78A8")
        ax.set_title(title)
        ax.set_xlabel("Words")
        ax.set_ylabel("Frequency")
        ax.set_xticks(range(len(words)))
        # Show every Nth x-tick label to avoid clutter
        step = max(1, len(words) // 25)
        ax.set_xticklabels([w if i % step == 0 else "" for i, w in enumerate(words)], rotation=45, ha="right")
        fig.tight_layout()
        fig.savefig(str(out_path), dpi=150)
        plt.close(fig)
        return True
    except Exception:
        return False


def remove_stopwords_by_threshold(freq: Dict[str, int], threshold: int) -> Dict[str, int]:
    # Treat words with frequency >= threshold as stopwords and remove them
    return {w: c for w, c in freq.items() if c < threshold}


def main() -> None:
    inp = find_input_file()
    if not inp:
        print(
            f"Input file '{DEFAULT_INPUT_NAME}' not found in expected locations.\n"
            f"Place it next to this script or in the workspace root/Lab 1 and re-run."
        )
        return

    print(f"Reading tokens from: {inp}")
    freq = count_frequencies(read_tokens(inp))
    total_tokens = sum(freq.values())
    vocab_size = len(freq)
    print(f"Total tokens: {total_tokens}; Vocabulary size: {vocab_size}")

    # Top-N overall
    top_rows = top_k(freq, TOP_N)
    csv_path = Path(__file__).with_name("freq_top100.csv")
    img_path = Path(__file__).with_name("freq_top100.png")
    write_csv(top_rows, csv_path)
    plotted = plot_bar(top_rows, f"Top {len(top_rows)} words (overall)", img_path)
    print(f"Wrote {csv_path}")
    print(f"Wrote {img_path}" if plotted else "matplotlib not available; plot skipped")

    # Thresholded stopword removal and plots
    for T in DEFAULT_THRESHOLDS:
        pruned = remove_stopwords_by_threshold(freq, T)
        top_rows_T = top_k(pruned, TOP_N)
        csv_T = Path(__file__).with_name(f"freq_after_stop_{T}_top100.csv")
        img_T = Path(__file__).with_name(f"freq_after_stop_{T}_top100.png")
        write_csv(top_rows_T, csv_T)
        plotted_T = plot_bar(top_rows_T, f"Top {len(top_rows_T)} after removing stopwords (freq >= {T})", img_T)
        print(f"Threshold {T}: kept {len(pruned)} words; wrote {csv_T}")
        print(f"Threshold {T}: wrote {img_T}" if plotted_T else f"Threshold {T}: matplotlib not available; plot skipped")


if __name__ == "__main__":
    main()
