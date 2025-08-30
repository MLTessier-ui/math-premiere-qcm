# -*- coding: utf-8 -*-
import random
import streamlit as st
from qcm_engine import generate_set, to_dict

st.set_page_config(page_title="QCM Debug", layout="wide")
st.title("QCM Debug — 1 question")

# ===============================
# Générer une seule question
# ===============================
seed = 123
q = to_dict(generate_set("Fonctions et représentations", "Facile", 1, seed)[0])

i = 1  # index unique de la question

if "validated" not in st.session_state:
    st.session_state["validated"] = {}
if "answers" not in st.session_state:
    st.session_state["answers"] = {}

st.subheader(f"Q{i}. {q['theme']} — {q['difficulty']}")
st.markdown(f"**Énoncé :** {q['stem']}")

# afficher options (sans key dans session_state)
choice = st.radio(
    "Votre réponse :",
    options=list(range(4)),
    format_func=lambda idx: f"{['A','B','C','D'][idx]}. {q['choices'][idx]}",
)

# bouton valider
if st.button("Valider ma réponse"):
    st.session_state["validated"][i] = True
    st.session_state["answers"][i] = choice

# correction seulement si validée
if st.session_state["validated"].get(i, False):
    user_choice = st.session_state["answers"][i]
    st.caption(f"Bonne réponse : {['A','B','C','D'][q['correct_index']]}")
    st.write(f"**Explication :** {q['explanation']}")
    if user_choice == q["correct_index"]:
        st.success("✅ Correct")
    else:
        st.error("❌ Incorrect")
