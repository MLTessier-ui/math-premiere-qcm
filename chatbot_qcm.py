# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys

st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")
st.markdown("Choisis un chapitre pour générer une question de QCM adaptée au programme.")

# Liste de chapitres disponibles
chapitres = [
    "Fonctions", "Dérivation", "Statistiques", "Suites",
    "Trigonométrie", "Probabilités", "Géométrie", "Nombres et calculs", "Grandeurs et mesures"
]
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

# Vérification API key
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncodeError):
    st.error("❌ Clé API invalide ou manquante.")
    sys.exit()

client = openai.OpenAI(api_key=key)

# Initialisation des états Streamlit
if "qcm_data" not in st.session_state:
    st.session_state.qcm_data = None
if "answer_submitted" not in st.session_state:
    st.session_state.answer_submitted = False
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None

# Génération de la question
if st.button("🎲 Générer une question"):
    st.session_state.answer_submitted = False
    st.session_state.user_answer = None

    prompt_data = {
        "instructions": f"""Tu es un professeur de mathématiques. Génère une question QCM niveau Première.

- Le chapitre est : {chapitre_choisi}
- Fournis UNE question claire.
- Propose 4 réponses DIFFÉRENTES.
- Donne UNE seule bonne réponse (ex: 'B').
- Donne une explication pédagogique.
- Ne commence pas par "Voici une question...".

Réponds en JSON comme ceci :
{{
  "question": "...",
  "options": {{
    "A": "...",
    "B": "...",
    "C": "...",
    "D": "..."
  }},
  "correct_answer": "B",
  "explanation": "..."
}}""",
    }

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_data["instructions"]}],
            temperature=0.7
        )

        qcm_raw = json.loads(response.choices[0].message.content)

        # Mélange des options localement pour éviter les doublons
        items = list(qcm_raw["options"].items())
        random.shuffle(items)
        shuffled_options = {letter: text for letter, text in zip(["A", "B", "C", "D"], [t[1] for t in items])}
        correct_index = [t[1] for t in items].index(qcm_raw["options"][qcm_raw["correct_answer"]])
        correct_letter = ["A", "B", "C", "D"][correct_index]

        st.session_state.qcm_data = {
            "question": qcm_raw["question"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "explanation": qcm_raw["explanation"]
        }

    except Exception as e:
        st.error(f"❌ Erreur GPT : {e}")
        st.session_state.qcm_data = None

# Affichage de la question si elle existe
if st.session_state.qcm_data:
    q = st.session_state.qcm_data

    st.markdown(f"**❓ Question :** {q['question']}")

    st.session_state.user_answer = st.radio(
        "Choisis ta réponse :", 
        list(q["options"].keys()),
        format_func=lambda k: f"{k} : {q['options'][k]}"
    )

    if st.button("✅ Valider ma réponse"):
        st.session_state.answer_submitted = True

# Affichage du feedback
if st.session_state.answer_submitted and st.session_state.user_answer:
    q = st.session_state.qcm_data
    if st.session_state.user_answer == q["correct_answer"]:
        st.success("✅ Bravo, c'est la bonne réponse !")
    else:
        bonne = q["correct_answer"]
        st.error(f"❌ Mauvais choix. La bonne réponse était **{bonne} : {q['options'][bonne]}**")
    st.markdown(f"**💡 Explication :** {q['explanation']}")
