"""
Downward Mobility Qualitative Coding Sample

This beginner-friendly project demonstrates a reproducible first-pass screening
workflow for qualitative interview excerpts from a downward mobility research
context.

Research context
----------------
The broader project studies unemployed or re-employed workers' experiences of
downward economic mobility in the United States. In the actual research process,
final coding decisions require close reading, attention to interview context,
and researcher judgment.

What this script does
---------------------
1. Reads interview excerpts from a CSV file.
2. Searches for candidate evidence of two focal interpretive concepts:
   - social_solidarity
   - meritocratic_individualism
3. Adds descriptive flags such as age, race, gender, education, class, and
   structural barriers.
4. Produces several outputs that support manual review:
   - coded_excerpts.csv
   - theme_summary.csv
   - code_cooccurrence.csv
   - manual_review_queue.csv
   - coding_report.md

Important limitation
--------------------
This script does not replace NVivo-style interpretive coding. Keyword and phrase
matching can only identify candidate excerpts. The final decision about whether
an excerpt truly reflects social solidarity or meritocratic individualism must
be made through manual contextual review.

Example
-------
python3 downward_mobility_text_coding_sample.py

Optional:
python3 downward_mobility_text_coding_sample.py --input sample_interviews.csv --output-dir outputs
"""

from collections import Counter
import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import re


DEFAULT_INPUT = Path("sample_interviews.csv")
DEFAULT_OUTPUT_DIR = Path("outputs")


FOCAL_CODEBOOK = {
    "meritocratic_individualism": [
        "work harder",
        "my fault",
        "personal responsibility",
        "should have",
        "try harder",
        "better choices",
        "blame myself",
        "pulled myself up",
        "didn't do enough",
        "up to me",
        "depends on me",
        "depends on myself",
        "individual success",
        "personal success",
        "individual effort",
        "personal effort",
        "my own effort",
    ],
    "social_solidarity": [
        "support",
        "community",
        "union",
        "help each other",
        "shared struggle",
        "not alone",
        "collective",
        "our generation",
        "people like us",
        "as men",
        "as women",
        "as a man",
        "as a woman",
    ],
}


DESCRIPTIVE_FLAGS = {
    "age": [
        "young",
        "older",
        "age",
        "retirement",
        "middle-aged",
    ],
    "race": [
        "race",
        "racial",
        "black",
        "white",
        "latino",
        "asian",
    ],
    "gender": [
        "gender",
        "woman",
        "women",
        "man",
        "men",
        "mother",
        "father",
    ],
    "education": [
        "college",
        "degree",
        "school",
        "education",
        "credential",
    ],
    "class": [
        "middle class",
        "working class",
        "class",
        "status",
        "income",
    ],
    "structural_barriers": [
        "economy",
        "recession",
        "industry changed",
        "outsourcing",
        "automation",
        "no openings",
        "health insurance",
        "childcare",
    ],
}


DEMO_EXCERPTS = [
    {
        "participant_id": "P01",
        "excerpt_id": "E01",
        "excerpt": (
            "After I was laid off, I took a lower pay job outside my old field. "
            "At first I blamed myself and thought I should have made better "
            "choices before the industry changed."
        ),
    },
    {
        "participant_id": "P02",
        "excerpt_id": "E02",
        "excerpt": (
            "The industry changed so quickly that there were no openings near me. "
            "My coworkers and I talked about it as a shared struggle for our "
            "generation."
        ),
    },
    {
        "participant_id": "P03",
        "excerpt_id": "E03",
        "excerpt": (
            "Losing health insurance made it hard to switch careers. Support "
            "from my family helped, but I still felt like I had lost middle "
            "class status. I kept thinking my future depended on my own effort."
        ),
    },
    {
        "participant_id": "P04",
        "excerpt_id": "E04",
        "excerpt": (
            "As a woman, I felt that people like us were expected to stay quiet "
            "and just keep working. The union meeting was the first place where "
            "I felt I was not alone."
        ),
    },
    {
        "participant_id": "P05",
        "excerpt_id": "E05",
        "excerpt": (
            "I kept telling myself that individual success comes from personal "
            "effort, but after months of applications I started to wonder how "
            "much the economy was shaping my options."
        ),
    },
]


@dataclass
class MatchResult:
    labels: list[str]
    matched_terms: dict[str, list[str]]


