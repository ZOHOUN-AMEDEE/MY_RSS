import streamlit as st
import json
from datetime import datetime
from main import process_source

# Set page configuration
st.set_page_config(
    page_title="Veille Technologique",
    page_icon="📚",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    .highlight-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📚 Veille Technologique")
st.markdown("*Explorez les dernières nouvelles et discussions technologiques*")

# Create two columns for input controls
col1, col2 = st.columns(2)

with col1:
    # Platform selection
    platforms = ["Google News", "Reddit", "Hacker News", "arXiv"]
    selected_platform = st.selectbox("Plateforme", platforms)

with col2:
    # Query input
    query = st.text_input("Requête", "Machine Learning")

# Search button
if st.button("🔍 Rechercher"):
    with st.spinner("Recherche en cours..."):
        # Map platform names to source types
        source_type_mapping = {
            "Google News": "google_news",
            "Reddit": "reddit",
            "Hacker News": "hackernews",
            "arXiv": "arxiv"
        }
        
        source_type = source_type_mapping.get(selected_platform)
        
        if source_type:
            result = process_source(source_type, query)
            
            if result and isinstance(result, dict):
                # Display overall summary
                if "summary" in result and isinstance(result["summary"], dict):
                    st.header("📝 Résumé général")
                    st.markdown(f"*{result['summary'].get('overall', 'Aucun résumé disponible.')}*")
                    
                    # Display category-specific highlights
                    if "highlights" in result["summary"]:
                        st.header("✨ Points clés")
                        highlights = result["summary"]["highlights"]
                        
                        for category, summary in highlights.items():
                            if summary:
                                with st.expander(f"📌 {category.title()}"):
                                    st.write(summary)
                
                # Display content items
                if "content" in result:
                    st.header("📄 Articles et discussions")
                    
                    # Create tabs for different content views
                    tab1, tab2 = st.tabs(["Vue détaillée", "Vue compacte"])
                    
                    with tab1:
                        for item in result["content"]:
                            with st.container():
                                st.markdown("---")
                                st.subheader(item.get("title", "Sans titre"))
                                
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    if "summary" in item:
                                        st.markdown(f"*{item['summary']}*")
                                    if "selftext" in item and item["selftext"]:
                                        st.text(item["selftext"][:200] + "..." if len(item["selftext"]) > 200 else item["selftext"])
                                
                                with col2:
                                    st.markdown(f"**Source:** {item.get('source', 'Unknown')}")
                                    st.markdown(f"[Lien vers l'article]({item.get('url', '#')})")
                    
                    with tab2:
                        # Create a dataframe for compact view
                        import pandas as pd
                        df = pd.DataFrame(result["content"])
                        if not df.empty:
                            df = df[["title", "source", "url"]].copy()
                            st.dataframe(df, use_container_width=True)
            else:
                st.error("Format de résultat invalide.")
        else:
            st.error("Plateforme non reconnue.")

# Add footer
st.markdown("---")
st.markdown("*Développé avec ❤️ pour la veille technologique*")
