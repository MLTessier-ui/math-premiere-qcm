# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys
import re

# Configuration de la page
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")

# Choix du chapitre et paramètres
chapitres = [
    "Fonctions", "Dérivation", "Statistiques", "Suites",
    "Trigonométrie", "Probabilités", "Géométrie", "Nombres et calculs", "Grandeurs et mesures"
]
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)
nb_questions = st.slider("Nombre de questions", 5, 20, 10)
difficulte = st.selectbox("Niveau de difficulté", ["Facile", "Moyen", "Difficile"])
mode_examen = st.checkbox("Mode examen (corrigé à la fin)")

# Clé API
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncodeError):
    st.error("❌ Clé API invalide ou manquante.")
    st.stop()

client = openai.OpenAI(api_key=key)

# Initialisation de session_state
if "qcm_data" not in st.session_state:
    st.session_state.qcm_data = None
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "nb_questions" not in st.session_state:
    st.session_state.nb_questions = 0
if "max_questions" not in st.session_state:
    st.session_state.max_questions = nb_questions
if "seen_questions" not in st.session_state:
    st.session_state.seen_questions = set()
if "answers_log" not in st.session_state:
    st.session_state.answers_log = []

st.session_state.max_questions = nb_questions

# Fonction de génération sécurisée
def generate_unique_qcm():
    prompt_data = f"""Tu es un professeur de mathématiques. Génère une question QCM niveau Première.

- Chapitre : {chapitre_choisi}
- Difficulté : {difficulte}
- Fournis UNE question claire.
- Propose 4 réponses DIFFÉRENTES.
- Donne UNE seule bonne réponse (ex: 'B').
- Donne une explication pédagogique.
- Réponds STRICTEMENT en JSON valide (avec guillemets doubles pour les clés et les valeurs) et rien d'autre.
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
            messages=[{"role": "user", "content": prompt_data}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        try:
            qcm_raw = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.S)
            if match:
                try:
                    qcm_raw = json.loads(match.group())
                except json.JSONDecodeError:
                    return None
            else:
                return None

        if qcm_raw["question"] in st.session_state.seen_questions:
            return None
        st.session_state.seen_questions.add(qcm_raw["question"])

        # Mélange des options
        original_options = qcm_raw["options"]
        items = list(original_options.items())
        random.shuffle(items)
        new_letters = ["A", "B", "C", "D"]
        shuffled_options = {new_letter: text for new_letter, (_, text) in zip(new_letters, items)}

        correct_text = original_options[qcm_raw["correct_answer"]]
        correct_letter = next(letter for letter, text in shuffled_options.items() if text == correct_text)

        return {
            "question": qcm_raw["question"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "explanation": qcm_raw["explanation"]
        }
    except Exception:
        return None

# Lancer une question si nécessaire
if (not st.session_state.qcm_data) and (st.session_state.nb_questions < st.session_state.max_questions):
    while True:
        qcm = generate_unique_qcm()
        if qcm:
            st.session_state.qcm_data = qcm
            break

# Affichage de la question
if st.session_state.qcm_data and st.session_state.nb_questions < st.session_state.max_questions:
    q = st.session_state.qcm_data
    st.markdown(f"**❓ Question {st.session_state.nb_questions+1}/{st.session_state.max_questions} :** {q['question']}")
    st.markdown(f"📌 Il reste {st.session_state.max_questions - st.session_state.nb_questions} questions")

    st.session_state.user_answer = st.radio(
        "Choisis ta réponse :",
        list(q["options"].keys()),
        format_func=lambda k: f"{k} : {q['options'][k]}",
        index=None
    )

    if st.button("✅ Valider ma réponse") and st.session_state.user_answer:
        user_letter = st.session_state.user_answer
        correct_letter = q["correct_answer"]
        is_correct = user_letter == correct_letter

        if not mode_examen:
            if is_correct:
                st.success("✅ Bravo, c'est la bonne réponse !")
            else:
                st.error(f"❌ Mauvais choix. La bonne réponse était **{correct_letter} : {q['options'][correct_letter]}**")
            st.markdown(f"<span style='color:black;'><b>💡 Explication :</b> {q['explanation']}</span>", unsafe_allow_html=True)

        st.session_state.answers_log.append({
            "question": q["question"],
            "votre réponse": f"{user_letter} : {q['options'][user_letter]}",
            "bonne réponse": f"{correct_letter} : {q['options'][correct_letter]}",
            "explication": q["explanation"],
            "correct": is_correct
        })

        if is_correct:
            st.session_state.score += 1
        st.session_state.nb_questions += 1
        st.session_state.qcm_data = None
        st.rerun()

# Fin du quiz
if st.session_state.nb_questions >= st.session_state.max_questions:
    st.success(f"🎉 Quiz terminé ! Tu as obtenu {st.session_state.score} / {st.session_state.max_questions} bonnes réponses.")
    if mode_examen:
        st.markdown("## 📄 Corrigé complet")
        for i, rep in enumerate(st.session_state.answers_log, 1):
            st.markdown(f"**Q{i} :** {rep['question']}")
            st.markdown(f"Votre réponse : {rep['votre réponse']}")
            st.markdown(f"Bonne réponse : {rep['bonne réponse']}")
            st.markdown(f"<span style='color:black;'>💡 {rep['explication']}</span>", unsafe_allow_html=True)
            st.markdown("---")

    if st.button("🔁 Recommencer un nouveau quiz"):
        st.session_state.score = 0
        st.session_state.nb_questions = 0
        st.session_state.qcm_data = None
        st.session_state.answers_log.clear()
        st.session_state.seen_questions.clear()
        st.rerun()
