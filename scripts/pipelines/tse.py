from extractors.tse import extract_presidency_data, extract_voter_profile_data
from transformers.tse import (
    run_presidency_transformation,
    run_voter_profile_transformation,
)


def run_tse_pipeline() -> int:
    """
    Runs the complete TSE ETL pipeline for presidential election data:
    1. Extracts raw data from TSE sources
    2. Transforms and cleans the data
    3. Persists parsed datasets to disk
    
    Returns the total number of TSE files successfully processed.
    """
    print("Starting TSE ETL pipeline...")
    
    # Phase 1: Extraction
    print("\n--- Phase 1: Extraction ---")
    presidency_count = extract_presidency_data()
    voter_profile_count = extract_voter_profile_data()
    
    total_extracted = presidency_count + voter_profile_count

    if total_extracted == 0:
        print("No TSE files were extracted.")
        return 0
    
    print(f"Extracted: {total_extracted} TSE files")
    
    # Phase 2: Transformation
    print("\n--- Phase 2: Transformation ---")
    presidency_transform_success = run_presidency_transformation()
    electorate_transform_success = run_voter_profile_transformation()

    if not presidency_transform_success:
        print("Warning: Presidency transformation failed.")
    if not electorate_transform_success:
        print("Warning: Voter profile transformation failed.")
    
    if not presidency_transform_success or not electorate_transform_success:
        print("Transformation completed with warnings.")
        return total_extracted
    
    print("Transformation completed successfully.")
    print(f"\nSuccess! TSE ETL pipeline completed with {total_extracted} files extracted.")
    
    return total_extracted

