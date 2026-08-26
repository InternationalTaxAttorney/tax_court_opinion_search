import os
import re
import subprocess
import sys
from pathlib import Path

import FreeSimpleGUI as sg
import pandas as pd

from tax_court_opinion_search.download import download_data, get_data_dir

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCAL_PARQUET_PATH = PROJECT_ROOT / 'cases.parquet'
USER_PARQUET_PATH = get_data_dir() / 'cases.parquet'


def get_parquet_path():
    if LOCAL_PARQUET_PATH.exists():
        return LOCAL_PARQUET_PATH
    return USER_PARQUET_PATH


def get_output_dir():
    output_dir = get_data_dir() / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def show_download_popup():
    layout = [[sg.Text('Downloading opinion data (~180MB). This happens once and may take a minute...')]]
    window = sg.Window('Please wait', layout, keep_on_top=True, finalize=True)
    window.force_focus()
    window.read(timeout=0)
    return window


def load_dataframe():
    parquet_path = get_parquet_path()

    if not parquet_path.exists():
        popup = show_download_popup()
        try:
            download_data()
        except Exception as e:
            sg.popup_error(f'Failed to download data:\n\n{e}')
            raise FileNotFoundError(parquet_path) from e
        finally:
            popup.close()
        parquet_path = get_parquet_path()

    if not parquet_path.exists():
        sg.popup_error(f'Could not find parquet file:\n\n{parquet_path}')
        raise FileNotFoundError(parquet_path)
    return pd.read_parquet(parquet_path)


def write_results(results):
    results_path = get_output_dir() / 'results.txt'
    results_path.write_text(''.join(results), encoding='utf-8')
    if sys.platform == 'win32':
        os.startfile(results_path.resolve())
    elif sys.platform == 'darwin':
        subprocess.run(['open', results_path.resolve()])
    else:  # Linux
        subprocess.run(['xdg-open', results_path.resolve()])


def regex_search(df, pattern, num_before_chars, num_after_chars):
    try:
        compiled_pattern = re.compile(
            rf'.{{{num_before_chars}}}{pattern}.{{{num_after_chars}}}',
            flags=re.DOTALL | re.IGNORECASE,
        )
    except re.error as e:
        sg.popup_error(f'Invalid regex:\n\n{e}')
        return

    results = []

    for _, row in df.iterrows():
        text = str(row['text'])
        match = compiled_pattern.search(text)

        if match:
            case_name = row.get('filename', 'Unknown Case')
            results.append(f'{case_name}\n{match.group()}\n\n')

    results.insert(0, f'Regex Pattern: {pattern}\n\nNumber of files found: {len(results)}\n\n')
    write_results(results)


def other_search(df, text_to_search_for, num_before_chars, num_after_chars):
    all_items = re.findall(r'"(.*?)"|(\S+)', text_to_search_for)
    all_items = [item for sublist in all_items for item in sublist if item]
    all_items = [item.lower() for item in all_items]

    if not all_items:
        sg.popup_error('Please enter search terms.')
        return

    first_item = all_items[0]
    escaped_first_item = re.escape(first_item)

    try:
        pattern = re.compile(rf'.{{{num_before_chars}}}{escaped_first_item}.{{{num_after_chars}}}', flags=re.DOTALL | re.IGNORECASE)
    except re.error as e:
        sg.popup_error(f'Invalid regex:\n\n{e}')
        return

    included = [item for item in all_items if not item.startswith('-')]
    excluded = [item[1:] for item in all_items if item.startswith('-')]
    results = []

    for _, row in df.iterrows():
        text = str(row['text']).lower()

        if not all(item in text for item in included):
            continue

        if any(item in text for item in excluded):
            continue

        match = pattern.search(text)

        if match:
            year = row['year']
            month = row['month']
            day = row['day']
            opinion_type = row['opinion_type']
            opinion_name = row['opinion_name']
            num_pages = row['num_pages']
            docket_num = row['docket_number']
            judge = row['judge_name']
            match = match.group()
            results.append(
                f'    Date: {year}-{month}-{day}, Opinion Type: {opinion_type}, Number of Pages: {num_pages}, Docket No.:{docket_num}, Judge: {judge}\n    Taxpayer Name: {opinion_name}\n{match}\n\n'
            )

    results.insert(0, f'[Non-regex] Search Term(s): {text_to_search_for}\n\nNumber of files found: {len(results)}\n\n')

    write_results(results)


def main():

    try:
        df = load_dataframe()
    except FileNotFoundError:
        return

    layout = [
        [
            sg.Text('Enter text in one of the two input fields below.'),
        ],
        [
            sg.Text('Regular Expression (Regex) Search:', font=18, text_color='black'),
        ],
        [
            sg.Text('Regex Pattern:'),
            sg.Input(key='regex_pattern', size=(30, 1), default_text='', background_color='lightpink'),
        ],
        [
            sg.Text(''),
        ],
        [
            sg.Text('Normal Text Search (Non-Regex):', font=18, text_color='black'),
        ],
        [
            sg.Text('Search Term(s):'),
            sg.Input(key='text_to_search_for', size=(30, 1), default_text='', background_color='lightpink'),
        ],
        [
            sg.Multiline(
                """    Opinions containing all search terms will be found.
    The text will be centered on the first term.
    Use quotes to search for multiple words in sequence.
    Use "-" to exclude terms, but don't use a dash before quoted text.
    Uppercase vs. lowercase is ignored.
        """,
                size=(70, 5),
                disabled=True,
                no_scrollbar=True,
            )
        ],
        [
            sg.Text('Number of characters before search term(s):'),
            sg.Input(key='num_before_chars', size=(6, 1), default_text='300', background_color='lightpink'),
        ],
        [
            sg.Text('Number of characters after search term(s):'),
            sg.Input(key='num_after_chars', size=(6, 1), default_text='300', background_color='lightpink'),
        ],
        [
            sg.Text('After entering the terms, press enter or click on the Search button', font=('Arial', 12, 'bold'), text_color='orange'),
        ],
        [
            sg.Button('Search'),
            sg.Button('Cancel'),
        ],
        [sg.Text('Andrew Mitchel LLC, Copyright (c) 2026', font=('Arial', 12, 'bold'), text_color='black')],
    ]

    window = sg.Window('Search Tax Court Opinions', layout, return_keyboard_events=True, finalize=True)
    window['text_to_search_for'].set_focus()

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, 'Cancel', 'Escape:27'):
            window.close()
            break

        if values['regex_pattern'] and values['text_to_search_for']:
            sg.popup_error('Use only one search type.')
            continue

        try:
            num_before_chars = int(values['num_before_chars'])
            num_after_chars = int(values['num_after_chars'])
        except ValueError:
            sg.popup_error('Character counts must be integers.')
            continue

        if event in ('Search', '\r') and values['regex_pattern']:
            regex_search(df, values['regex_pattern'], num_before_chars, num_after_chars)
            break

        if event in ('Search', '\r') and values['text_to_search_for']:
            other_search(df, values['text_to_search_for'], num_before_chars, num_after_chars)
            break

    window.close()


if __name__ == '__main__':
    main()
