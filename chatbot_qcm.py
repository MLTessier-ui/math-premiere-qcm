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
    "Probabilités": "Expériences aléatoires simples, calculs de probabilités, événements co
