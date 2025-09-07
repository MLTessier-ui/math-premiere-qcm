# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

from qcm_engine import THEMES, generate_set, generate_exam, to_dict

# ===============================
# Configuration Streamlit
# ===============================
st.set_page_config(page_title="QCM Math Première", page_icon="📘", layout="centered")

# ===============================
# Initialisation de session
# ===============================
if "mode" not in st.session_state:
    st.session_state.mode = None
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# ===============================
# Fonctions utilitaires
# ===============================
def reset_session():
    st.session_state.questions = []
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.answers = []

def save_results_to_csv(results):
    """Sauvegarde des résultats uniquement en mode examen"""
    filename = "resultats.csv"
    df = pd.DataFrame(results)
    if os.path.exists(filename):
        old = pd.read_csv(filename)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(filename, index=False)

# ===============================
# Choix du mode
# ===============================
st.title("📘 QCM de mathématiques - Première")
mode = st.radio("Choisissez le mode :", ["Entraînement", "Examen"], index=0)

# ===============================
# Mode Entraînement
# ===============================
if mode == "Entraînement":
    st.session_state.mode = "Entraînement"

    theme = st.selectbox("Choisir un thème", THEMES + ["Auto"])
    nb_q = st.slider("Nombre de questions", min_value=5, max_value=10, value=5, step=1)

    if st.button("Démarrer l'entraînement"):
        reset_session()
        st.session_state.questions = generate_set(theme, "Moyen", nb_q)
        st.session_state.mode = "Quiz"

# ===============================
# Mode Examen
# ===============================
elif mode == "Examen":
    if st.button("Commencer l'examen (12 questions)"):
        reset_session()
        st.session_state.questions = generate_exam()
        st.session_state.mode = "Examen en cours"

# ===============================
# Affichage des questions
# ===============================
if st.session_state.mode in ["Quiz", "Examen en cours"]:
    questions = st.session_state.questions
    index = st.session_state.current_index

    if index < len(questions):
        q = questions[index]
        st.subheader(f"Question {index+1}/{len(questions)} - {q.theme}")
        st.write(q.stem)

        choix = st.radio("Choix :", q.choices, key=f"q{index}")

        if st.button("Valider la réponse", key=f"valider_{index}"):
            correct = (choix == q.choices[q.correct_index])
            if correct:
                st.success("✅ Bonne réponse !")
                st.session_state.score += 1
            else:
                st.error(f"❌ Mauvaise réponse. La bonne réponse était : {q.choices[q.correct_index]}")

            st.info(q.explanation)
            st.session_state.answers.append({
                "theme": q.theme,
                "question": q.stem,
                "choix": choix,
                "correct": q.choices[q.correct_index],
                "explication": q.explanation
            })

            st.session_state.current_index += 1
            st.rerun()   # ✅ correction ici

    else:
        st.success(f"Quiz terminé ! Score : {st.session_state.score}/{len(questions)}")

        # Corrigé complet
        with st.expander("Voir le corrigé complet"):
            for ans in st.session_state.answers:
                st.markdown(f"**{ans['theme']}** – {ans['question']}")
                st.write(f"Votre réponse : {ans['choix']}")
                st.write(f"Bonne réponse : {ans['correct']}")
                st.info(ans['explication'])
                st.markdown("---")

        # Sauvegarde des résultats uniquement en mode examen
        if st.session_state.mode == "Examen en cours":
            results = [{
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "score": st.session_state.score,
                "total": len(questions)
            }]
            save_results_to_csv(results)
            st.success("📂 Résultats sauvegardés dans `resultats.csv`")
