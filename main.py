import os
import feedparser
import time
import google.generativeai as genai
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load Keys
load_dotenv()

# Config
SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = os.getenv("BLOG_ID")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
DB_FILE = "processed_urls.txt"

RSS_URLS = [
    "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss?hl=en-CA&gl=CA&ceid=CA:en&hl=en-CA&gl=CA"
]

def get_blogger_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('blogger', 'v3', credentials=creds)

def is_already_processed(url):
    if not os.path.exists(DB_FILE): return False
    with open(DB_FILE, "r") as f:
        return url in f.read()

def mark_as_processed(url):
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def generate_content(title, summary):
    # Model name change kiya hai
    model = genai.GenerativeModel('models/gemini-1.5-flash') 
    prompt = f"Write a professional SEO blog post in HTML for: {title}. Context: {summary}. Use <h2> and <p> tags. No markdown blocks."
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.replace("```html", "").replace("```", "").strip()
        return None
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None
    
    
def main():
    service = get_blogger_service()
    print("🤖 Bot Started...")

    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]: 
            if is_already_processed(entry.link):
                print(f"⏩ Skipping: {entry.title}")
                continue

            print(f"✍️ Writing: {entry.title}")
            content = generate_content(entry.title, entry.summary)
            
            if content:
                body = {
                    "kind": "blogger#post",
                    "blog": {"id": BLOG_ID},
                    "title": entry.title,
                    "content": content,
                    "labels": ["AI News", "Tech"]
                }
                try:
                    response = service.posts().insert(blogId=BLOG_ID, body=body).execute()
                    print(f"🚀 Published! Link: {response.get('url')}")
                    mark_as_processed(entry.link)
                    time.sleep(10) 
                except Exception as e:
                    print(f"❌ Blogger Error: {e}")
            else:
                print(f"⚠️ Content generation failed for: {entry.title}")

if __name__ == "__main__":
    main()