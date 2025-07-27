# -*- coding: utf-8 -*-

import streamlit as st
import json
import openai

import sys

key = st.secrets["OPENAI_API_KEY"]

try:
    key.encode("ascii")
except UnicodeEncodeError:
    st.error("❌ La clé API contient un caractère accentué ou invisible. Veuillez en recréer une.")
    sys.exit()

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
        chapitre_choisi = chapitre_choisi or "Fonctions"

        # ✅ Définir le prompt ici, juste avant l'appel à l'API
# Génération propre du prompt
prompt_data = {
    "instructions": f"""Tu es un professeur de mathématiques. Génére une question de type QCM pour le niveau Première - Mathématiques spécifiques.

- Le thème est : {theme}
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

prompt = prompt_data["instructions"] + "\n\n" + json.dumps(prompt_data["json_format"], indent=2)
