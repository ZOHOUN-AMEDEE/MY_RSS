import streamlit as st
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
from main import main as fetch_tech_watch

# Page configuration
st.set_page_config(
    page_title="Tech Watch Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .stAlert {
            padding: 10px;
            margin-bottom: 20px;
        }
        .source-card {
            padding: 20px;
            border-radius: 5px;
            margin: 10px 0;
            background-color: #f0f2f6;
        }
        .metric-card {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

def load_data():
    """Load data from JSON file or fetch new data"""
    try:
        with open("veille_tech.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def format_date(date_str):
    """Format date string to readable format"""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def display_source_metrics(data):
    """Display metrics for each source"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Google News Articles",
            len(data["data"]["google_news"])
        )
    with col2:
        st.metric(
            "Reddit Subreddits",
            len(data["data"]["reddit"])
        )
    with col3:
        st.metric(
            "Hacker News Posts",
            len(data["data"]["hackernews"]["content"]) if "content" in data["data"]["hackernews"] else 0
        )
    with col4:
        st.metric(
            "arXiv Papers",
            len(data["data"]["arxiv"])
        )

def display_content_table(content, source_type):
    """Display content in a formatted table"""
    if not content:
        st.warning(f"No data available for {source_type}")
        return

    if isinstance(content, list):
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(content)
    else:
        # If content is nested in 'content' key
        df = pd.DataFrame(content.get('content', []))

    # Select and rename columns based on source type
    if source_type == "google_news":
        columns = ["title", "published", "url"]
        rename_dict = {"title": "Title", "published": "Published", "url": "URL"}
    elif source_type == "reddit":
        columns = ["title", "score", "comments", "url"]
        rename_dict = {"title": "Title", "score": "Score", "comments": "Comments", "url": "URL"}
    elif source_type == "hackernews":
        columns = ["title", "score", "comments", "url"]
        rename_dict = {"title": "Title", "score": "Score", "comments": "Comments", "url": "URL"}
    elif source_type == "arxiv":
        columns = ["title", "published", "pdf_url"]
        rename_dict = {"title": "Title", "published": "Published", "pdf_url": "PDF URL"}
    
    # Filter and rename columns
    df = df[columns].rename(columns=rename_dict)
    
    # Format date columns if they exist
    if "Published" in df.columns:
        df["Published"] = df["Published"].apply(format_date)
    
    # Convert URLs to clickable links
    url_col = "URL" if "URL" in df.columns else "PDF URL"
    df[url_col] = df[url_col].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>')
    
    # Display table with HTML
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

def main():
    st.title("🔍 Tech Watch Dashboard")
    
    # Add refresh button
    if st.button("🔄 Fetch New Data"):
        with st.spinner("Fetching fresh data..."):
            fetch_tech_watch()
        st.success("Data refreshed successfully!")
    
    # Load data
    data = load_data()
    if data is None:
        st.error("No data found. Please fetch new data.")
        return
    
    # Display last update time
    st.info(f"Last updated: {format_date(data['metadata']['generated_at'])}")
    
    # Display source metrics
    display_source_metrics(data)
    
    # Create tabs for different sources
    tabs = st.tabs(["Google News", "Reddit", "Hacker News", "arXiv"])
    
    # Google News Tab
    with tabs[0]:
        st.header("📰 Google News")
        for query, content in data["data"]["google_news"].items():
            with st.expander(f"Query: {query}"):
                st.subheader("Summary")
                st.write(content["summary"])
                st.subheader("Articles")
                display_content_table(content["content"], "google_news")
    
    # Reddit Tab
    with tabs[1]:
        st.header("🤖 Reddit")
        for subreddit, content in data["data"]["reddit"].items():
            with st.expander(f"Subreddit: r/{subreddit}"):
                st.subheader("Summary")
                st.write(content["summary"])
                st.subheader("Posts")
                display_content_table(content["content"], "reddit")
    
    # Hacker News Tab
    with tabs[2]:
        st.header("💻 Hacker News")
        st.subheader("Summary")
        st.write(data["data"]["hackernews"]["summary"])
        st.subheader("Posts")
        display_content_table(data["data"]["hackernews"], "hackernews")
    
    # arXiv Tab
    with tabs[3]:
        st.header("📚 arXiv")
        for query, content in data["data"]["arxiv"].items():
            with st.expander(f"Query: {query}"):
                st.subheader("Summary")
                st.write(content["summary"])
                st.subheader("Papers")
                display_content_table(content["content"], "arxiv")

if __name__ == "__main__":
    main()
