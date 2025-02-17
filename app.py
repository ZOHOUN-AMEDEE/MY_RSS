import streamlit as st
from main import process_source  # Importez les fonctions de votre script principal

# Titre de l'application
st.title("Veille Technologique")

# Boutons pour chaque plateforme
platforms = ["Google News", "Reddit", "Hacker News", "arXiv"]

# Sélection de la plateforme
selected_platform = st.selectbox("Choisissez une plateforme", platforms)

# Entrée de l'utilisateur pour la requête
query = st.text_input("Entrez votre requête", "Machine Learning")

# Bouton pour lancer la recherche
if st.button("Rechercher"):
    st.write(f"Recherche sur {selected_platform} pour la requête : {query}")

    # Mapping des noms de plateformes aux types de source
    source_type_mapping = {
        "Google News": "google_news",
        "Reddit": "reddit",
        "Hacker News": "hackernews",
        "arXiv": "arxiv"
    }

    # Récupérer le type de source correspondant
    source_type = source_type_mapping.get(selected_platform)

    if source_type:
        # Traiter la source
        result = process_source(source_type, query)

        if result:
            # Afficher le résumé global
            st.subheader("Résumé global")
            st.write(result.get("summary", "Aucun résumé disponible."))

            # Afficher les posts avec un résumé individuel (si disponible)
            st.subheader("Posts")
            for item in result.get("content", []):
                st.write(f"**Titre:** {item.get('title', '')}")
                st.write(f"**Lien:** [{item.get('url', '')}]({item.get('url', '')})")
                st.write(f"**Source:** {item.get('source', '')}")

                # Afficher un résumé individuel si disponible
                if "summary" in item:
                    st.write(f"**Résumé:** {item.get('summary', '')}")
                else:
                    st.write("**Résumé:** Non disponible pour ce post.")

                st.write("---")
        else:
            st.error("Aucun résultat trouvé.")
    else:
        st.error("Plateforme non reconnue.")
