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

def gen_puissances(difficulty="Moyen"):
    base = random.choice([2,3,5])
    exp1, exp2 = random.randint(2,4), random.randint(2,4)
    stem = f"Calculer : {base}^{exp1} × {base}^{exp2}"
    correct = base**(exp1+exp2)
    wrong = [base**(exp1*exp2), base**(exp1-exp2), (base**exp1)+(base**exp2)]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"On additionne les exposants : {base}^{exp1} × {base}^{exp2} = {base}^{exp1+exp2} = {correct}."
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

def gen_identite_remarquable(difficulty="Moyen"):
    a = random.randint(1, 5)
    choice = random.choice(["(a+b)²", "(a-b)²", "(a+b)(a-b)"])
    if choice == "(a+b)²":
        stem = f"Développer : ({a}+x)²"
        correct = f"x² + {2*a}x + {a*a}"
        wrong = [f"x² + {a}x + {a*a}", f"x² + {2*a}x - {a*a}", f"x² - {2*a}x + {a*a}"]
        explanation = f"(a+b)² = a² + 2ab + b². Ici, ({a}+x)² = x² + 2×{a}×x + {a*a}."
    elif choice == "(a-b)²":
        stem = f"Développer : (x-{a})²"
        correct = f"x² - {2*a}x + {a*a}"
        wrong = [f"x² + {2*a}x + {a*a}", f"x² - {a}x + {a*a}", f"x² + {a}x - {a*a}"]
        explanation = f"(a-b)² = a² - 2ab + b². Ici, (x-{a})² = x² - 2×{a}×x + {a*a}."
    else:
        stem = f"Développer : (x+{a})(x-{a})"
        correct = f"x² - {a*a}"
        wrong = [f"x² + {a*a}", f"x² - {2*a}x + {a*a}", f"x² + {2*a}x + {a*a}"]
        explanation = f"(a+b)(a-b) = a² - b². Ici, (x+{a})(x-{a}) = x² - {a*a}."
    choices = [correct] + wrong
    random.shuffle(choices)
    correct_index = choices.index(correct)
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

def gen_stats_dispersion(difficulty="Moyen"):
    data = [random.randint(1,10) for _ in range(5)]
    stem = f"On a relevé les valeurs suivantes : {data}. Quelle est l'étendue ?"
    correct = max(data) - min(data)
    wrong = [max(data), min(data), sum(data)]
    choices = [str(correct)] + [str(w) for w in wrong]
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    explanation = f"L'étendue est max - min = {max(data)} - {min(data)} = {correct}."
    return Question("Statistiques", stem, choices, correct_index, explanation, difficulty)

# ===============================
# Dictionnaire de générateurs
# ===============================

THEME_GENERATORS = {
    "Numérique": [gen_fraction_addition, gen_percentage_increase, gen_puissances],
    "Fonctions": [gen_fonction_image, gen_fonction_slope, gen_identite_remarquable],
    "Statistiques": [gen_stats_mean, gen_stats_median, gen_stats_dispersion],
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
    """Génère toujours 12 questions en mode examen"""
    if seed is not None:
        random.seed(seed)
    qs = []
    themes = list(THEME_GENERATORS.keys())
    for _ in range(12):
        t = random.choice(themes)
        qs.append(generate_question(t, "Moyen"))
    random.shuffle(qs)
    return qs

# ===============================
# Compatibilité avec app.py
# ===============================
THEMES = list(THEME_GENERATORS.keys())
