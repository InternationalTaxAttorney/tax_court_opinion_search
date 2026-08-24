# Tax Court Opinion Search

A small desktop GUI for searching the full text of [U.S. Tax Court opinions](https://dawson.ustaxcourt.gov/) (1995 to present, updated monthly) — no coding required.

## Features
- Search across all opinions with plain text or a full regex pattern
- Plain-text search supports multiple terms (AND logic), `"quoted phrases"` for exact word sequences, and a `-term` prefix to exclude opinions containing that term
- Matching is case-insensitive
- Choose how many characters of surrounding context to show before/after each match
- Results — including date, opinion type, docket number, judge, and taxpayer name for plain-text searches — are written to a text file that opens automatically when the search finishes

## Installation
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install tax-court-opinion-search
tc-search
```
The first command installs [uv](https://docs.astral.sh/uv/), a fast Python package/tool manager. Already have Python set up your own way? `pip install tax-court-opinion-search` works too, as long as `tc-search` ends up on your PATH.

The first time `tc-search` runs, it automatically downloads the opinion dataset (~180MB) from Hugging Face. That download only happens once — new opinions are added to the dataset monthly, but `tc-search` won't pick them up on its own. Run `tax-court-opinion-search download-data` any time to pull the latest version.

## Usage
Fill in exactly one of the two search fields, then press Enter or click **Search**:

- **Regex Pattern** — a standard Python regular expression, matched against each opinion's text.
- **Search Term(s)** — one or more words to match, without regex syntax:
  - Every term must be present in an opinion for it to match (AND logic).
  - Wrap multiple words in quotes (e.g. `"innocent spouse"`) to require that exact sequence.
  - Prefix a term with `-` (e.g. `-partnership`) to exclude opinions containing it.

Use the **Number of characters before/after** fields to control how much surrounding context is shown around each match (300 characters on each side by default).

When the search finishes, the results file opens automatically. It's also saved under your user data folder (e.g. `%LOCALAPPDATA%\tax_court_opinion_search\tax_court_opinion_search\output\results.txt` on Windows) if you want to find it again later.

## Data
The dataset lives on [Hugging Face](https://huggingface.co/datasets/andrew-mitchel/tax-court-opinions) and contains the text of 14,789 Tax Court opinions, with new opinions added monthly. The Tax Court publishes opinions as PDFs; these were converted to text and compiled into a single parquet file, with one row per opinion including its date, opinion type, number of pages, docket number, judge, taxpayer's name, and full text.

Older opinions were converted using OCR, and text for opinions from 2009–2012 in particular is less accurate than other years.

## License
[MIT](LICENSE)
