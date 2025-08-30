# -*- coding: utf-8 -*-
import random
from enum import Enum
import numpy as np

# ===============================
# Thèmes du programme officiel
# ===============================
THEMES = [
    "Suites arithmétiques et géométriques",
    "Fonctions et représentations graphiques",
    "Statistiques et probabilités",
    "Second degré",
    "Dérivation",
    "Géométrie analytique"
]

class Difficulty(str, Enum):
    Facile = "Facile"
    Moyen = "Moyen"
    Difficile = "Difficile"

# ===============================
# Classe Question
# ===============================
class Question:
    def __init__(self, theme, stem, choices, correct_index, explanation,
                 difficulty="Moyen", plot=False, plot_payload=None):
        self.theme = theme
        self.stem = stem
        self.choices = choices
        self.correct_index = correct_index
        self.explanation = explanation
        self.difficulty = difficulty
        self.plot = plot
        self.plot_payload = plot_payload or {}

def to_dict(q: Question):
    return {
        "theme": q.theme,
        "stem": q.stem,
        "choices": q.choices,
        "correct_index": q.correct_index,
        "explanation": q.explanation,
        "difficulty": q.difficulty,
        "plot": q.plot,
        "plot_payload": q.plot_payload,
    }

# ===============================
# Générateurs par thème
# ===============================
def gen_suite_geo(difficulty="Moyen"):
    """Suites géométriques avec raisons simples"""
    u0 = random.choice([1, 2, 3, 5])
    raison = random.choice([2, 3, 0.5, -2])  # entiers ou fraction simple
    n = random.randint(3, 5)
    stem = f"Soit (u_n) une suite géométrique de premier terme u0 = {u0} et de raison q = {raison}. Calculer u_{n}."
    correct = u0 * (raison ** n)
    # Distracteurs
    wrong = [
        u0 + n * raison,        # confondu avec arithmétique
        u0 * raison * n,        # erreur classique
        raison ** n             # oubli du u0
    ]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = (
        f"Une suite géométrique vérifie u_n = u0 × q^n. "
        f"Ici, u0 = {u0}, q = {raison}, donc u_{n} = {u0} × {raison}^{n} = {correct}."
    )
    return Question("Suites arithmétiques et géométriques", stem, [str(c) for c in choices],
                    correct_index, explanation, difficulty)

def gen_fonction_affine(difficulty="Moyen"):
    """Fonctions affines données par deux points"""
    a = random.choice([1, -1, 2, -2, 0.5])
    b = random.randint(-3, 3)
    # On choisit deux points distincts
    x1, x2 = -2, 1
    y1, y2 = a * x1 + b, a * x2 + b
    stem = f"On considère une fonction affine f. On sait que f({x1}) = {y1} et f({x2}) = {y2}. Quelle est l'expression de f(x) ?"
    correct = f"f(x) = {a}x + {b}"
    wrong = [
        f"f(x) = {a}x - {b}",
        f"f(x) = {-a}x + {b}",
        f"f(x) = {a}x"
    ]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = (
        f"Une fonction affine est déterminée par deux points. "
        f"La pente est (y2-y1)/(x2-x1) = ({y2}-{y1})/({x2}-{x1}) = {a}. "
        f"Puis on trouve b en utilisant f({x1}) = {y1}. "
        f"On obtient f(x) = {a}x + {b}."
    )
    return Question("Fonctions et représentations graphiques", stem, choices,
                    correct_index, explanation, difficulty)

def gen_stats(difficulty="Moyen"):
    """Statistiques sous forme de série de valeurs"""
    notes = [random.choice([8, 9, 10, 11, 12, 13, 14, 15]) for _ in range(10)]
    stem = f"On a relevé les notes suivantes sur 10 élèves : {notes}. Quelle est la moyenne ?"
    correct = round(sum(notes)/len(notes), 2)
    wrong = [
        max(notes),
        min(notes),
        round((max(notes)+min(notes))/2, 2)
    ]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = (
        f"La moyenne est la somme des valeurs divisée par l'effectif. "
        f"Ici somme = {sum(notes)}, effectif = {len(notes)}, "
        f"moyenne = {sum(notes)}/{len(notes)} = {correct}."
    )
    return Question("Statistiques et probabilités", stem, [str(c) for c in choices],
                    correct_index, explanation, difficulty)

