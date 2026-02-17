from scraper import CompetitorMonitor
import json
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def test_grok():
    print("Testing Grok API connection...")
    
    # Check API Key
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("ERROR: GROK_API_KEY not found in .env")
        return

    monitor = CompetitorMonitor()
    
    # Test with a dummy company
    company_name = "TechDiorama Test"
    print(f"Fetching updates for: {company_name}")
    
    try:
        # We might need to mock the response if we don't want to use real credits, 
        # but for verification we should try a real call if possible or check client init.
        # Actually scraper.py fetch_x_updates calls the API. 
        # Let's try to call it.
        results = monitor.fetch_x_updates(company_name)
        
        print("\n--- API Response ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        if isinstance(results, list):
            print("\nSUCCESS: API returned a list (even if empty). Connection is working.")
        else:
            print("\nWARNING: API returned something else.")
            
    except Exception as e:
        print(f"\nERROR: Failed to call Grok API: {e}")

if __name__ == "__main__":
    test_grok()