def normalize_text(text):
    """Lowercase text and remove extra spaces for consistent matching."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def phrase_is_present(phrase, text):
    """
    Match a phrase in a normalized text.

    Word boundaries reduce false matches for single words. Phrase matching is
    still imperfect, which is why every result is marked for manual review.
    """
    normalized_phrase = normalize_text(phrase)
    pattern = r"(?<!\w)" + re.escape(normalized_phrase) + r"(?!\w)"
    return re.search(pattern, text) is not None


def find_matches(excerpt, codebook):
    """Return matched labels and the exact terms that triggered each match."""
    cleaned = normalize_text(excerpt)
    labels = []
    matched_terms = {}

    for label, terms in codebook.items():
        label_terms = [term for term in terms if phrase_is_present(term, cleaned)]
        if label_terms:
            labels.append(label)
            matched_terms[label] = label_terms

    return MatchResult(labels=labels, matched_terms=matched_terms)


def calculate_confidence(focal_matches, flag_matches):
    """
    Produce a simple screening confidence label.

    This is not a statistical confidence score. It is only a practical review
    cue: excerpts with more matched focal terms should be reviewed first.
    """
    focal_term_count = sum(len(terms) for terms in focal_matches.matched_terms.values())
    flag_count = len(flag_matches.labels)

    if focal_term_count >= 2:
        return "medium"
    if focal_term_count == 1 and flag_count >= 1:
        return "low-medium"
    if focal_term_count == 1:
        return "low"
    return "none"


def review_priority(confidence):
    """Rank excerpts for manual review."""
    priority_map = {
        "medium": "review_first",
        "low-medium": "review_next",
        "low": "review_if_time",
        "none": "background_only",
    }
    return priority_map[confidence]


def read_excerpts(path):
    """Read excerpts from a CSV file, or use demo excerpts if no file exists."""
    if not path.exists():
        return DEMO_EXCERPTS

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    required_columns = {"participant_id", "excerpt"}
    missing_columns = required_columns.difference(reader.fieldnames or [])
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Input CSV is missing required column(s): {missing}")

    for index, row in enumerate(rows, start=1):
        if not row.get("excerpt_id"):
            row["excerpt_id"] = f"E{index:03d}"

    return rows


def format_labels(labels):
    return "; ".join(labels) if labels else "none_found"


def format_matched_terms(matched_terms):
    if not matched_terms:
        return "none_found"

    parts = []
    for label, terms in matched_terms.items():
        parts.append(f"{label}: {', '.join(terms)}")
    return " | ".join(parts)


def code_excerpts(excerpts):
    """Apply first-pass screening to all excerpts."""
    coded_rows = []

    for row in excerpts:
        focal_matches = find_matches(row["excerpt"], FOCAL_CODEBOOK)
        flag_matches = find_matches(row["excerpt"], DESCRIPTIVE_FLAGS)
        confidence = calculate_confidence(focal_matches, flag_matches)

        coded_rows.append(
            {
                "participant_id": row["participant_id"],
                "excerpt_id": row.get("excerpt_id", ""),
                "excerpt": row["excerpt"],
                "candidate_focal_codes": format_labels(focal_matches.labels),
                "focal_matched_terms": format_matched_terms(
                    focal_matches.matched_terms
                ),
                "descriptive_flags": format_labels(flag_matches.labels),
                "flag_matched_terms": format_matched_terms(flag_matches.matched_terms),
                "screening_confidence": confidence,
                "review_priority": review_priority(confidence),
                "needs_manual_review": "yes",
                "manual_review_note": (
                    "Preliminary keyword result; final coding requires contextual "
                    "reading."
                ),
            }
        )

    return coded_rows


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_coded_excerpts(output_dir, coded_rows):
    fieldnames = [
        "participant_id",
        "excerpt_id",
        "excerpt",
        "candidate_focal_codes",
        "focal_matched_terms",
        "descriptive_flags",
        "flag_matched_terms",
        "screening_confidence",
        "review_priority",
        "needs_manual_review",
        "manual_review_note",
    ]
    write_csv(output_dir / "coded_excerpts.csv", fieldnames, coded_rows)


def summarize_categories(coded_rows):
    focal_counts = Counter()
    flag_counts = Counter()

    for row in coded_rows:
        if row["candidate_focal_codes"] != "none_found":
            focal_counts.update(row["candidate_focal_codes"].split("; "))
        if row["descriptive_flags"] != "none_found":
            flag_counts.update(row["descriptive_flags"].split("; "))

    summary_rows = []
    for code, count in focal_counts.most_common():
        summary_rows.append(
            {
                "category_type": "candidate_focal_code",
                "category": code,
                "excerpt_count": count,
            }
        )
    for flag, count in flag_counts.most_common():
        summary_rows.append(
            {
                "category_type": "descriptive_flag",
                "category": flag,
                "excerpt_count": count,
            }
        )

    return summary_rows


def write_theme_summary(output_dir, summary_rows):
    fieldnames = ["category_type", "category", "excerpt_count"]
    write_csv(output_dir / "theme_summary.csv", fieldnames, summary_rows)


def build_cooccurrence_rows(coded_rows):
    pair_counts = Counter()

    for row in coded_rows:
        focal_codes = []
        flags = []

        if row["candidate_focal_codes"] != "none_found":
            focal_codes = row["candidate_focal_codes"].split("; ")
        if row["descriptive_flags"] != "none_found":
            flags = row["descriptive_flags"].split("; ")

        for focal_code in focal_codes:
            for flag in flags:
                pair_counts[(focal_code, flag)] += 1

    return [
        {
            "candidate_focal_code": focal_code,
            "descriptive_flag": flag,
            "cooccurring_excerpt_count": count,
        }
        for (focal_code, flag), count in pair_counts.most_common()
    ]


def write_cooccurrence(output_dir, cooccurrence_rows):
    fieldnames = [
        "candidate_focal_code",
        "descriptive_flag",
        "cooccurring_excerpt_count",
    ]
    write_csv(output_dir / "code_cooccurrence.csv", fieldnames, cooccurrence_rows)


def write_manual_review_queue(output_dir, coded_rows):
    review_rows = [
        row
        for row in coded_rows
        if row["candidate_focal_codes"] != "none_found"
        or row["descriptive_flags"] != "none_found"
    ]

    priority_order = {
        "review_first": 1,
        "review_next": 2,
        "review_if_time": 3,
        "background_only": 4,
    }
    review_rows.sort(key=lambda row: priority_order[row["review_priority"]])

    fieldnames = [
        "participant_id",
        "excerpt_id",
        "excerpt",
        "candidate_focal_codes",
        "focal_matched_terms",
        "descriptive_flags",
        "screening_confidence",
        "review_priority",
        "manual_review_note",
    ]
    write_csv(output_dir / "manual_review_queue.csv", fieldnames, review_rows)


def write_markdown_report(output_dir, coded_rows, summary_rows, cooccurrence_rows):
    focal_hits = sum(
        1 for row in coded_rows if row["candidate_focal_codes"] != "none_found"
    )
    flag_hits = sum(1 for row in coded_rows if row["descriptive_flags"] != "none_found")

    lines = [
        "# Coding Report",
        "",
        "This report summarizes a first-pass qualitative screening workflow.",
        "",
        "## Overview",
        "",
        f"- Total excerpts screened: {len(coded_rows)}",
        f"- Excerpts with candidate focal codes: {focal_hits}",
        f"- Excerpts with descriptive flags: {flag_hits}",
        "",
        "## Category Summary",
        "",
        "| Category Type | Category | Excerpt Count |",
        "| --- | --- | ---: |",
    ]

    for row in summary_rows:
        lines.append(
            f"| {row['category_type']} | {row['category']} | {row['excerpt_count']} |"
        )

    lines.extend(
        [
            "",
            "## Co-occurrence Summary",
            "",
            "| Candidate Focal Code | Descriptive Flag | Excerpt Count |",
            "| --- | --- | ---: |",
        ]
    )

    if cooccurrence_rows:
        for row in cooccurrence_rows:
            lines.append(
                "| "
                f"{row['candidate_focal_code']} | "
                f"{row['descriptive_flag']} | "
                f"{row['cooccurring_excerpt_count']} |"
            )
    else:
        lines.append("| none | none | 0 |")

    lines.extend(
        [
            "",
            "## Methodological Note",
            "",
            "The script uses keyword and phrase matching to identify candidate excerpts. "
            "This is useful for organizing materials, but it cannot determine final "
            "interpretive codes. Excerpts marked by this workflow should be reviewed "
            "manually in context before being used in analysis.",
            "",
        ]
    )

    (output_dir / "coding_report.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(
        description="First-pass qualitative coding sample for downward mobility excerpts."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to an input CSV with participant_id and excerpt columns.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where output files will be saved.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    excerpts = read_excerpts(input_path)
    coded_rows = code_excerpts(excerpts)
    summary_rows = summarize_categories(coded_rows)
    cooccurrence_rows = build_cooccurrence_rows(coded_rows)

    write_coded_excerpts(output_dir, coded_rows)
    write_theme_summary(output_dir, summary_rows)
    write_cooccurrence(output_dir, cooccurrence_rows)
    write_manual_review_queue(output_dir, coded_rows)
    write_markdown_report(output_dir, coded_rows, summary_rows, cooccurrence_rows)

    print(f"Screened {len(coded_rows)} excerpts.")
    print(f"Saved coded excerpts to {output_dir / 'coded_excerpts.csv'}.")
    print(f"Saved theme summary to {output_dir / 'theme_summary.csv'}.")
    print(f"Saved co-occurrence table to {output_dir / 'code_cooccurrence.csv'}.")
    print(f"Saved manual review queue to {output_dir / 'manual_review_queue.csv'}.")
    print(f"Saved markdown report to {output_dir / 'coding_report.md'}.")


if __name__ == "__main__":
    main()
