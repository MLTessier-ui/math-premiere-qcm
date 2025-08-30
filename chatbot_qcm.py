# -*- coding: utf-8 -*-
import random, os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from qcm_engine import THEMES, Difficulty, generate_set, generate_exam, to_dict, validate

st.set_page_config(page_title="QCM Première - Entraînement Bac", layout="wide")
st.title("QCM Première — Entraînement Bac 2026")

# Sidebar
with st.sidebar:
    st.header("Paramètres")
    user_id = st.text_input("Identifiant élève", help="Ex: prenom.nom ou numéro")
    theme = st.selectbox("Thème", options=["Auto"] + THEMES)
    difficulty = st.selectbox("Difficulté", options=Difficulty, index=1)
    n_questions = st.slider("Nombre de questions", 5, 10, 5)
    exam_mode = st.toggle("Mode examen (12 questions)")
    start_quiz = st.button("Commencer l’entraînement")

@st.cache_data(show_spinner=False)
def _generate_cached(theme, difficulty, n, seed, exam):
    if exam:
        return [to_dict(q) for q in generate_exam(seed)]
    else:
        return [to_dict(q) for q in generate_set(theme, difficulty, n, seed)]

def _plot(qdict):
    if not qdict.get("plot"):
        return
    payload = qdict.get("plot_payload", {})
    plt.figure()
    if payload.get("type") == "affine":
        a, b = payload["a"], payload["b"]
        xs = np.linspace(-6, 6, 100)
        ys = a * xs + b
        plt.axhline(0, color="black", linewidth=0.5)
        plt.axvline(0, color="black", linewidth=0.5)
        plt.plot(xs, ys)
        for x0, y0 in payload.get("points", []):
            plt.scatter([x0], [y0], color="red")
        st.pyplot(plt.gcf(), clear_figure=True)
    elif payload.get("type") == "stats_hist":
        data = payload["data"]
        plt.hist(data, bins="auto")
        plt.title("Histogramme")
        st.pyplot(plt.gcf(), clear_figure=True)

if start_quiz or exam_mode:
    seed = int(hash(user_id) % 10_000) if user_id else random.randint(0, 10_000)
    qdicts = _generate_cached(theme, difficulty, n_questions, seed, exam_mode)

    st.subheader("Questions")
    if "validated" not in st.session_state:
        st.session_state["validated"] = {}

    if "scores" not in st.session_state:
        st.session_state["scores"] = {}

    for i, q in enumerate(qdicts, start=1):
        ok, issues = validate(type("Q", (), q))
        choice_key = f"choice_{i}"
        validate_key = f"validate_{i}"

        with st.expander(f"Q{i}. {q['theme']} — {q['difficulty']}", expanded=True):
            st.markdown(f"**Énoncé :** {q['stem']}")
            _plot(q)

            # Choix de réponse
            st.radio(
                "Votre réponse :",
                options=list(range(4)),
                format_func=lambda idx: f"{['A','B','C','D'][idx]}. {q['choices'][idx]}",
                key=choice_key
            )

            # Bouton Valider
            if st.button("Valider ma réponse", key=validate_key):
                st.session_state["validated"][i] = True
                choice = st.session_state[choice_key]
                is_correct = int(choice == q["correct_index"])
                st.session_state["scores"][i] = is_correct

            # Affichage de la correction SEULEMENT si validée
            if st.session_state["validated"].get(i, False):
                choice = st.session_state[choice_key]
                st.caption(f"Bonne réponse : {['A','B','C','D'][q['correct_index']]}")
                st.write(f"**Explication :** {q['explanation']}")
                if not ok:
                    st.warning("Validation automatique : " + "; ".join(issues))

    # Score
    if st.session_state["scores"]:
        score = sum(st.session_state["scores"].values())
        total = len(st.session_state["scores"])
        st.success(f"Score : {score}/{total} ({round(100*score/total)}%)")
