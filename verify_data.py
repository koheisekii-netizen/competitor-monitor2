from scraper import CompetitorMonitor
import sys

# Set stdout to utf-8 just in case
sys.stdout.reconfigure(encoding='utf-8')

def verify():
    monitor = CompetitorMonitor()
    worksheet = monitor.sheet.worksheet("Data")
    rows = worksheet.get_all_values()
    
    print(f"Total rows in Data sheet: {len(rows)}")
    if len(rows) > 1:
        print("Header:", rows[0])
        print("First 3 data rows:")
        for i, row in enumerate(rows[1:4]):
            print(f"Row {i+1}: {row}")
            
        # Check source types
        sources = set(r[2] for r in rows[1:])
        print(f"Sources found: {sources}")
    else:
        print("Data sheet is empty (only header or less).")

if __name__ == "__main__":
    verify()
