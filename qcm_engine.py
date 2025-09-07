# -*- coding: utf-8 -*-
import random
from enum import Enum
from fractions import Fraction

# ===============================
# Classe et constantes
# ===============================

class Difficulty(str, Enum):
    Facile = "Facile"
    Moyen = "Moyen"
    Difficile = "Difficile"

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

# ===============================
# Générateurs : Numérique
# ===============================

def gen_fraction_addition(difficulty="Moyen"):
    a, b = random.randint(1, 5), random.randint(2, 6)
    c, d = random.randint(1, 5), random.randint(2, 6)
    stem = f"Calculer : {a}/{b} + {c}/{d}"
    correct = Fraction(a, b) + Fraction(c, d)
    wrong = [
        Fraction(a+c, b+d),
        Fraction(a, b) + Fraction(c, b),
        Fraction(a*d + c*b, b*d+1),
    ]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"On réduit au même dénominateur : {a}/{b} + {c}/{d} = {correct}."
    return Question("Numérique", stem, choices, correct_index, explanation, difficulty)

def gen_percentage_increase(difficulty="Moyen"):
    price = random.randint(20, 100)
    percent = random.choice([10, 20, 50])
    stem = f"Un article coûte {price} €. Après une augmentation de {percent} %, quel est le nouveau prix ?"
    correct = round(price * (1 + percent/100), 2)
    wrong = [price + percent, price * (percent/100), price - percent]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"Une augmentation de {percent}% correspond à multiplier par (1+{percent}/100)."
    return Question("Numérique", stem, choices, correct_index, explanation, difficulty)

# ===============================
# Générateurs : Fonctions
# ===============================

def gen_fonction_image(difficulty="Moyen"):
    a, b, x0 = random.choice([1,2,3]), random.randint(-3,3), random.randint(-2,2)
    stem = f"Soit f(x) = {a}x + {b}. Quelle est l'image de {x0} par f ?"
    correct = a*x0 + b
    wrong = [a+b, a-x0, b-x0]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"On calcule f({x0}) = {a}×{x0}+{b} = {correct}."
    return Question("Fonctions", stem, choices, correct_index, explanation, difficulty)

def gen_fonction_slope(difficulty="Moyen"):
    x1, x2 = -2, 2
    a = random.choice([1, -1, 2])
    b = random.randint(-3, 3)
    y1, y2 = a*x1+b, a*x2+b
    stem = f"On considère une droite passant par A({x1},{y1}) et B({x2},{y2}). Quel est son coefficient directeur ?"
    correct = (y2-y1)/(x2-x1)
    wrong = [y2-y1, (x2-x1)/(y2-y1), a+b]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"Le coefficient directeur est (y2-y1)/(x2-x1) = ({y2}-{y1})/({x2}-{x1}) = {correct}."
    return Question("Fonctions", stem, choices, correct_index, explanation, difficulty)

# ===============================
# Dictionnaire de générateurs
# ===============================

THEME_GENERATORS = {
    "Numérique": [gen_fraction_addition, gen_percentage_increase],
    "Fonctions": [gen_fonction_image, gen_fonction_slope],
    # à compléter avec Statistiques, Second degré, Dérivation, Géométrie
}

# ===============================
# Choix aléatoire d’une question
# ===============================

def generate_question(theme, difficulty="Moyen"):
    if theme in THEME_GENERATORS:
        generator = random.choice(THEME_GENERATORS[theme])
        return generator(difficulty)
    else:
        # fallback simple
        return gen_fraction_addition(difficulty)

# ===============================
# Fonctions de compatibilité
# ===============================

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

def generate_set(theme, difficulty, n, seed=None):
    if seed is not None:
        random.seed(seed)
    qs = []
    for _ in range(n):
        if theme == "Auto":
            t = random.choice(list(THEME_GENERATORS.keys()))
        else:
            t = theme
        qs.append(generate_question(t, difficulty))
    return qs

def generate_exam(seed=None):
    if seed is not None:
        random.seed(seed)
    qs = []
    for t in THEME_GENERATORS.keys():
        for _ in range(2):  # 2 questions par thème
            qs.append(generate_question(t, "Moyen"))
    random.shuffle(qs)
    return qs[:12]
