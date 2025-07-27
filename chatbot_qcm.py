# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys

# Configuration de la page
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")

# Choix du chapitre
chapitres = [
    "Fonctions", "Dérivation", "Statistiques", "Suites",
    "Trigonométrie", "Probabilités", "Géométrie", "Nombres et calculs", "Grandeurs et mesures"
]
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

# Clé API
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncodeError):
    st.error("❌ Clé API invalide ou manquante.")
    sys.exit()

client = openai.OpenAI(api_key=key)

# Initialisation de session_state
if "qcm_data" not in st.session_state:
    st.session_state.qcm_data = None
if "answer_submitted" not in st.session_state:
    st.session_state.answer_submitted = False
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "nb_questions" not in st.session_state:
    st.session_state.nb_questions = 0
if "max_questions" not in st.session_state:
    st.session_state.max_questions = 10

# Bouton pour générer une question
if st.button("🎲 Nouvelle question") and st.session_state.nb_questions < st.session_state.max_questions:
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
}}"""
    }

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_data["instructions"]}],
            temperature=0.7
        )

        qcm_raw = json.loads(response.choices[0].message.content)

        # Mélange sécurisé
        original_options = qcm_raw["options"]
        correct_text = original_options[qcm_raw["correct_answer"]]
        items = list(original_options.items())
        random.shuffle(items)
        new_letters = ["A", "B", "C", "D"]
        shuffled_options = {new_letter: text for new_letter, (_, text) in zip(new_letters, items)}

        # Recalcul de la bonne lettre
        for new_letter, text in shuffled_options.items():
            if text == correct_text:
                correct_letter = new_letter
                break

        # Enregistrement en session
        st.session_state.qcm_data = {
            "question": qcm_raw["question"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "explanation": qcm_raw["explanation"]
        }

    except Exception as e:
        st.error(f"❌ Erreur GPT : {e}")
        st.session_state.qcm_data = None

# Affichage de la question
if st.session_state.qcm_data and st.session_state.nb_questions < st.session_state.max_questions:
    q = st.session_state.qcm_data

    st.markdown(f"**❓ Question :** {q['question']}")

    st.session_state.user_answer = st.radio(
        "Choisis ta réponse :",
        list(q["options"].keys()),
        format_func=lambda k: f"{k} : {q['options'][k]}"
    )

    if st.button("✅ Valider ma réponse") and not st.session_state.answer_submitted:
        st.session_state.answer_submitted = True
        user_letter = st.session_state.user_answer
        user_text = q["options"][user_letter]
        correct_letter = q["correct_answer"]
        correct_text = q["options"][correct_letter]

        if user_text == correct_text:
            st.success("✅ Bravo, c'est la bonne réponse !")
            st.session_state.score += 1
        else:
            st.error(f"❌ Mauvais choix. La bonne réponse était **{correct_letter} : {correct_text}**")

        st.markdown(f"**💡 Explication :** {q['explanation']}")
        st.session_state.nb_questions += 1

# Score et progression
st.markdown(f"### 🧮 Score : {st.session_state.score} / {st.session_state.nb_questions}")

# Fin du quiz
if st.session_state.nb_questions >= st.session_state.max_questions:
    st.success(f"🎉 Quiz terminé ! Tu as obtenu {st.session_state.score} / {st.session_state.max_questions} bonnes réponses.")
    if st.button("🔁 Recommencer un nouveau quiz"):
        st.session_state.score = 0
        st.session_state.nb_questions = 0
        st.session_state.qcm_data = None
        st.session_state.answer_submitted = False
