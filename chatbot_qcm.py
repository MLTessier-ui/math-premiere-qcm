# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys

st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")
st.markdown("Choisis un chapitre pour générer une question de QCM adaptée au programme.")

# Liste de chapitres
chapitres = [
    "Fonctions", "Dérivation", "Statistiques", "Suites",
    "Trigonométrie", "Probabilités", "Géométrie", "Nombres et calculs", "Grandeurs et mesures"
]
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

# Vérification de la clé API
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

    prompt = f"""
Tu es un professeur de mathématiques en Première. Génère une question QCM sur le chapitre : {chapitre_choisi}.
- Donne UNE question claire.
- Propose 4 réponses DIFFÉRENTES (A, B, C, D).
- Une SEULE bonne réponse (ex: "C").
- Indique le champ "correct_answer": "lettre", et donne une explication dans "explanation".
- Réponds uniquement en JSON (pas de phrases ou d'intro).

Format :
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
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        qcm_raw = json.loads(response.choices[0].message.content)

        # Vérifie que toutes les options sont uniques
        options_text = list(qcm_raw["options"].values())
        if len(set(options_text)) < 4:
            st.error("❌ Certaines réponses sont identiques. Réessaie.")
            st.stop()

        # Vérifie que la bonne réponse est bien dans les options
        correct_text = qcm_raw["options"][qcm_raw["correct_answer"]]
        if correct_text not in options_text:
            st.error("❌ La bonne réponse n’est pas dans les propositions. Réessaie.")
            st.stop()

        # Mélange les options tout en retrouvant la bonne lettre
        items = list(qcm_raw["options"].items())
        random.shuffle(items)

        new_letters = ["A", "B", "C", "D"]
        shuffled_options = {new_letter: text for new_letter, (_, text) in zip(new_letters, items)}

        # Retrouve la nouvelle lettre de la bonne réponse
        correct_letter = next(
            (letter for letter, text in shuffled_options.items() if text == correct_text), None
        )

        if correct_letter is None:
            st.error("❌ Erreur interne : impossible de retrouver la bonne réponse.")
            st.stop()

        # Sauvegarde des données
        st.session_state.qcm_data = {
            "question": qcm_raw["question"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "explanation": qcm_raw["explanation"]
        }

    except Exception as e:
        st.error(f"❌ Erreur GPT : {e}")
        st.session_state.qcm_data = None

# Affichage de la question si disponible
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

# Feedback
if st.session_state.answer_submitted and st.session_state.user_answer:
    q = st.session_state.qcm_data
    user = st.session_state.user_answer
    correct = q["correct_answer"]
    if user == correct:
        st.success("✅ Bravo, c'est la bonne réponse !")
    else:
        st.error(f"❌ Mauvais choix. La bonne réponse était **{correct} : {q['options'][correct]}**")
    st.markdown(f"**💡 Explication :** {q['explanation']}")
