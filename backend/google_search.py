"""
Google Custom Search API Script
Searches Google using the Custom Search API
"""

import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def read_api_key(filename='key.txt'):
    """Read API key from the file"""
    try:
        with open(filename, 'r') as f:
            api_key = f.read().strip()
        return api_key
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None

def google_search(query, api_key, cse_id, num_results=10):
    """
    Perform a Google Custom Search with pagination support
    
    Args:
        query: Search query string
        api_key: Google API key
        cse_id: Custom Search Engine ID (cx parameter)
        num_results: Number of results to return (max 100, uses pagination if > 10)
    
    Returns:
        List of search results
    """
    all_results = []
    max_results = min(num_results, 100)  # Google API max is 100 results
    results_per_page = 10  # API allows max 10 results per request
    
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        
        # Calculate number of pages needed
        num_pages = (max_results + results_per_page - 1) // results_per_page
        
        for page in range(num_pages):
            start_index = (page * results_per_page) + 1
            results_this_page = min(results_per_page, max_results - len(all_results))
            
            if results_this_page <= 0:
                break
            
            # Make API request with pagination
            result = service.cse().list(
                q=query,
                cx=cse_id,
                num=results_this_page,
                start=start_index
            ).execute()
            
            items = result.get('items', [])
            all_results.extend(items)
            
            # If we got fewer results than requested, we've reached the end
            if len(items) < results_this_page:
                break
            
            # Show progress for pagination
            if num_pages > 1:
                print(f"  Fetched page {page + 1}/{num_pages} ({len(all_results)}/{max_results} results)...", end='\r')
        
        if num_pages > 1:
            print()  # New line after progress
        
        return all_results[:max_results]
        
    except HttpError as e:
        print(f"\nAn HTTP error occurred: {e}")
        if hasattr(e, 'error_details'):
            print(f"Error details: {e.error_details}")
        return all_results if all_results else []
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return all_results if all_results else []

def display_results(results):
    """Display search results in a formatted way"""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    print("=" * 80)
    
    for i, item in enumerate(results, 1):
        print(f"\n{i}. {item.get('title', 'No title')}")
        print(f"   URL: {item.get('link', 'No link')}")
        print(f"   Snippet: {item.get('snippet', 'No snippet')}")
        
        # Display displayLink if available
        if 'displayLink' in item:
            print(f"   Site: {item['displayLink']}")
        
        print("-" * 80)

def save_results_to_json(results, filename='search_results.json'):
    """Save search results to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

def load_cse_id() -> Optional[str]:
    """Load CSE ID from config file if it exists"""
    config_file = 'config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('cse_id', '')
        except Exception:
            pass
    return None

def main():
    # Read API key from test.py
    api_key = read_api_key('key.txt')
    
    if not api_key:
        print("Could not read API key. Please check test.py file.")
        return
    
    print("Google Custom Search API Script")
    print("=" * 80)
    
    # Get Custom Search Engine ID
    # Note: You need to create a Custom Search Engine at https://cse.google.com/cse/
    # and get the Search Engine ID (cx parameter)
    cse_id = load_cse_id()
    
    if not cse_id:
        print("Error: Custom Search Engine ID is required.")
        print("Create one at: https://cse.google.com/cse/")
        return
    
    # Get search query
    query = input("\nEnter search query: ").strip()
    
    if not query:
        print("Error: Search query cannot be empty.")
        return
    
    # Number of results
    try:
        num_results = int(input("Number of results (1-100, default 10): ").strip() or "10")
        num_results = max(1, min(num_results, 100))  # Google API max is 100 results
    except ValueError:
        num_results = 10
    
    if num_results > 10:
        print(f"\n📄 Note: Fetching {num_results} results will require {(num_results + 9) // 10} API calls...")
    
    # Perform search
    print(f"\nSearching for: '{query}'...")
    results = google_search(query, api_key, cse_id, num_results)
    
    # Display results
    display_results(results)
    
    # Option to save results
    if results:
        save_option = input("\nSave results to JSON file? (y/n): ").strip().lower()
        if save_option == 'y':
            save_results_to_json(results)

if __name__ == "__main__":
    main()

