# -*- coding: utf-8 -*-
import json, random, re, os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from qcm_engine import THEMES, Difficulty, generate_set, generate_exam, to_dict, validate

# Configuration de la page
st.set_page_config(page_title="QCM Première - Entraînement Bac", layout="wide")
st.title("QCM Première — Entraînement Bac 2026")

# --------- Sidebar: paramètres ----------
with st.sidebar:
    st.header("Paramètres")
    user_id = st.text_input("Identifiant élève", help="Ex: prenom.nom ou numéro")
    seed_base = st.number_input("Graine aléatoire (reproductible)", value=42, step=1)
    theme = st.selectbox(
        "Thème", 
        options=["Auto"] + THEMES, 
        help="Choisissez un thème officiel du BO ou 'Auto' pour tirage aléatoire."
    )
    difficulty = st.selectbox(
        "Difficulté", 
        options=Difficulty, 
        index=1, 
        help="Facile, Moyen ou Difficile."
    )
    n_questions = st.slider("Nombre de questions", 3, 30, 8, help="Nombre de questions pour l'entraînement.")
    exam_mode = st.toggle("Mode examen (12 questions, couvrant tous les thèmes)")
    use_llm = st.toggle(
        "Reformulation LLM (optionnel)", 
        value=False, 
        help="Pour paraphraser l’énoncé/explication, sans toucher aux corrections."
    )

# --------- Cache génération ----------
@st.cache_data(show_spinner=False)
def _generate_cached(theme, difficulty, n, seed, exam):
    if exam:
        return [to_dict(q) for q in generate_exam(seed)]
    else:
        return [to_dict(q) for q in generate_set(theme, difficulty, n, seed)]

# --------- Fonctions utilitaires ----------
def _plot(qdict):
    """Affiche le graphique associé à une question, si nécessaire."""
    if not qdict.get("plot"): 
        return
    payload = qdict.get("plot_payload", {})
    plt.figure()
    t = payload.get("type")

    if t == "affine":
        a, b = payload["a"], payload["b"]
        xs = np.linspace(-6, 6, 100)
        ys = a*xs + b
        plt.plot(xs, ys)
        for x0, y0 in payload.get("points", []):
            plt.scatter([x0], [y0])
        plt.title(f"f(x) = {a}x + {b}")
        st.pyplot(plt.gcf(), clear_figure=True)

    elif t == "stats_hist":
        data = payload["data"]
        plt.hist(data, bins="auto")
        plt.title("Histogramme de la série statistique")
        st.pyplot(plt.gcf(), clear_figure=True)

def _save_results(user_id: str, records: list):
    """Sauvegarde les résultats dans un fichier CSV par élève."""
    if not user_id: 
        return
    os.makedirs("results", exist_ok=True)
    path = os.path.join("results", f"{user_id}.csv")
    df_new = pd.DataFrame(records)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(path, index=False)
    return path

# --------- Génération des QCM ----------
seed = int(seed_base + (hash(user_id) % 10_000) if user_id else seed_base)
qdicts = _generate_cached(theme, difficulty, n_questions, seed, exam_mode)

if use_llm:
    st.info("LLM activé : reformulation possible (non montrée ici pour concision).")
    # ⚠️ Ici tu peux brancher une paraphrase LLM si tu veux,
    # mais ne jamais toucher à correct_index / choices / explication de fond.

st.subheader("Questions")
answers = []
records = []
for i, q in enumerate(qdicts, start=1):
    ok, issues = validate(type("Q", (), q))  # validation rapide
    with st.expander(f"Q{i}. {q['theme']} — {q['difficulty']}", expanded=True):
        st.markdown(f"**Énoncé :** {q['stem']}")
        _plot(q)
        choice = st.radio(
            "Votre réponse :", 
            options=list(range(4)),
            format_func=lambda idx: f"{['A','B','C','D'][idx]}. {q['choices'][idx]}",
            key=f"q_{i}"
        )
        is_correct = int(choice == q["correct_index"])
        st.caption(f"Bonne réponse : {['A','B','C','D'][q['correct_index']]}")
        st.write(f"**Explication :** {q['explanation']}")
        if not ok:
            st.warning("Validation automatique : " + "; ".join(issues))
    answers.append(is_correct)
    records.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_id": user_id,
        "seed": seed,
        "question_idx": i,
        "theme": q["theme"],
        "difficulty": q["difficulty"],
        "is_correct": is_correct
    })

# --------- Score final ----------
score = int(sum(answers))
total = len(answers)
st.success(f"Score : {score}/{total} ({round(100*score/total)}%)")

path = _save_results(user_id, records)
if path:
    st.caption(f"Résultats sauvegardés dans : `{path}`")

# --------- Progression ----------
st.subheader("Progression (par élève)")
if user_id and path and os.path.exists(path):
    df = pd.read_csv(path)
    col1, col2 = st.columns(2)
    with col1:
        by_theme = df.groupby("theme")["is_correct"].mean().reset_index()
        st.dataframe(by_theme.rename(columns={"is_correct":"taux de réussite"}))
    with col2:
        by_time = df.groupby("timestamp")["is_correct"].mean().reset_index()
        if len(by_time) >= 2:
            plt.figure()
            plt.plot(by_time["timestamp"], 100*by_time["is_correct"])
            plt.xticks(rotation=45, ha="right")
            plt.ylabel("Réussite (%)")
            plt.title("Évolution du score")
            st.pyplot(plt.gcf(), clear_figure=True)

