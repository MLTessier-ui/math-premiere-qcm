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
# Choix du mode
# ===============================
mode = st.radio("Choisissez le mode :", ["Entraînement", "Examen (12 questions)"])

with st.sidebar:
    st.header("Paramètres")
    user_id = st.text_input("Identifiant élève", help="Ex: prenom.nom ou numéro")
    if mode == "Entraînement":
        theme = st.selectbox("Thème", options=["Auto"] + THEMES)
        difficulty = st.selectbox("Difficulté", options=Difficulty, index=1)
        n_questions = st.slider("Nombre de questions", 5, 10, 5)
    else:
        theme, difficulty, n_questions = None, None, 12

    start_quiz = st.button("Commencer")

# ===============================
# Helpers
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
        st.pyplot(plt.gcf(), clear_figure=True)
    elif payload.get("type") == "stats_hist":
        data = payload["data"]
        plt.hist(data, bins="auto")
        plt.title("Histogramme")
        st.pyplot(plt.gcf(), clear_figure=True)

def _save_results(user_id: str, records: list):
    if not user_id or not records:
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

# ===============================
# Génération quiz
# ===============================
if start_quiz:
    if "questions" not in st.session_state or st.session_state.get("last_mode") != mode:
        seed = int(hash(user_id) % 10_000) if user_id else random.randint(0, 10_000)
        if mode == "Examen (12 questions)":
            qdicts = [to_dict(q) for q in generate_exam(seed)]
        else:
            qdicts = [to_dict(q) for q in generate_set(theme, difficulty, n_questions, seed)]
        st.session_state["questions"] = qdicts
        st.session_state["validated"] = {}
        st.session_state["answers"] = {}
        st.session_state["scores"] = {}
        st.session_state["last_mode"] = mode

    qdicts = st.session_state["questions"]

    # ===============================
    # Affichage questions
    # ===============================
    st.subheader("Questions")

    for i, q in enumerate(qdicts, start=1):
        validated = st.session_state["validated"].get(i, False)

        with st.expander(f"Q{i}. {q['theme']} — {q['difficulty']}", expanded=True):
            st.markdown(f"**Énoncé :** {q['stem']}")
            _plot(q)

            choice = st.radio(
                "Votre réponse :",
                options=list(range(4)),
                format_func=lambda idx: f"{['A','B','C','D'][idx]}. {q['choices'][idx]}",
                index=st.session_state["answers"].get(i, 0) if i in st.session_state["answers"] else 0,
                key=f"radio_{i}"
            )

            if st.button("Valider ma réponse", key=f"btn_{i}"):
                st.session_state["validated"][i] = True
                st.session_state["answers"][i] = choice
                st.session_state["scores"][i] = int(choice == q["correct_index"])

            if validated:
                user_choice = st.session_state["answers"][i]
                st.caption(f"Bonne réponse : {['A','B','C','D'][q['correct_index']]}")
                st.write(f"**Explication :** {q['explanation']}")
                if user_choice == q["correct_index"]:
                    st.success("✅ Correct")
                else:
                    st.error("❌ Incorrect")

    # ===============================
    # Score courant
    # ===============================
    if st.session_state["scores"]:
        score = sum(st.session_state["scores"].values())
        total = len(st.session_state["scores"])
        st.success(f"Score : {score}/{total} ({round(100*score/total)}%)")

    # ===============================
    # Corrigé final (examen)
    # ===============================
    if mode == "Examen (12 questions)" and len(st.session_state["validated"]) == len(qdicts):
        st.subheader("📘 Corrigé complet")
        records = []
        for i, q in enumerate(qdicts, start=1):
            st.markdown(f"**Q{i}. {q['stem']}**")
            st.caption(f"Bonne réponse : {q['choices'][q['correct_index']]}")
            st.write(q['explanation'])
            records.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "user_id": user_id,
                "question_idx": i,
                "theme": q["theme"],
                "difficulty": q["difficulty"],
                "is_correct": st.session_state['scores'].get(i, 0)
            })

        path = _save_results(user_id, records)
        if path:
            st.caption(f"Résultats sauvegardés dans : `{path}`")

    # ===============================
    # Bouton "Nouvel essai"
    # ===============================
    if st.button("🔄 Nouvel essai"):
        for key in ["questions", "validated", "answers", "scores", "last_mode"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