def gen_second_deg(difficulty="Moyen"):
    a = random.choice([1, -1, 2])
    b = random.randint(-4, 4)
    c = random.randint(-3, 3)
    stem = f"On considère f(x) = {a}x² + {b}x + {c}. Quel est le discriminant Δ ?"
    delta = b*b - 4*a*c
    wrong = [b*b + 4*a*c, (b-2*a*c), b*b]
    choices = [delta] + wrong
    random.shuffle(choices)
    correct_index = choices.index(delta)
    explanation = (
        f"Δ = b² - 4ac = {b}² - 4×{a}×{c} = {delta}."
    )
    return Question("Second degré", stem, [str(c) for c in choices],
                    correct_index, explanation, difficulty)

def gen_derivation(difficulty="Moyen"):
    coeff = random.choice([1, 2, 3])
    exp = random.choice([2, 3, 4])
    stem = f"Quelle est la dérivée de f(x) = {coeff}x^{exp} ?"
    correct = f"{coeff*exp}x^{exp-1}"
    wrong = [f"{coeff}x^{exp-1}", f"{coeff*exp}x^{exp}", f"{exp}x^{coeff-1}"]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = (
        f"On applique la formule (x^n)' = n x^(n-1). "
        f"Ici, ({coeff}x^{exp})' = {coeff}×{exp}×x^{exp-1} = {correct}."
    )
    return Question("Dérivation", stem, choices,
                    correct_index, explanation, difficulty)

def gen_geo(difficulty="Moyen"):
    xA, yA = random.randint(-3, 3), random.randint(-3, 3)
    xB, yB = random.randint(-3, 3), random.randint(-3, 3)
    stem = f"Dans un repère, A({xA},{yA}) et B({xB},{yB}). Quelle est la distance AB ?"
    correct = round(((xB-xA)**2 + (yB-yA)**2)**0.5, 2)
    wrong = [abs(xB-xA)+abs(yB-yA), (xB-xA)**2 + (yB-yA)**2, abs(xB-xA-yB+yA)]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = (
        f"La distance AB = √((xB-xA)² + (yB-yA)²) = √(({xB}-{xA})² + ({yB}-{yA})²) = {correct}."
    )
    return Question("Géométrie analytique", stem, [str(c) for c in choices],
                    correct_index, explanation, difficulty)

# ===============================
# Générateurs globaux
# ===============================
def generate_question(theme, difficulty="Moyen"):
    if theme == "Suites arithmétiques et géométriques":
        return gen_suite_geo(difficulty)
    elif theme == "Fonctions et représentations graphiques":
        return gen_fonction_affine(difficulty)
    elif theme == "Statistiques et probabilités":
        return gen_stats(difficulty)
    elif theme == "Second degré":
        return gen_second_deg(difficulty)
    elif theme == "Dérivation":
        return gen_derivation(difficulty)
    elif theme == "Géométrie analytique":
        return gen_geo(difficulty)
    else:
        return gen_stats(difficulty)

def generate_set(theme, difficulty, n, seed=None):
    if seed is not None:
        random.seed(seed)
    qs = []
    for _ in range(n):
        t = theme if theme != "Auto" else random.choice(THEMES)
        q = generate_question(t, difficulty)
        qs.append(q)
    return qs

def generate_exam(seed=None):
    if seed is not None:
        random.seed(seed)
    qs = []
    chosen = random.sample(THEMES, min(len(THEMES), 6))
    for t in chosen:
        for _ in range(2):  # 2 questions par thème
            qs.append(generate_question(t, "Moyen"))
    return qs
