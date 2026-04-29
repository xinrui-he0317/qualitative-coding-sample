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
        "excerpt": (
            "After I was laid off, I took a lower pay job outside my old field. "
            "At first I blamed myself and thought I should have made better "
            "choices before the industry changed."
        ),
    },
    {
        "participant_id": "P02",
        "excerpt": (
            "The industry changed so quickly that there were no openings near me. "
            "My coworkers and I talked about it as a shared struggle for our "
            "generation."
        ),
    },
    {
        "participant_id": "P03",
        "excerpt": (
            "Losing health insurance made it hard to switch careers. Support "
            "from my family helped, but I still felt like I had lost middle "
            "class status. I kept thinking my future depended on my own effort."
        ),
    },
]


def clean_text(text):
    """Lowercase text and remove extra spaces for easier matching."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def assign_matches(excerpt, codebook):
    """Return all labels whose keywords appear in the excerpt."""
    cleaned = clean_text(excerpt)
    matched_labels = []

    for label, keywords in codebook.items():
        for keyword in keywords:
            if keyword in cleaned:
                matched_labels.append(label)
                break

    return matched_labels


def read_excerpts(path):
    """Read excerpts from a CSV file, or use demo excerpts if no file exists."""
    if not path.exists():
        return DEMO_EXCERPTS

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def write_coded_excerpts(rows):
    with CODED_OUTPUT.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "participant_id",
            "excerpt",
            "candidate_focal_codes",
            "descriptive_flags",
            "needs_manual_review",
            "manual_review_note",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_theme_summary(focal_counts, flag_counts):
    with SUMMARY_OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["category_type", "category", "excerpt_count"])
        for theme, count in focal_counts.most_common():
            writer.writerow(["candidate_focal_code", theme, count])
        for flag, count in flag_counts.most_common():
            writer.writerow(["descriptive_flag", flag, count])


def main():
    excerpts = read_excerpts(INPUT_FILE)
    coded_rows = []
    focal_counts = Counter()
    flag_counts = Counter()

    for row in excerpts:
        participant_id = row["participant_id"]
        excerpt = row["excerpt"]
        focal_codes = assign_matches(excerpt, FOCAL_CODEBOOK)
        descriptive_flags = assign_matches(excerpt, DESCRIPTIVE_FLAGS)

        focal_counts.update(focal_codes)
        flag_counts.update(descriptive_flags)
        coded_rows.append(
            {
                "participant_id": participant_id,
                "excerpt": excerpt,
                "candidate_focal_codes": (
                    "; ".join(focal_codes) if focal_codes else "none_found"
                ),
                "descriptive_flags": (
                    "; ".join(descriptive_flags) if descriptive_flags else "none_found"
                ),
                "needs_manual_review": "yes",
                "manual_review_note": (
                    "Keyword results are preliminary; final coding requires "
                    "contextual reading."
                ),
            }
        )

    write_coded_excerpts(coded_rows)
    write_theme_summary(focal_counts, flag_counts)

    print(f"Coded {len(coded_rows)} excerpts.")
    print(f"Saved detailed coding to {CODED_OUTPUT}.")
    print(f"Saved theme summary to {SUMMARY_OUTPUT}.")


if __name__ == "__main__":
    main()
