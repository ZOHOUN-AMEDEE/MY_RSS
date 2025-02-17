# app.py
import streamlit as st
import json
from datetime import datetime
import main  # importing your main script

def load_data():
    try:
        with open("veiltech.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def refresh_data():
    main.main()  # Run the data collection process
    return load_data()

def render_content(content_list):
    for item in content_list:
        st.write("---")
        st.markdown(f"### {item['title']}")
        st.write(f"Source: {item['source']}")
        if 'published' in item:
            st.write(f"Published: {item['published']}")
        if 'score' in item:
            st.write(f"Score: {item['score']} | Comments: {item['comments']}")
        if 'summary' in item:
            st.write("Summary:", item['summary'])
        st.markdown(f"[Read More]({item['url']})")

def main():
    st.set_page_config(
        page_title="Tech Watch Dashboard",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Tech Watch Dashboard")
    st.markdown("Stay updated with the latest in technology across multiple platforms")

    # Add refresh button
    if st.button("🔄 Refresh Data"):
        with st.spinner("Fetching fresh data..."):
            data = refresh_data()
            st.success("Data refreshed successfully!")
    else:
        data = load_data()

    if not data:
        st.warning("No data available. Please click the refresh button to fetch data.")
        return

    # Display last update time
    st.info(f"Last updated: {data['metadata']['generated_at']}")

    # Create tabs for different platforms
    platforms = ["Google News", "Reddit", "Hacker News", "arXiv"]
    tabs = st.tabs(platforms)

    # Google News Tab
    with tabs[0]:
        st.header("Google News")
        topics = list(data['data']['google_news'].keys())
        selected_topic = st.selectbox("Select Topic", topics, key="google_news")
        
        if selected_topic in data['data']['google_news']:
            st.subheader(f"Summary for {selected_topic}")
            st.write(data['data']['google_news'][selected_topic]['summary'])
            st.subheader("Articles")
            render_content(data['data']['google_news'][selected_topic]['content'])

    # Reddit Tab
    with tabs[1]:
        st.header("Reddit")
        subreddits = list(data['data']['reddit'].keys())
        selected_subreddit = st.selectbox("Select Subreddit", subreddits, key="reddit")
        
        if selected_subreddit in data['data']['reddit']:
            st.subheader(f"Summary for r/{selected_subreddit}")
            st.write(data['data']['reddit'][selected_subreddit]['summary'])
            st.subheader("Posts")
            render_content(data['data']['reddit'][selected_subreddit]['content'])

    # Hacker News Tab
    with tabs[2]:
        st.header("Hacker News")
        if data['data']['hackernews']:
            st.subheader("Summary")
            st.write(data['data']['hackernews']['summary'])
            st.subheader("Top Stories")
            render_content(data['data']['hackernews']['content'])

    # arXiv Tab
    with tabs[3]:
        st.header("arXiv Papers")
        topics = list(data['data']['arxiv'].keys())
        selected_topic = st.selectbox("Select Topic", topics, key="arxiv")
        
        if selected_topic in data['data']['arxiv']:
            st.subheader(f"Summary for {selected_topic}")
            st.write(data['data']['arxiv'][selected_topic]['summary'])
            st.subheader("Papers")
            render_content(data['data']['arxiv'][selected_topic]['content'])

if __name__ == "__main__":
    main()
