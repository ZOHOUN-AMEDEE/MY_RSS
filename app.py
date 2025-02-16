import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from main import main as fetch_tech_watch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        .stDataFrame {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_tech_watch_data():
    """Fetch and cache tech watch data"""
    try:
        return fetch_tech_watch()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def format_date(date_str):
    """Format date string to readable format"""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def create_content_df(content, source_type):
    """Create a DataFrame from content with appropriate columns"""
    if not content:
        return pd.DataFrame()

    if isinstance(content, list):
        df = pd.DataFrame(content)
    else:
        df = pd.DataFrame(content.get('content', []))

    # Select columns based on source type
    if source_type == "google_news":
        columns = ["title", "published", "url", "summary"]
    elif source_type == "reddit":
        columns = ["title", "score", "comments", "url", "created_utc"]
    elif source_type == "hackernews":
        columns = ["title", "score", "comments", "url"]
    elif source_type == "arxiv":
        columns = ["title", "published", "pdf_url", "authors", "summary"]
    
    # Filter columns that exist in the DataFrame
    columns = [col for col in columns if col in df.columns]
    return df[columns]

def display_content(content, source_type):
    """Display content in an interactive format"""
    df = create_content_df(content, source_type)
    
    if df.empty:
        st.warning(f"No data available for {source_type}")
        return

    # Format dates
    if "published" in df.columns:
        df["published"] = df["published"].apply(format_date)
    if "created_utc" in df.columns:
        df["created_utc"] = pd.to_datetime(df["created_utc"], unit='s').dt.strftime("%Y-%m-%d %H:%M")

    # Create interactive table
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "url": st.column_config.LinkColumn("Link"),
            "pdf_url": st.column_config.LinkColumn("PDF"),
            "authors": st.column_config.ListColumn("Authors"),
            "score": st.column_config.NumberColumn("Score", format="%d"),
            "comments": st.column_config.NumberColumn("Comments", format="%d")
        }
    )

def main():
    st.title("🔍 Tech Watch Dashboard")
    
    # Sidebar for refresh control
    with st.sidebar:
        st.header("Controls")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    # Load data
    data = get_tech_watch_data()
    if data is None:
        st.error("No data available
