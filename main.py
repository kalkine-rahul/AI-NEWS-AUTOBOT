import os
import feedparser
import time
from dotenv import load_dotenv

# Blogger imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# New Gemini SDK (google-genai)
from google import genai
# from google.genai import types   # Uncomment only if you need advanced config later

# Load environment variables
load_dotenv()

# Config
SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = os.getenv("BLOG_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DB_FILE = "processed_urls.txt"

RSS_URLS = [
    "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss?hl=en-CA&gl=CA&ceid=CA:en"
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
    if not os.path.exists(DB_FILE):
        return False
    with open(DB_FILE, "r") as f:
        return url in f.read()

def mark_as_processed(url):
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def generate_content(title, summary):
    # Create client with new SDK
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Recommended models (as of 2026):
    # "gemini-2.5-flash"     → Best balance of speed + quality (recommended)
    # "gemini-2.5-pro"       → Higher quality but slower & more expensive
    model_name = "gemini-2.5-flash"

    prompt = f"""Write a professional, engaging SEO-optimized blog post in clean HTML for this news article.

Title: {title}
Summary/Context: {summary}

Requirements:
- Use semantic HTML: <h1> for main title, <h2> for subheadings, <p> for paragraphs, <ul>/<li> if needed.
- Make it informative, neutral, and readable.
- Naturally include SEO keywords from the title.
- Do NOT wrap the output in ```html or any markdown code blocks.
- Start directly with the HTML content."""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        if response and hasattr(response, 'text') and response.text:
            html_content = response.text.replace("```html", "").replace("```", "").strip()
            return html_content
        else:
            print("⚠️ Empty response from Gemini")
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
                    time.sleep(15)   # Increased a bit to avoid rate limits
                except Exception as e:
                    print(f"❌ Blogger Error: {e}")
            else:
                print(f"⚠️ Content generation failed for: {entry.title}")

if __name__ == "__main__":
    main()
