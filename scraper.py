import os
import sys
import glob

# Allow importing from user site-packages if not in PATH
user_site_packages = glob.glob(os.path.expanduser("~\\AppData\\Roaming\\Python\\Python3*\\site-packages"))
if user_site_packages:
    sys.path.append(user_site_packages[0])

import json
import requests
import gspread
from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Constants
KEYWORDS = ["花粉症", "オンライン診療", "オンライン保険診療"]
SERVICE_ACCOUNT_FILE = 'service_account.json'

class CompetitorMonitor:
    def __init__(self):
        self.grok_api_key = os.getenv("GROK_API_KEY")
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        
        if not self.grok_api_key:
            raise ValueError("GROK_API_KEY not found in .env")
        if not self.spreadsheet_id:
            raise ValueError("SPREADSHEET_ID not found in .env")
        
        # Initialize Google Sheets Client (using google-auth)
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load service account info and fix private key newlines
        with open(SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as f:
            service_account_info = json.load(f)
            # Ensure private key has correct newlines
            if 'private_key' in service_account_info:
                key = service_account_info['private_key']
                # Replace literal \n with actual newline
                key = key.replace('\\n', '\n')
                # Remove any other stray backslashes (e.g. from invalid escapes like \u)
                key = key.replace('\\', '')
                service_account_info['private_key'] = key
                
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        self.client_gs = gspread.authorize(creds)
        self.sheet = self.client_gs.open_by_key(self.spreadsheet_id)

        # Initialize User Agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Initialize OpenAI client for Grok
        self.client_ai = OpenAI(
            api_key=self.grok_api_key,
            base_url="https://api.x.ai/v1",
        )

    def fetch_config(self):
        """Read target companies from 'Config' sheet."""
        try:
            worksheet = self.sheet.worksheet("Config")
        except gspread.exceptions.WorksheetNotFound:
            # Create Config sheet if not exists
            worksheet = self.sheet.add_worksheet(title="Config", rows=100, cols=5)
            worksheet.append_row(["Company Name", "News URL", "X Query (Optional)", "IR URL (Optional)"])
            return []

        records = worksheet.get_all_records()
        return records

    def is_relevant(self, text):
        """Check if text contains any of the target keywords."""
        if not text:
            return False
        for keyword in KEYWORDS:
            if keyword in text:
                return True
        return False

    def fetch_x_updates(self, company_name):
        """Fetch X updates using Grok API with keyword filtering."""
        print(f"Fetching X updates for {company_name}...")
        
        keywords_str = " OR ".join(f'"{k}"' for k in KEYWORDS)
        prompt = f"""
        Search for recent posts or news regarding "{company_name}" on X (formerly Twitter) that match ANY of these keywords: {keywords_str}.
        
        Focus on official announcements or significant buzz related to these topics.
        Return a JSON list of objects with 'title', 'url' (if available, else null), and 'summary'.
        If nothing relevant is found, return an empty list [].
        Output ONLY valid JSON.
        """

        try:
            response = self.client_ai.chat.completions.create(
                model="grok-4",
                messages=[
                    {"role": "system", "content": "You are a research assistant. Output only JSON."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            # Clean up potential markdown blocks
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"Error fetching X for {company_name}: key error or other issue: {e}")
            return []

    def fetch_website_news(self, url, company_name):
        """Fetch news from company website looking for keywords."""
        if not url:
            return []
            
        print(f"Fetching website news for {company_name} ({url})...")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            updates = []
            # Find all links that contain keywords
            links = soup.find_all('a')
            seen_urls = set()
            
            for link in links:
                text = link.get_text(strip=True)
                href = link.get('href')
                
                if not href:
                    continue
                    
                # Resolve relative URLs
                full_url = requests.compat.urljoin(url, href)
                
                if full_url in seen_urls:
                    continue
                
                if self.is_relevant(text):
                    seen_urls.add(full_url)
                    updates.append({
                        'company': company_name,
                        'source': 'Website News',
                        'title': text[:100], # Truncate title
                        'url': full_url,
                        'summary': f"Found keyword match in link text: {text}"
                    })
            
            return updates
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

    def fetch_ir_updates(self, url, company_name):
        """Fetch IR updates with specific keywords."""
        if not url:
            return []
            
        print(f"Fetching IR updates for {company_name} ({url})...")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            updates = []
            links = soup.find_all('a')
            seen_urls = set()
            
            # IR Keywords
            ir_keywords = ["決算", "Financial", "Report", "Presentation", "説明会", "有価証券報告書", "短信"]
            
            for link in links:
                text = link.get_text(strip=True)
                href = link.get('href')
                
                if not href:
                    continue
                    
                full_url = requests.compat.urljoin(url, href)
                
                if full_url in seen_urls:
                    continue
                
                # Check for IR keywords
                if any(k in text for k in ir_keywords):
                    seen_urls.add(full_url)
                    updates.append({
                        'company': company_name,
                        'source': 'IR',
                        'title': text[:100],
                        'url': full_url,
                        'summary': f"IR Match: {text}"
                    })
            
            return updates
            
        except Exception as e:
            print(f"Error scraping IR {url}: {e}")
            return []

    def save_results(self, results):
        """Save relevant results to 'Data' sheet, avoiding duplicates."""
        try:
            worksheet = self.sheet.worksheet("Data")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.sheet.add_worksheet(title="Data", rows=1000, cols=6)
            worksheet.append_row(["Date", "Company", "Source", "Title", "URL", "Summary"])

        # Fetch existing URLs to avoid duplicates
        existing_records = worksheet.get_all_records()
        existing_urls = set(str(r.get('URL', '')).strip() for r in existing_records)

        rows_to_add = []
        for res in results:
            url = str(res.get('url', '')).strip()
            
            # If URL exists, skip (Simple deduplication)
            if url and url in existing_urls:
                print(f"Skipping duplicate: {res['title']}")
                continue
                
            rows_to_add.append([
                datetime.now().strftime("%Y-%m-%d"),
                res['company'],
                res['source'],
                res['title'],
                url,
                res['summary']
            ])
            print(f"Saved: {res['title']}")
            # Add to local set to avoid duplicates within the same run
            existing_urls.add(url)
        
        if rows_to_add:
            worksheet.append_rows(rows_to_add)

    def send_email(self, results):
        """Send email notification efficiently."""
        gmail_user = os.getenv("GMAIL_USER") or ""
        gmail_password = os.getenv("GMAIL_APP_PASSWORD") or ""
        to_email = os.getenv("TO_EMAIL") or gmail_user

        if not gmail_user or not gmail_password:
            print("Skipping email: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env")
            return

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = f"【競合ウォッチ】{datetime.now().strftime('%Y/%m/%d')} の新着情報 ({len(results)}件)"

        body = "以下の更新がありました。\n\n"
        for i, res in enumerate(results, 1):
            body += f"{i}. [{res['company']}] {res['title']} ({res['source']})\n"
            body += f"   {res.get('url', 'No URL')}\n\n"
        
        body += f"スプレッドシートを確認: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, to_email, text)
            server.quit()
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def run(self):
        targets = self.fetch_config()
        if not targets:
            print("No targets found in Config sheet. Please add some.")
            return

        all_results = []
        for target in targets:
            company = target.get('Company Name')
            if not company: continue

            # 1. Check X (Grok)
            x_updates = self.fetch_x_updates(company)
            if x_updates:
                for update in x_updates:
                    all_results.append({
                        'company': company,
                        'source': 'X (Grok)',
                        'title': update.get('title', 'Update'),
                        'url': update.get('url'),
                        'summary': update.get('summary')
                    })
            
            # 2. Check Website News
            news_url = target.get('News URL')
            if news_url:
                web_updates = self.fetch_website_news(news_url, company)
                all_results.extend(web_updates)

            # 3. Check IR
            ir_url = target.get('IR URL (Optional)')
            if ir_url:
                ir_updates = self.fetch_ir_updates(ir_url, company)
                all_results.extend(ir_updates)

        if all_results:
            self.save_results(all_results)
            self.send_email(all_results)
        else:
            print("No relevant updates found.")

if __name__ == "__main__":
    monitor = CompetitorMonitor()
    monitor.run()
