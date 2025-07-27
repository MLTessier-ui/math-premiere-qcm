import streamlit as st
import openai
import json

# Clé API OpenAI
# openai.api_key = "TON_API_KEY"
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Liste de chapitres possibles
chapitres = [
    "Fonctions",
    "Calcul littéral",
    "Statistiques",
    "Probabilités",
    "Géométrie",
    "Nombres et calculs",
    "Grandeurs et mesures"
]

st.title("🤖 Chatbot QCM – Maths Première (Spécifiques)")
st.markdown("Choisis un chapitre pour générer un QCM :")

# Choix du chapitre
chapitre_choisi = st.selectbox("Chapitre", chapitres)

if st.button("Générer une question"):
    with st.spinner("Génération de la question..."):
        prompt = f"""
Tu es un professeur de mathématiques. Crée une question de QCM conforme au programme de mathématiques spécifiques de Première (enseignement commun). Chapitre : {chapitre_choisi}.

Présente la question dans ce format JSON :
{{
  "chapitre": "{chapitre_choisi}",
  "question": "...",
  "propositions": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "bonne_reponse": "A",
  "explication": "..."
}}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        # Afficher et traiter le résultat
        try:
            qcm_json = json.loads(response['choices'][0]['message']['content'])

            st.subheader("📘 Question")
            st.write(qcm_json["question"])

            # Affichage des options
            choix = st.radio("Réponses :", qcm_json["propositions"])
            if st.button("Valider ma réponse"):
                if choix.startswith(qcm_json["bonne_reponse"]):
                    st.success("✅ Bonne réponse !")
                else:
                    st.error(f"❌ Mauvaise réponse. La bonne était : {qcm_json['bonne_reponse']}")
                st.info("🔍 Explication : " + qcm_json["explication"])

        except Exception as e:
            st.error("Erreur de génération ou de format. Détails : " + str(e))
