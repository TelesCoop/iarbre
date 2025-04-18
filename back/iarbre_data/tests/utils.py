import os
import shutil
from iarbre_data.settings import BASE_DIR


def setup_test_data() -> None:
    """If there is no data in file_data, put test_data in it."""
    file_data_dir = os.path.join(BASE_DIR, "file_data")
    test_data_dir = os.path.join(BASE_DIR, "iarbre_data/tests/test_data")

    if not os.path.exists(file_data_dir) or not os.listdir(file_data_dir):
        os.makedirs(file_data_dir, exist_ok=True)

    if os.path.exists(test_data_dir):
        for file_name in os.listdir(test_data_dir):
            source_path = os.path.join(test_data_dir, file_name)
            destination_path = os.path.join(file_data_dir, file_name)
            if os.path.exists(destination_path):
                continue

            if os.path.isfile(source_path):
                shutil.copy(source_path, destination_path)


def clean_media() -> None:
    """If it exists, clean the media folder corresponding to fake data."""
    directory = "media/mvt_files/fake_data"
    if os.path.exists(directory) and os.path.isdir(directory):
        shutil.rmtree(directory)
