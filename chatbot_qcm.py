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
        prompt = f"""
Tu es un professeur de mathématiques. Génére une question de type QCM pour le niveau Première - Mathématiques spécifiques (anciennement appelé "Maths expertes"). 

- Le thème est : [insérer ici le chapitre choisi, par exemple "Fonctions", "Suites", etc.].
- Rédige une question claire.
- Donne 4 propositions (A, B, C, D), dont une seule est correcte.
- Mélange aléatoirement l'ordre des propositions.
- Indique la lettre de la bonne réponse.
- Donne une explication claire et pédagogique pour justifier la bonne réponse, même si l'élève s’est trompé.

Réponds dans ce format JSON structuré :

{
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

"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            content = response.choices[0].message.content
            qcm_json = json.loads(content)

            st.subheader("❓ Question")
            st.write(qcm_json["question"])

            choix = st.radio("Réponses :", qcm_json["propositions"], key="choix")

            if st.button("✅ Valider ma réponse"):
                if choix.startswith(qcm_json["bonne_reponse"]):
                    st.success("Bonne réponse ! 🎉")
                else:
                    st.error(f"Mauvaise réponse. La bonne était : {qcm_json['bonne_reponse']}")
                st.info("🧠 Explication : " + qcm_json["explication"])

        except Exception as e:
            st.error("❌ Une erreur est survenue lors de la génération du QCM.")
            st.exception(e)
