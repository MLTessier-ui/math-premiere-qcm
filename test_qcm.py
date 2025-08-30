# -*- coding: utf-8 -*-
"""
Tests unitaires pour le générateur de QCM (qcm_engine.py).
À exécuter avec :  pytest test_qcm.py
"""

import pytest
import random
from qcm_engine import THEMES, Difficulty, generate_set, generate_exam, validate, _norm

# ============================
# Helpers
# ============================

def _check_question(q):
    """Vérifie les contraintes de base d'une question."""
    ok, issues = validate(q)
    assert ok, f"Validation échouée : {issues}"
    assert len(q.choices) == 4, "Chaque question doit avoir 4 choix"
    assert 0 <= q.correct_index < 4, "Index de la bonne réponse incorrect"
    assert q.explanation and len(q.explanation) > 5, "Explication manquante"
    # Vérifier unicité des choix
    normed = [_norm(c) for c in q.choices]
    assert len(normed) == len(set(normed)), "Doublons dans les choix"
    return True

# ============================
# Tests
# ============================

@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("difficulty", Difficulty)
def test_generate_set(theme, difficulty):
    """Vérifie qu'un set de questions est valide pour chaque thème/difficulté."""
    qs = generate_set(theme, difficulty, 5, seed=42)
    assert len(qs) == 5
    seen_stems = set()
    for q in qs:
        _check_question(q)
        assert q.stem not in seen_stems, "Doublon détecté dans le set"
        seen_stems.add(q.stem)

def test_generate_exam():
    """Vérifie qu'un examen génère bien 12 questions variées et valides."""
    qs = generate_exam(seed=123)
    assert len(qs) == 12
    themes_covered = {q.theme for q in qs}
    # Vérifie qu'au moins 4 thèmes sont représentés (tolérance)
    assert len(themes_covered) >= 4
    for q in qs:
        _check_question(q)

def test_multiple_runs_consistency():
    """Vérifie que deux appels avec la même seed donnent le même résultat."""
    qs1 = generate_set("Calcul numérique et algébrique", "Facile", 5, seed=99)
    qs2 = generate_set("Calcul numérique et algébrique", "Facile", 5, seed=99)
    stems1 = [q.stem for q in qs1]
    stems2 = [q.stem for q in qs2]
    assert stems1 == stems2, "Résultats incohérents pour la même seed"
