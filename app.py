import streamlit as st
import json

# Charger les données depuis le fichier JSON
def load_data():
    try:
        with open("veiltech.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

# Interface Streamlit
st.title("📰 Veille Technologique")
st.write("Consultez les résumés et les liens des derniers articles et posts sur différentes plateformes.")

data = load_data()
if data:
    sources = list(data["data"].keys())
    selected_source = st.selectbox("Choisissez une source :", sources)
    
    if selected_source in data["data"]:
        if selected_source in ["google_news", "arxiv"]:
            queries = list(data["data"][selected_source].keys())
            selected_query = st.selectbox("Choisissez un sujet :", queries)
            
            if selected_query in data["data"][selected_source]:
                st.subheader("Résumé")
                st.write(data["data"][selected_source][selected_query]["summary"])
                
                st.subheader("Articles")
                for item in data["data"][selected_source][selected_query]["content"]:
                    st.markdown(f"**[{item['title']}]({item['url']})**")
                    st.write(item.get("summary", "Aucun résumé disponible."))
                    st.write("---")
        
        elif selected_source == "reddit":
            subreddits = list(data["data"][selected_source].keys())
            selected_subreddit = st.selectbox("Choisissez un subreddit :", subreddits)
            
            if selected_subreddit in data["data"][selected_source]:
                st.subheader("Résumé")
                st.write(data["data"][selected_source][selected_subreddit]["summary"])
                
                st.subheader("Posts")
                for item in data["data"][selected_source][selected_subreddit]["content"]:
                    st.markdown(f"**[{item['title']}]({item['url']})**")
                    st.write(f"👍 {item['score']} | 💬 {item['comments']} commentaires")
                    st.write(item.get("selftext", "Aucun contenu disponible."))
                    st.write("---")
        
        elif selected_source == "hackernews":
            st.subheader("Résumé")
            st.write(data["data"][selected_source]["summary"])
            
            st.subheader("Posts")
            for item in data["data"][selected_source]["content"]:
                st.markdown(f"**[{item['title']}]({item['url']})**")
                st.write(f"👍 {item['score']} | 💬 {item['comments']} commentaires")
                st.write("---")
else:
    st.error("Impossible de charger les données.")
