"""
Simple EpiCollect5 Data Downloader
Just downloads data and saves as CSV - nothing else!
"""

import requests
import csv
import json
from datetime import datetime

def download_epicollect_data(project_slug):
    """Download data from EpiCollect5 and save as CSV"""
    
    print(f"Downloading data from EpiCollect5 project: {project_slug}")
    print("=" * 50)
    
    # EpiCollect5 API URL
    url = f"https://five.epicollect.net/api/export/entries/{project_slug}"
    
    try:
        # Download ALL pages of data
        print("Connecting to EpiCollect5...")
        all_entries = []
        page = 1
        
        while True:
            params = {'format': 'json', 'page': page, 'per_page': 50}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            entries = data.get('data', {}).get('entries', [])
            
            if not entries:
                break
                
            all_entries.extend(entries)
            print(f"Downloaded page {page}: {len(entries)} entries")
            page += 1
        
        if not all_entries:
            print("No data found!")
            return
        
        print(f"Total entries found: {len(all_entries)}")
        entries = all_entries
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON backup
        json_filename = f"epicollect_data_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved raw data: {json_filename}")
        
        # Save as CSV
        if entries:
            csv_filename = f"epicollect_data_{timestamp}.csv"
            
            # Get all field names from first entry
            fieldnames = list(entries[0].keys())
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in entries:
                    # Flatten any nested dictionaries for CSV
                    flat_entry = {}
                    for key, value in entry.items():
                        if isinstance(value, dict):
                            flat_entry[key] = str(value)
                        else:
                            # Fix scrambled Unicode symbols
                            if isinstance(value, str):
                                # Fix the actual Unicode characters found in debug
                                # Replace with simple text versions for better compatibility
                                value = value.replace('﹤', '<')   # Replace small less-than with simple <
                                value = value.replace('﹥', '>')   # Replace small greater-than with simple >
                                
                                # Alternative: if you want the mathematical symbols, try these
                                # value = value.replace('﹤', '<=')  # Less than or equal as text
                                # value = value.replace('﹥', '>=')  # Greater than or equal as text
                                
                                # Fix apostrophes and quotes - multiple variants
                                value = value.replace('â€™', "'")  # Fix apostrophe variant 1
                                value = value.replace('â€˜', "'")  # Fix apostrophe variant 2 (left single quote)
                                value = value.replace('â€œ', '"')  # Fix opening quote
                                value = value.replace('â€', '"')   # Fix closing quote variant 1
                                value = value.replace('â€�', '"')  # Fix closing quote variant 2
                                
                                # More comprehensive apostrophe fixes
                                value = value.replace(''', "'")    # Fix proper left single quote
                                value = value.replace(''', "'")    # Fix proper right single quote
                                value = value.replace('"', '"')    # Fix proper left double quote
                                value = value.replace('"', '"')    # Fix proper right double quote
                                
                                # Fix dashes
                                value = value.replace('â€"', '–')  # Fix en-dash
                                value = value.replace('â€"', '—')  # Fix em-dash
                                
                                # Additional common encoding fixes
                                value = value.replace('â€¦', '...')  # Fix ellipsis
                                value = value.replace('Â', '')      # Remove stray Â characters
                            flat_entry[key] = value
                    writer.writerow(flat_entry)
            
            print(f"✓ Saved CSV file: {csv_filename}")
        
        print("\nDone! Check your files:")
        print(f"- Raw data: {json_filename}")
        print(f"- CSV data: {csv_filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    # Your project slug
    PROJECT_SLUG = "saltmarsh-saver"
    


    print()
    
    download_epicollect_data(PROJECT_SLUG)
    
    input("\nPress Enter to close...")
