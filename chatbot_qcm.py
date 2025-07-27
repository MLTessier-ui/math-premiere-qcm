# -*- coding: utf-8 -*-

import json
import openai
import streamlit as st
import sys

# Configuration de la page
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")
st.markdown("Choisis un chapitre pour générer une question de QCM adaptée au programme.")

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

# Choix de chapitre
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

# Clé API
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except UnicodeEncodeError:
    st.error("❌ La clé API contient un caractère accentué ou invisible. Veuillez en recréer une.")
    sys.exit()

# Initialisation du client OpenAI
client = openai.OpenAI(api_key=key)

if st.button("🎲 Générer une question"):
    with st.spinner("GPT prépare une question adaptée..."):

        # Génération du prompt
        prompt_data = {
            "instructions": f"""Tu es un professeur de mathématiques. Génére une question de type QCM pour le niveau Première - Mathématiques spécifiques.

- Le thème est : {chapitre_choisi}
- Rédige une question claire.
- Donne 4 propositions (A, B, C, D), dont une seule est correcte.
- Mélange aléatoirement l'ordre des propositions.
- Indique la lettre de la bonne réponse.
- Donne une explication claire et pédagogique pour justifier la bonne réponse, même si l'élève s’est trompé.

Réponds dans ce format JSON structuré :""",
            "json_format": {
                "question": "...",
                "options": {
                    "A": "...",
                    "B": "...",
                    "C": "...",
                    "D": "..."
                },
                "correct_answer": "B",
                "explanation": "..."
            }
        }

        prompt = prompt_da_
