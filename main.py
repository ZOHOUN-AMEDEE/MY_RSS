import feedparser
import json
import praw
import requests
import urllib.parse
import logging
import time
import re
import arxiv
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Tuple
from transformers import pipeline
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reddit Configuration
reddit = praw.Reddit(
    client_id="EOBdz3QUuh0i4DDCjc424Q",
    client_secret="mozO4jtP0n5qXg_Es0zIylvZCvDP1Q",
    user_agent="veille_tech:v1.0 (by u/WrapKindly4277)"
)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def clean_text(text: str) -> str:
    """Clean text by removing HTML tags and special characters."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def fetch_google_news_rss(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Fetch articles from Google News RSS."""
    try:
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=fr&gl=FR&ceid=FR:fr"
        feed = feedparser.parse(url)
        
        if not feed.entries:
            logger.warning(f"No articles found for query: {query}")
            return []
            
        articles = []
        for entry in feed.entries[:limit]:
            clean_summary = clean_text(entry.get("summary", ""))
            clean_title = clean_text(entry.get("title", ""))
            
            articles.append({
                "title": clean_title,
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": clean_summary,
                "source": "Google News"
            })
            
        return articles
    except Exception as e:
        logger.error(f"Error fetching Google News articles for {query}: {str(e)}")
        return []

def fetch_reddit_posts(subreddit_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch top posts from a subreddit."""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []

        for post in subreddit.hot(limit=limit):
            posts.append({
                "title": post.title,
                "url": post.url,
                "score": post.score,
                "comments": post.num_comments,
                "created_utc": post.created_utc,
                "selftext": post.selftext,
                "source": f"Reddit - r/{subreddit_name}"
            })

        return posts
    except Exception as e:
        logger.error(f"Error fetching Reddit posts for {subreddit_name}: {str(e)}")
        return []

def fetch_hackernews_posts(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch top posts from Hacker News."""
    try:
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url)
        top_stories_ids = response.json()
        
        posts = []
        for story_id in top_stories_ids[:limit]:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_response = requests.get(story_url)
            story_data = story_response.json()
            
            posts.append({
                "title": story_data.get("title", ""),
                "url": story_data.get("url", ""),
                "score": story_data.get("score", 0),
                "comments": story_data.get("descendants", 0),
                "created_utc": story_data.get("time", 0),
                "selftext": story_data.get("text", ""),
                "source": "Hacker News"
            })
        
        return posts
    except Exception as e:
        logger.error(f"Error fetching Hacker News posts: {str(e)}")
        return []

def fetch_arxiv_papers(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch recent papers from arXiv based on query."""
    try:
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = []
        for result in search.results():
            papers.append({
                "title": result.title,
                "url": result.entry_id,
                "summary": result.summary,
                "published": result.published.isoformat(),
                "authors": [author.name for author in result.authors],
                "pdf_url": result.pdf_url,
                "source": "arXiv"
            })

        return papers
    except Exception as e:
        logger.error(f"Error fetching arXiv papers for {query}: {str(e)}")
        return []

def summarize_content(content: List[Dict[str, Any]], max_length: int = 300, min_length: int = 100) -> str:
    """Generate a summary from content using BART model."""
    try:
        # Concatenate titles and content
        text = " ".join([
            item.get("title", "") + " " + 
            item.get("selftext", "") + " " + 
            item.get("summary", "")
            for item in content
        ])
        
        # Split text into chunks to respect BART's token limit
        chunk_size = 1000
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        summaries = []
        for chunk in chunks:
            if chunk.strip():
                summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                if summary:
                    summaries.append(summary[0]['summary_text'])
        
        return " ".join(summaries)
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Error generating summary"

def process_source(source_type: str, query: str = None) -> Dict[str, Any]:
    """Process a single source (Google News, Reddit, Hacker News, or arXiv)."""
    try:
        if source_type == "google_news":
            content = fetch_google_news_rss(query)
        elif source_type == "reddit":
            content = fetch_reddit_posts(query)
        elif source_type == "hackernews":
            content = fetch_hackernews_posts()
        elif source_type == "arxiv":
            content = fetch_arxiv_papers(query)
        else:
            logger.error(f"Unknown source type: {source_type}")
            return {}

        if content:
            summary = summarize_content(content)
            return {
                "summary": summary,
                "content": content
            }
        return {}
    except Exception as e:
        logger.error(f"Error processing {source_type}: {str(e)}")
        return {}

def main():
    """Main function to process all sources and save results."""
    try:
        # Define queries and sources
        queries = [
            "Machine Learning", "MLOps", "Technology",
            "Data Engineering", "Data Science", "Python",
            "Artificial Intelligence"
        ]
        
        subreddits = [
            "MachineLearning", "MLOps", "technology",
            "dataengineering", "datascience", "Python"
        ]

        veille_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "status": "success"
            },
            "data": {
                "google_news": {},
                "reddit": {},
                "hackernews": {},
                "arxiv": {}
            }
        }

        # Process Google News queries
        for query in queries:
            result = process_source("google_news", query)
            if result:
                veille_data["data"]["google_news"][query] = result

        # Process Reddit subreddits
        for subreddit in subreddits:
            result = process_source("reddit", subreddit)
            if result:
                veille_data["data"]["reddit"][subreddit] = result

        # Process Hacker News
        hn_result = process_source("hackernews")
        if hn_result:
            veille_data["data"]["hackernews"] = hn_result

        # Process arXiv papers
        for query in queries:
            result = process_source("arxiv", query)
            if result:
                veille_data["data"]["arxiv"][query] = result

        # Update metadata
        veille_data["metadata"]["queries_processed"] = {
            "google_news": len(veille_data["data"]["google_news"]),
            "reddit": len(veille_data["data"]["reddit"]),
            "hackernews": 1 if veille_data["data"]["hackernews"] else 0,
            "arxiv": len(veille_data["data"]["arxiv"])
        }

        # Save to JSON file
        with open("veille_tech.json", "w", encoding="utf-8") as f:
            json.dump(veille_data, f, indent=4, ensure_ascii=False, cls=DateTimeEncoder)
        
        logger.info("Tech watch data saved to veille_tech.json")
        return veille_data
        
    except Exception as e:
        logger.error(f"Critical error in main script: {str(e)}")
        raise

if __name__ == "__main__":
    main()
