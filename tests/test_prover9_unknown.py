import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.symbolic_solvers.fol_solver.prover9_solver import FOL_Prover9_Program

logic_program_u = """Premises:
∀x (Listed(x) → ¬NegativeReviews(x)) ::: If the restaurant is listed in Yelp's recommendations, then the restaurant does not receive many negative reviews.
∀x (GreaterThanNine(x) → Listed(x)) ::: All restaurants with a rating greater than 9 are listed in Yelp's recommendations.
∃x (¬TakeOut(x) ∧ NegativeReviews(x)) ::: Some restaurants that do not provide take-out service receive many negative reviews.
∀x (Popular(x) → GreaterThanNine(x)) ::: All restaurants that are popular among local residents have ratings greater than 9.
GreaterThanNine(subway) ∨ Popular(subway) ::: Subway has a rating greater than 9 or is popular among local residents.
Conclusion:
TakeOut(subway) ∧ ¬NegativeReviews(subway) ::: Subway provides take-out service and does not receive many negative reviews."""


def test_unknown_result():
    prog = FOL_Prover9_Program(logic_program_u)
    result, error, reasoning = prog.execute_program()
    assert result == 'Unknown'
    assert "trying to prove original conclusion" in reasoning
    assert "trying to prove negation of original conclusion" in reasoning
    assert reasoning.strip().endswith("So: Unknown")
    assert "given #" not in reasoning
