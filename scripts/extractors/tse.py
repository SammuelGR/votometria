import os
import requests
import zipfile
import tempfile
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(PARENT_DIR)

from constants_tse import (
    URL_TSE_PRESIDENCY_2018,
    URL_TSE_PRESIDENCY_2022,
    TARGET_CSV_PRESIDENCY_2018,
    TARGET_CSV_PRESIDENCY_2022,
    URL_TSE_ELECTORATE_2018,
    URL_TSE_ELECTORATE_2022,
    TARGET_CSV_ELECTORATE_2018,
    TARGET_CSV_ELECTORATE_2022,
    RAW_DATA_DIR,
)


def download_and_extract_tse(url_zip, target_filename):
    """
    Downloads a ZIP file from TSE via stream and extracts only the target file.
    """
    # 1. Ensures that the data/raw/ folder exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    final_csv_path = os.path.join(RAW_DATA_DIR, target_filename)

    # Skips extraction if the file already exists (avoids redundant work)
    if os.path.exists(final_csv_path):
        print(f"File {target_filename} already exists in {RAW_DATA_DIR}. Skipping extraction.")
        return

    print(f"Starting download from: {url_zip}")

    # 2. Creates a temporary file to avoid consuming all RAM
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
        # Makes the request in streaming mode (downloads in chunks)
        response = requests.get(url_zip, stream=True)
        response.raise_for_status()  # Checks for download errors

        # Writes 8MB chunks to disk
        for chunk in response.iter_content(chunk_size=8192 * 1024):
            if chunk:
                tmp_zip.write(chunk)

        tmp_zip_path = tmp_zip.name

    print("Download completed. Starting target CSV extraction...")

    # 3. Opens the temporary ZIP and extracts only the target file
    try:
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            if target_filename in zip_ref.namelist():
                # Extracts the CSV file to the raw folder
                zip_ref.extract(target_filename, path=RAW_DATA_DIR)
                print(f"Success: {target_filename} extracted to {RAW_DATA_DIR}")
            else:
                print(f"Error: File {target_filename} not found in ZIP.")
    finally:
        # 4. Cleanup: removes the temporary ZIP file to free up space
        os.remove(tmp_zip_path)
        print("Temporary ZIP file removed to free up space.")


def extract_presidency_data() -> int:
    """
    Extracts TSE presidential election data for 2018 and 2022.
    Returns the number of files successfully extracted.
    """
    presidency_targets = [
        (URL_TSE_PRESIDENCY_2018, TARGET_CSV_PRESIDENCY_2018),
        (URL_TSE_PRESIDENCY_2022, TARGET_CSV_PRESIDENCY_2022),
    ]

    print("\nExtracting TSE presidential election data...")
    extracted_count = 0

    for url, target_file in presidency_targets:
        try:
            download_and_extract_tse(url, target_file)
            extracted_count += 1
        except Exception as exc:
            print(f"Error extracting {target_file}: {exc}")
            continue

    return extracted_count


def extract_voter_profile_data() -> int:
    """
    Extracts TSE voter profile data for 2018 and 2022.
    Returns the number of files successfully extracted.
    """
    voter_profile_targets = [
        (URL_TSE_ELECTORATE_2018, TARGET_CSV_ELECTORATE_2018),
        (URL_TSE_ELECTORATE_2022, TARGET_CSV_ELECTORATE_2022),
    ]

    print("\nExtracting TSE voter profile data...")
    extracted_count = 0

    for url, target_file in voter_profile_targets:
        try:
            download_and_extract_tse(url, target_file)
            extracted_count += 1
        except Exception as exc:
            print(f"Error extracting {target_file}: {exc}")
            continue

    return extracted_count