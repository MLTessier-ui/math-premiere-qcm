# -*- coding: utf-8 -*-
import json
import random
import re
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

# Choix du nombre de questions et difficulté
nb_questions = st.slider("Nombre de questions", min_value=5, max_value=20, value=10)
difficulte = st.selectbox("Niveau de difficulté", ["Facile", "Moyen", "Difficile"])
mode_examen = st.checkbox("Mode examen (correction à la fin)")

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
    st.session_state.max_questions = nb_questions
if "exam_answers" not in st.session_state:
    st.session_state.exam_answers = []

st.session_state.max_questions = nb_questions

# Fonction pour générer un QCM unique
def generate_unique_qcm():
    prompt = f"""Tu es un professeur de mathématiques. Génère une question QCM niveau Première.

- Chapitre : {chapitre_choisi}
- Difficulté : {difficulte}
- Fournis UNE question claire.
- Propose 4 réponses DIFFÉRENTES.
- Donne UNE seule bonne réponse (ex: 'B').
- Donne une explication pédagogique.
- Ne commence pas par \"Voici une question...\".

Réponds STRICTEMENT en JSON valide (avec guillemets doubles pour les clés et les valeurs) et rien d'autre :
{{
  \"question\": \"...\",
  \"options\": {{
    \"A\": \"...\",
    \"B\": \"...\",
    \"C\": \"...\",
    \"D\": \"...\"
  }},
  \"correct_answer\": \"B\",
  \"explanation\": \"...\"
}}"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        try:
            qcm_raw = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.S)
            if match:
                qcm_raw = json.loads(match.group())
            else:
                st.error("❌ Format JSON invalide renvoyé par GPT.")
                return None

        # Vérification unicité des options
        if len(set(map(str.lower, qcm_raw["options"].values()))) < 4:
            return None

        # Mélange sécurisé
        original_options = list(qcm_raw["options"].items())
        correct_letter_orig = qcm_raw["correct_answer"]
        correct_text = qcm_raw["options"][correct_letter_orig]
        random.shuffle(original_options)
        new_letters = ["A", "B", "C", "D"]
        shuffled_options = {letter: text for letter, (_, text) in zip(new_letters, original_options)}
        correct_letter = [letter for letter, text in shuffled_options.items() if text == correct_text][0]

        return {
            "question": qcm_raw["question"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "explanation": qcm_raw["explanation"]
        }
    except Exception as e:
        st.error(f"❌ Erreur GPT : {e}")
        return None

# Génération initiale si aucune question
if st.session_state.qcm_data is None and st.session_state.nb_questions < st.session_state.max_questions:
    qcm = None
    for _ in range(4):  # réessayer jusqu'à 4 fois si problème de format ou doublons
        qcm = generate_unique_qcm()
        if qcm:
            break
    st.session_state.qcm_data = qcm

# Affichage de la question
if st.session_state.qcm_data and st.session_state.nb_questions < st.session_state.max_questions:
    q = st.session_state.qcm_data
    st.progress(st.session_state.nb_questions / st.session_state.max_questions)
    st.markdown(f"📌 Il reste **{st.session_state.max_questions - st.session_state.nb_questions}** question(s) sur {st.session_state.max_questions}")
    st.markdown(f"**❓ Question :** {q['question']}")

    st.session_state.user_answer = st.radio(
        "Choisis ta réponse :",
        list(q["options"].keys()),
        format_func=lambda k: f"{k} : {q['options'][k]}",
        index=None
    )

    if st.button("✅ Valider ma réponse") and st.session_state.user_answer is not None:
        user_letter = st.session_state.user_answer
        if mode_examen:
            st.session_state.exam_answers.append((q, user_letter))
        else:
            if user_letter == q["correct_answer"]:
                st.success("✅ Bravo, c'est la bonne réponse !")
                st.session_state.score += 1
            else:
                st.error(f"❌ Mauvais choix. La bonne réponse était **{q['correct_answer']} : {q['options'][q['correct_answer']]}**")
            st.markdown(f"**💡 Explication :** {q['explanation']}")
        st.session_state.nb_questions += 1

        # Charger la prochaine question
        if st.session_state.nb_questions < st.session_state.max_questions:
            st.session_state.qcm_data = None
            st.rerun()

# Fin du quiz
if st.session_state.nb_questions >= st.session_state.max_questions:
    if mode_examen:
        score_final = 0
        for q, user_letter in st.session_state.exam_answers:
            if user_letter == q["correct_answer"]:
                score_final += 1
        st.success(f"🎉 Examen terminé ! Score : {score_final}/{st.session_state.max_questions}")
        for q, user_letter in st.session_state.exam_answers:
            if user_letter == q["correct_answer"]:
                st.markdown(f"✅ {q['question']} — **Bonne réponse** ({q['correct_answer']})")
            else:
                st.markdown(f"❌ {q['question']} — Mauvaise réponse. La bonne était **{q['correct_answer']} : {q['options'][q['correct_answer']]}**")
            st.markdown(f"💡 {q['explanation']}")
    else:
        st.success(f"🎉 Quiz terminé ! Tu as obtenu {st.session_state.score} / {st.session_state.max_questions} bonnes réponses.")

    if st.button("🔁 Recommencer un nouveau quiz"):
        st.session_state.score = 0
        st.session_state.nb_questions = 0
        st.session_state.qcm_data = None
        st.session_state.answer_submitted = False
        st.session_state.exam_answers = []
        st.rerun()
