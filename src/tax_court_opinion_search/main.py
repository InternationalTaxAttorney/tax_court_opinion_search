import multiprocessing
import os
import re
from pathlib import Path

import FreeSimpleGUI as sg
from platformdirs import user_data_dir

APP_NAME = 'tax_court_opinion_search'


def get_data_dir():
    return Path(user_data_dir(APP_NAME))


TEXT_FILES_PATH = get_data_dir() / 'text_files'


def get_output_dir():
    output_dir = get_data_dir() / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def main():
    layout = [
        [
            sg.Text('Enter text in one of the two input fields below.'),
        ],
        [
            sg.Text('Regular Expression (Regex) Search:', font=18, text_color='black'),
        ],
        [
            sg.Text('Regex Pattern:'),
            sg.Input(
                key='regex_pattern',
                size=(30, 1),
                default_text='',
                background_color='lightpink',
            ),
        ],
        [
            sg.Text(''),
        ],
        [
            sg.Text('Normal Text Search (Non-Regex):', font=18, text_color='black'),
        ],
        [
            sg.Text('Search Term(s):'),
            sg.Input(
                key='text_to_search_for',
                size=(30, 1),
                default_text='',
                background_color='lightpink',
            ),
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
        [sg.Button('Search'), sg.Button('Cancel')],
        [sg.Text('Andrew Mitchel LLC, Copyright 2026', font=('Arial', 12, 'bold'), text_color='black')],
    ]
    window = sg.Window('Search Tax Court Opinions', layout, return_keyboard_events=True, finalize=True)
    window['text_to_search_for'].set_focus()  # need finalize=True above for focus

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Cancel', 'Escape:27'):
            window.close()
            break
        if values['regex_pattern'] and values['text_to_search_for']:
            sg.popup_error('Use only one search type.')
            continue
        if event in ('Search', '\r') and values['regex_pattern']:
            try:
                _ = int(values['num_before_chars'])
                _ = int(values['num_after_chars'])
            except ValueError:
                sg.popup_error('Character counts must be integers.')
                continue
            regex_search(values['regex_pattern'], int(values['num_before_chars']), int(values['num_after_chars']))
            break
        if event in ('Search', '\r') and values['text_to_search_for']:
            try:
                _ = int(values['num_before_chars'])
                _ = int(values['num_after_chars'])
            except ValueError:
                sg.popup_error('Character counts must be integers.')
                continue
            other_search(values['text_to_search_for'], int(values['num_before_chars']), int(values['num_after_chars']))
            break


def get_case_text_files():
    return [p for p in TEXT_FILES_PATH.iterdir() if p.is_file()]


def write_results(results):
    results_path = get_output_dir() / 'results.txt'
    results_path.write_text(''.join(results), encoding='utf-8')
    os.startfile(results_path.resolve())


def search_file(file, pattern):

    # open the text file
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()

    # match any patterns
    match = pattern.search(text)

    # if there is a match, return the text of the match
    if match:
        return f'{file.name}\n{match.group()}\n\n'

    # otherwise return an empty string
    return ''


def regex_search(pattern, num_before_chars, num_after_chars):
    # compile the pattern
    try:
        compiled_pattern = re.compile(rf'.{{{num_before_chars}}}{pattern}.{{{num_after_chars}}}', flags=re.DOTALL | re.IGNORECASE)
    except re.error as e:
        sg.popup_error(f'Invalid regex:\n\n{e}')
        return

    # get a list of the files to search
    case_text_files = get_case_text_files()

    # use multiprocessing to make the search faster
    with multiprocessing.Pool() as pool:
        results = pool.starmap(search_file, [(file, compiled_pattern) for file in case_text_files])

    # Remove None results
    results = [r for r in results if r]

    # insert the search pattern at the beginning of the results
    results.insert(0, f'Regex Pattern: {pattern}\n\nNumber of files found: {len(results)}\n\n')

    # save the results to a file and open the file
    write_results(results)


def process_file(file, included, excluded, pattern):
    # open the text file
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read().lower()

    # return if all search terms not in the file
    if not all(item in text for item in included):
        return None

    # return if any of the excluded terms are in the file
    if any(item in text for item in excluded):
        return None

    return search_file(file, pattern)


def other_search(text_to_search_for, num_before_chars, num_after_chars):
    # get a list of the files to search
    case_text_files = get_case_text_files()

    # Separate arguments using a regular expression, keeping strings in quotes as a single item
    all_items = re.findall(r'"(.*?)"|(\S+)', text_to_search_for)  # returns a list of tuples

    # Flatten the tuple and remove any None values
    all_items = [item for sublist in all_items for item in sublist if item]
    all_items = [item.lower() for item in all_items]

    # the search results center on the first item
    first_item = all_items[0]

    # if the first item includes regex characters, they need to be escaped to avoid regex
    # for example, 162(a) will not return any results unless it is escaped
    escaped_first_item = re.escape(first_item)

    # compile the pattern
    try:
        pattern = re.compile(rf'.{{{num_before_chars}}}{escaped_first_item}.{{{num_after_chars}}}', flags=re.DOTALL | re.IGNORECASE)
    except re.error as e:
        sg.popup_error(f'Invalid regex:\n\n{e}')
        return

    # Separate included and excluded items (items to be excluded start with "-")
    included = [item for item in all_items if not item.startswith('-')]
    excluded = [item[1:] for item in all_items if item.startswith('-')]

    # use multiprocessing to make the search faster
    with multiprocessing.Pool() as pool:
        args = [(file, included, excluded, pattern) for file in case_text_files]
        results = pool.starmap(process_file, args)

    # Remove None results
    results = [r for r in results if r]

    # insert the search terms at the beginning so you can see what was searched for
    results.insert(0, f'[Non-regex] Search Term(s): {text_to_search_for}\n\nNumber of files found: {len(results)}\n\n')

    # save the results to a file and open the file
    write_results(results)


if __name__ == '__main__':
    multiprocessing.freeze_support()  # needed if using PyInstaller or on Windows
    main()
