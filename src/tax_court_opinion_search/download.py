from pathlib import Path

from huggingface_hub import snapshot_download
from platformdirs import user_data_dir

APP_NAME = 'tax_court_opinion_search'


def get_data_dir():
    return Path(user_data_dir(APP_NAME))


def download_data():
    data_dir = get_data_dir()

    snapshot_download(
        repo_id='andrew-mitchel/tax_court_opinions',
        repo_type='dataset',
        local_dir=data_dir,
        local_dir_use_symlinks=False,
    )

    return data_dir
