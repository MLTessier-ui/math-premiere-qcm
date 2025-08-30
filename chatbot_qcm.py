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

# ===============================
# Sidebar
# ===============================
with st.sidebar:
    st.header("Paramètres")
    user_id = st.text_input("Identifiant élève", help="Ex: prenom.nom ou numéro")
    theme = st.selectbox("Thème", options=["Auto"] + THEMES)
    difficulty = st.selectbox("Difficulté", options=Difficulty, index=1)
    n_questions = st.slider("Nombre de questions", 5, 10, 5)
    exam_mode = st.toggle("Mode examen (12 questions)")
    start_quiz = st.button("Commencer l’entraînement")

# ===============================
# Cache génération
# ===============================
@st.cache_data(show_spinner=False)
def _generate_cached(theme, difficulty, n, seed, exam):
    if exam:
        return [to_dict(q) for q in generate_exam(seed)]
    else:
        return [to_dict(q) for q in generate_set(theme, difficulty, n, seed)]

# ===============================
# Plot helper
# ===============================
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

# ===============================
# Sauvegarde résultats (exam only)
# ===============================
def _save_results(user_id: str, records: list):
    if not user_id or not records:
        return
    os.makedirs("results", exist_ok=True)
    path = os.path.join("results", f"{user_id}.csv")
    df_new = pd.DataFrame(records)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = pd.concat([df, df_ne_]()
