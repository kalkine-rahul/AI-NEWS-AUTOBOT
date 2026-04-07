AI News Automation Bot
An automated Python-based solution that fetches the latest AI/Tech news via RSS feeds, generates SEO-optimized blog posts using Google Gemini 2.5, and publishes them directly to Blogger.

🌟 Features
Automated News Sourcing: Pulls real-time news from multiple RSS feeds (Google News, etc.).

AI Content Generation: Uses the latest google-genai SDK with Gemini 2.5 Flash for high-quality, SEO-friendly HTML content.

Smart Duplicate Prevention: Maintains a local database (processed_urls.txt) to ensure no article is posted twice.

Blogger Integration: Fully automated publishing via Google Blogger API v3.

SEO Optimized: Automatically generates semantic HTML (h1, h2, p, ul) for better search engine ranking.

🛠️ Tech Stack
Language: Python 3.9+

AI Engine: Google Gemini (Generative AI)

APIs: Google Blogger API v3, Google OAuth 2.0

Libraries: feedparser, google-api-python-client, google-genai, python-dotenv

🚀 Getting Started
1. Prerequisites
A Google Cloud Project with Blogger API enabled.

OAuth 2.0 Credentials (credentials.json) from Google Cloud Console.

A Gemini API Key from Google AI Studio.

A Blogger Blog ID (Found in your Blogger dashboard settings).

2. Installation
Clone the repository and install the dependencies:

Bash
pip install feedparser google-auth-oauthlib google-api-python-client google-genai python-dotenv
3. Environment Setup
Create a .env file in the root directory and add your keys:

Code snippet
BLOG_ID=your_blogger_blog_id_here
GEMINI_API_KEY=your_gemini_api_key_here
4. Running the Bot
The first time you run the script, a browser window will open for Google Authentication. After logging in, a token.json file will be created for future automated sessions.

Bash
python main.py
🏗️ How it Works
Fetch: The bot scans predefined RSS URLs for the latest news entries.

Filter: It checks processed_urls.txt to skip articles that have already been published.

Generate: The bot sends the news title and summary to Gemini 2.5 Flash. The AI generates a full-length, SEO-optimized blog post in clean HTML.

Publish: The generated HTML is pushed to your Blogger site via the Blogger API with relevant tags like "AI News" and "Tech".

Record: The URL is saved to the local database to prevent future duplicates.

⚙️ Configuration
You can easily modify the RSS_URLS list in main.py to target different niches or regions:

Python
RSS_URLS = [
    "https://news.google.com/rss/search?q=AI&hl=en-US",
    "https://news.google.com/rss/search?q=MachineLearning&hl=en-US"
]
📝 License
Distributed under the MIT License. See LICENSE for more information.
