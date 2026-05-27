This app is a GUI to search text data derived from [Tax Court opinions](https://dawson.ustaxcourt.gov/) between about 1995 to April 2026.

## Installation
- pip install tax-court-opinion-search
- tax-court-opinion-search download-data
- tc-search

## Data
The dataset can be found on [Hugging Face](https://huggingface.co/datasets/andrew-mitchel/tax_court_opinions).  The dataset includes text from 14,789 files of Tax Court opinions. The Tax Court publishes its opinions as PDF files. The PDF files were converted to text files and then saved as a parquet file.

Each item includes the date, opinion type, number of pages, docket number, judge, taxpayer's name, and search results.

The older PDF files include text that appears to be from OCR. The OCR results for 2009 to 2012 are not as accurate as the results for other years.
