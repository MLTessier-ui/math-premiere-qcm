# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys
import re
import pandas as pd
import os
import matplotlib.pyplot as plt

# Configuration
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")

# Thèmes + automatismes officiels
themes_automatismes = {
    "Calcul numérique et algébrique": "Règles de calcul, priorités, puissances, factorisations simples, développements simples, identités remarquables.",
    "Proportions et pourcentages": "Proportionnalité, échelles, pourcentages simples et successifs, variations relatives.",
    "Évolutions et variations": "Augmentations, diminutions, taux d’évolution, variations composées.",
    "Fonctions et représentations": "Lecture graphique, valeurs, antécédents, variations, extrema.",
    "Statistiques": "Tableaux, diagrammes, moyennes, médianes, étendues.",
    "Probabilités": "Expériences aléatoires simples, calculs de probabilités, événements contraires."
}

# Sélection utilisateur
chapitres = list(themes_automatismes.keys())
chapitre_choisi = st.selectbox("📘 Chapitre :", ["--- Choisir un chapitre ---"] + chapitres)
nb_questions = st.slider("Nombre de questions", 5, 20, 10)
difficulte = st.selectbox("Niveau de difficulté", ["Facile", "Moyen", "Difficile"])
mode_examen = st.checkbox("Mode examen (corrigé à la fin)")

# Clé API
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncod
