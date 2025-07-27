# -*- coding: utf-8 -*-

import json
import openai
import streamlit as st
import sys

# Configuration de la page Streamlit
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")
st.markdown("Choisis un chapitre pour générer une question de QCM adaptée au programme.")

# Liste de chapitres disponibles
chapitres = [
    "Fonctions",
    "Dérivation",
    "Statistiques",
    "Suites",
    "Trigonométrie",
    "Probabilités",
    "Géométrie",
    "Nombres et calculs",
    "Grandeurs et mesures"
]

# Choix du chapitre
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

# Récupération de la clé API
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncodeError):
    st.error("❌ Clé API invalide ou manquante.")
    sys.exit()

# Initialisation du client OpenAI
client = openai.OpenAI(api_key=key)

# Bouton de génération
if st.button("🎲 Générer une question"):
    with st.spinner("GPT prépare une question adaptée..."):
        # Construction du prompt
        prompt_data = {
            "instructions": f"""Tu es un professeur de mathématiques. Génére une question de type QCM pour le niveau Première - Mathématiques.

- Le chapitre est : {chapitre_choisi}
- Rédige une question claire.
- Donne 4 propositions (A, B, C, D), dont une seule est correcte.
- Mélange aléatoirement l'ordre des propositions.
- Indique la lettre de la bonne réponse.
- Donne une explication claire et pédagogique.

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

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            data = json.loads(response.choices[0].message.content)

            st.markdown(f"**❓ Question :** {data['question']}")

            # Affichage des options
            user_answer = st.radio(
                "Choisis ta réponse :",
                list(data["options"].keys()),
                format_func=lambda x: f"{x} : {data['options'][x]}",
                key="qcm_radio"
            )

            # Bouton de validation
            if st.button("✅ Valider ma réponse"):
                if user_answer == data["correct_answer"]:
                    st.success("✅ Bonne réponse !")
                else:
                    st.error(
                        f"❌ Mauvaise réponse. La bonne réponse était {data['correct_answer']} : {data['options'][data['correct_answer']]}"
                    )
                st.markdown(f"**Explication** : {data['explanation']}")

        except Exception as e:
            st.error(f"❌ Erreur lors de la génération : {e}")
