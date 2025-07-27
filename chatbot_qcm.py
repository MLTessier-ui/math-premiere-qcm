# -*- coding: utf-8 -*-

import json
import openai
import streamlit
import sys



key = st.secrets["OPENAI_API_KEY"]

try:
    key.encode("ascii")
except UnicodeEncodeError:
    st.error("❌ La clé API contient un caractère accentué ou invisible. Veuillez en recréer une.")
    sys.exit()

# Initialisation du client OpenAI avec la clé depuis les secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Liste des chapitres du programme spécifique de Première
chapitres = [
    "Fonctions",
    "Calcul littéral",
    "Statistiques",
    "Probabilités",
    "Géométrie",
    "Nombres et calculs",
    "Grandeurs et mesures"
]

st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")
st.markdown("Choisis un chapitre pour générer une question de QCM adaptée au programme.")

# Choix de chapitre
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

if st.button("🎲 Générer une question"):
    with st.spinner("GPT prépare une question adaptée..."):
        chapitre_choisi = chapitre_choisi or "Fonctions"

        prompt_data = {
            "instructions": f"""Tu es un professeur de mathématiques. Génère une question de type QCM pour le niveau Première - Mathématiques spécifiques.

- Le thème est : {theme}
- Rédige une question claire.
- Donne 4 propositions (A, B, C, D), dont une seule est correcte.
- Mélange aléatoirement l'ordre des propositions.
- Indique la lettre de la bonne réponse.
- Donne une explication claire et pédagogique pour justifier la bonne réponse, même si l'élève s’est trompé.

Réponds dans ce format JSON structuré :""",
            "json_format": {
                "question": "...",
                "options": {
                    "A": "...",
                    "B": "...",
                    "C": "...",
                    "D": "..."
                },
                "correct_answer": "B",
                "explanation": "..."
            }
        }

        prompt = prompt_data["instructions"] + "\n\n" + json.dumps(prompt_data["json_format"], indent=2)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            qcm = json.loads(content)

            # Affichage dans l'app
            st.markdown(f"### ❓ Question :\n{qcm['question']}")
            for key, value in qcm["options"].items():
                st.markdown(f"**{key}** : {value}")

            if "correct_answer" in qcm:
                st.success(f"✅ Bonne réponse : {qcm['correct_answer']}")
            if "explanation" in qcm:
                st.info(f"ℹ️ Explication : {qcm['explanation']}")

        except Exception as e:
            st.error(f"❌ Erreur lors de l’appel à l’API : {str(e)}")
