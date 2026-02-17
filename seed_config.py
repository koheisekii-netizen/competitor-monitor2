from scraper import CompetitorMonitor

def seed():
    try:
        monitor = CompetitorMonitor()
        try:
            worksheet = monitor.sheet.worksheet("Config")
        except:
             print("Config sheet not found (should be impossible as scraper creates it).")
             return

        # Check if empty (excluding header)
        vals = worksheet.get_all_values()
        if len(vals) <= 1:
            targets = [
                ["患者目線のクリニック", "https://k-mesen.jp/", "", ""],
                ["ユビー", "https://ubie.app/telemedicine", "", ""],
                ["ミナカラ", "https://e-clinic.minacolor.com/", "", ""],
                ["ファストドクター", "https://fastdoctor.jp/", "", ""],
                ["おうち病院", "https://anamne.com/clinic/hayfever/", "", ""],
                ["からだ内科クリニック", "https://karada-naika.com/blog/telem-hay-fever/", "", ""],
            ]
            for t in targets:
                worksheet.append_row(t)
            print("Seeded 6 targets successfully.")
        else:
            print(f"Config sheet already has {len(vals)-1} entries. Skipping seed.")
            
    except Exception as e:
        print(f"Error seeding: {e}")

if __name__ == "__main__":
    seed()
