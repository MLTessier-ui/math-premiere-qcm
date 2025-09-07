# -*- coding: utf-8 -*-
import random
from enum import Enum
from fractions import Fraction

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
    """Suites géométriques avec raisons simples (entiers ou fractions)"""
    u0 = random.choice([1, 2, 3, Fraction(1, 2)])
    raison = random.choice([2, 3, Fraction(1, 2), Fraction(3, 4), -2])
    n = random.randint(2, 4)
    stem = f"Soit (u_n) une suite géométrique de premier terme u0 = {u0} et de raison q = {raison}. Donner u_{n}."
    correct = u0 * (raison ** n)
    wrong = [
        u0 + n * raison,        # confondu avec arithmétique
        u0 * raison * n,        # erreur multiplicative
        raison ** n             # oubli du u0
    ]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"Une suite géométrique vérifie u_n = u0 × q^n. Ici, u_{n} = {u0} × {raison}^{n} = {correct}."
    return Question("Suites arithmétiques et géométriques", stem, choices, correct_index, explanation, difficulty)

def gen_fonction_affine(difficulty="Moyen"):
    """Fonctions affines définies par deux points donnés"""
    a = random.choice([1, -1, 2, -2, Fraction(1, 2), Fraction(-1, 2)])
    b = random.randint(-3, 3)
    x1, x2 = -2, 1
    y1, y2 = a * x1 + b, a * x2 + b
    stem = f"On considère une fonction affine f. On sait que f({x1}) = {y1} et f({x2}) = {y2}. Quelle est l'expression de f(x) ?"
    correct = f"f(x) = {a}x + {b}"
    wrong = [f"f(x) = {a}x - {b}", f"f(x) = {-a}x + {b}", f"f(x) = {a}x"]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = (f"La pente est (y2-y1)/(x2-x1) = ({y2}-{y1})/({x2}-{x1}) = {a}. "
                   f"Puis b est trouvé avec f({x1}) = {y1}. Donc f(x) = {a}x + {b}.")
    return Question("Fonctions et représentations graphiques", stem, choices, correct_index, explanation,
                    difficulty, plot=True, plot_payload={"type": "affine", "a": float(a), "b": float(b),
                                                         "points": [(x1, float(y1)), (x2, float(y2))]})

def gen_stats(difficulty="Moyen"):
    """Statistiques sous forme de série de valeurs"""
    notes = [random.choice([8, 9, 10, 11, 12, 13, 14, 15]) for _ in range(10)]
    stem = f"On a relevé les notes suivantes sur 10 élèves : {notes}. Quelle est la moyenne ?"
    correct = round(sum(notes)/len(notes), 2)
    wrong = [max(notes), min(notes), round((max(notes)+min(notes))/2, 2)]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = (f"La moyenne est la somme des valeurs divisée par l'effectif. "
                   f"Ici, somme = {sum(notes)}, effectif = {len(notes)}, moyenne = {correct}.")
    return Question("Statistiques et probabilités", stem, choices, correct_index, explanation, difficulty)

def gen_second_deg(difficulty="Moyen"):
    delta = b*b - 4*a*c
    wrong = [b*b + 4*a*c, b-2*a*c, b*b]
    choices = [str(delta)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(delta))

