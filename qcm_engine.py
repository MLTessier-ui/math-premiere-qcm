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
# Générateurs : Statistiques
# ===============================

def gen_stats_mean(difficulty="Moyen"):
    data = [random.randint(5, 20) for _ in range(6)]
    stem = f"On a relevé les valeurs suivantes : {data}. Quelle est la moyenne ?"
    correct = round(sum(data)/len(data), 2)
    wrong = [max(data), min(data), round((max(data)+min(data))/2, 2)]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"La moyenne = somme ÷ effectif = {sum(data)} ÷ {len(data)} = {correct}."
    return Question("Statistiques", stem, choices, correct_index, explanation, difficulty)

def gen_stats_median(difficulty="Moyen"):
    data = sorted([random.randint(1, 20) for _ in range(7)])
    stem = f"On considère la série : {data}. Quelle est la médiane ?"
    correct = data[len(data)//2]
    wrong = [data[0], data[-1], sum(data)//len(data)]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"La médiane est la valeur centrale quand on range les données dans l'ordre croissant, ici {correct}."
    return Question("Statistiques", stem, choices, correct_index, explanation, difficulty)

# ===============================
# Générateurs : Second degré
# ===============================

def gen_second_deg_discriminant(difficulty="Moyen"):
    a = random.choice([1, -1, 2])
    b = random.randint(-4, 4)
    c = random.randint(-3, 3)
    stem = f"On considère f(x) = {a}x² + {b}x + {c}. Quel est le discriminant Δ ?"
    delta = b*b - 4*a*c
    wrong = [b*b + 4*a*c, b - 2*a*c, b*b]
    choices = [str(delta)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(delta))
    explanation = f"Δ = b² - 4ac = {b}² - 4×{a}×{c} = {delta}."
    return Question("Second degré", stem, choices, correct_index, explanation, difficulty)

def gen_second_deg_root_count(difficulty="Moyen"):
    a = random.choice([1, 2])
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    delta = b*b - 4*a*c
    stem = f"On considère f(x) = {a}x² + {b}x + {c}. Combien de racines réelles possède f ?"
    if delta > 0:
        correct = "Deux racines réelles distinctes"
    elif delta == 0:
        correct = "Une racine réelle double"
    else:
        correct = "Aucune racine réelle"
    wrong = ["Toujours deux racines", "Toujours une seule racine", "Toujours aucune racine"]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = f"On regarde le signe de Δ = {delta}. Δ>0 → 2 racines, Δ=0 → 1 racine double, Δ<0 → pas de racine."
    return Question("Second degré", stem, choices, correct_index, explanation, difficulty)

# ===============================
# Générateurs : Dérivation
# ===============================

def gen_deriv_poly(difficulty="Moyen"):
    coeff = random.choice([1, 2, 3])
    exp = random.choice([2, 3, 4])
    stem = f"Quelle est la dérivée de f(x) = {coeff}x^{exp} ?"
    correct = f"{coeff*exp}x^{exp-1}"
    wrong = [f"{coeff}x^{exp-1}", f"{coeff*exp}x^{exp}", f"{exp}x^{coeff-1}"]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = f"On applique (x^n)' = n×x^(n-1). Ici ({coeff}x^{exp})' = {coeff*exp}x^{exp-1}."
    return Question("Dérivation", stem, choices, correct_index, explanation, difficulty)

def gen_deriv_sum(difficulty="Moyen"):
    a, b = random.randint(1,3), random.randint(1,3)
    stem = f"Quelle est la dérivée de f(x) = {a}x^2 + {b}x ?"
    correct = f"{2*a}x + {b}"
    wrong = [f"{a}x + {b}", f"{a}x^2 + {b}", f"{2*a}x^2 + {b}"]
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
    explanation = f"La dérivée est (a x²)' + (b x)' = 2ax + b. Ici = {2*a}x + {b}."
    return Question("Dérivation", stem, choices, correct_index, explanation, difficulty)

# ===============================
# Générateurs : Géométrie
# ===============================

def gen_geo_distance(difficulty="Moyen"):
    xA, yA = random.randint(-3, 3), random.randint(-3, 3)
    xB, yB = random.randint(-3, 3), random.randint(-3, 3)
    stem = f"Dans un repère, A({xA},{yA}) et B({xB},{yB}). Quelle est la distance AB ?"
    correct = round(((xB-xA)**2 + (yB-yA)**2)**0.5, 2)
    wrong = [abs(xB-xA)+abs(yB-yA), (xB-xA)**2 + (yB-yA)**2, abs(xB-xA-yB+yA)]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"AB = √((xB-xA)² + (yB-yA)²) = {correct}."
    return Question("Géométrie", stem, choices, correct_index, explanation, difficulty)

def gen_geo_midpoint(difficulty="Moyen"):
    xA, yA = random.randint(-5, 5), random.randint(-5, 5)
    xB, yB = random.randint(-5, 5), random.randint(-5, 5)
    stem = f"Dans un repère, A({xA},{yA}) et B({xB},{yB}). Quelles sont les coordonnées du milieu M de [AB] ?"
    correct = ( (xA+xB)/2, (yA+yB)/2 )
    wrong = [(xA+xB, yA+yB), (xB-xA, yB-yA), ( (xA+xB)/2, (yB-yA)/2 )]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"M = ((xA+xB)/2 , (yA+yB)/2) = {correct}."
    return Question("Géométrie", stem, choices, correct_index, explanation, difficulty)

# ===============================
# Dictionnaire de générateurs
# ===============================

THEME_GENERATORS = {
    "Numérique": [gen_fraction_addition, gen_percentage_increase],
    "Fonctions": [gen_fonction_image, gen_fonction_slope],
    "Statistiques": [gen_stats_mean, gen_stats_median],
    "Second degré": [gen_second_deg_discriminant, gen_second_deg_root_count],
    "Dérivation": [gen_deriv_poly, gen_deriv_sum],
    "Géométrie": [gen_geo_distance, gen_geo_midpoint],
}

# ===============================
# Choix aléatoire d’une question
# ===============================

def generate_question(theme, difficulty="Moyen"):
    if theme in THEME_GENERATORS:
        generator = random.choice(THEME_GENERATORS[theme])
        return generator(difficulty)
    else:
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
        for _ in range(2):
            qs.append(generate_question(t, "Moyen"))
    random.shuffle(qs)
    return qs[:12]

# ===============================
# Compatibilité avec app.py
# ===============================
THEMES = list(THEME_GENERATORS.keys())
