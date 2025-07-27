import streamlit as st
import json
import openai

# Initialisation du client OpenAI avec la clé depuis les secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Liste des chapitres du programme spécifique de Première
chapitres = [
    "Fonctions",
    "Calcul littéral",
    "Statistiques",
    "Probabilités",
    "Géométrie",
    "Nombres et calculs",
    "Grandeurs et mesures"
]

st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")
st.markdown("Choisis un chapitre pour générer une question de QCM adaptée au programme.")

# Choix de chapitre
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

if st.button("🎲 Générer une question"):
    with st.spinner("GPT prépare une question adaptée..."):
        # Prompt personnalisé
        prompt = f"""
Tu es un professeur de mathématiques. Crée une question de QCM conforme au programme de mathématiques spécifiques de Première (enseignement commun). Chapitre : {chapitre_choisi}.

Présente la question dans ce format JSON :
{{
  "chapitre": "{chapitre_choisi}",
  "question": "...",
  "propositions": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "bonne_reponse": "A",
  "explication": "..."
}}
        """

        try:
            # Appel API OpenAI avec la nouvelle méthode
