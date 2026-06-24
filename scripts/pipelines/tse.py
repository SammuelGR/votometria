from extractors.tse import extract_presidency_data, extract_voter_profile_data


def run_tse_pipeline() -> int:
    """
    Runs the complete TSE extraction pipeline for both presidential election
    and voter profile data across all configured election cycles.
    Returns the total number of files successfully extracted.
    """
    print("Starting TSE extraction pipeline...")
    
    presidency_count = extract_presidency_data()
    voter_profile_count = extract_voter_profile_data()
    
    total_extracted = presidency_count + voter_profile_count

    if total_extracted > 0:
        print(f"\nSuccess! {total_extracted} TSE files extracted.")
    else:
        print("\nNo TSE files were extracted.")

    return total_extracted

