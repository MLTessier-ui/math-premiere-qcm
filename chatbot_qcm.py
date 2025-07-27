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
    st.session_state._
