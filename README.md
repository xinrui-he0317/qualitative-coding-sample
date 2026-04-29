# Qualitative Coding Sample

This is a beginner-level Python project inspired by qualitative coding work on
downward mobility. It demonstrates how I am learning to make interview coding
workflows more organized and reproducible.

## Project Context

The broader research context is downward economic mobility among unemployed or
re-employed workers in the United States. In this type of project, interview
excerpts often require close reading and contextual interpretation before a
final code can be assigned.

This sample focuses on two interpretive concepts:

- `social_solidarity`
- `meritocratic_individualism`

It also adds descriptive flags for topics such as age, race, gender, education,
class, and structural barriers.

## What The Script Does

The script reads fictional interview excerpts from `sample_interviews.csv`,
applies a small codebook, and generates several output files for manual review:

- `outputs/coded_excerpts.csv`
- `outputs/theme_summary.csv`
- `outputs/code_cooccurrence.csv`
- `outputs/manual_review_queue.csv`
- `outputs/coding_report.md`

The goal is not to replace qualitative interpretation. Instead, the script
creates a first-pass screening workflow that helps identify candidate excerpts
for later human review.

## Methodological Note

Concepts such as social solidarity and meritocratic individualism often depend
on context. A phrase like "my own effort" may reflect self-blame, but it could
also appear in a critical or ironic narrative. For that reason, all output from
this script should be treated as preliminary. Final coding decisions require
manual contextual reading, similar to NVivo-style interpretive analysis.

## Data Privacy

All excerpts in this repository are fictional and used only for demonstration.
No real interview transcripts, participant information, or private research data
are included.

## How To Run

In Terminal, navigate to the project folder and run:

```bash
python3 downward_mobility_text_coding_sample.py
```

The script will read `sample_interviews.csv` and save results in the `outputs`
folder.

Optional usage:

```bash
python3 downward_mobility_text_coding_sample.py --input sample_interviews.csv --output-dir outputs
```

## Why This Sample Matters

This project reflects my effort to connect NVivo-based qualitative coding
experience with beginner Python skills. It shows how qualitative research
materials can be organized into a simple, reproducible workflow while still
preserving the importance of human interpretation.
