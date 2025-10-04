import os
import sys


def main() -> int:
    try:
        import pytest  # type: ignore
    except ImportError:
        print("PyTest n'est pas installé. Exécutez: pip install -r requirements.txt")
        return 1

    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Arguments par défaut: mode quiet
    args = ["-q", "--import-mode=importlib"]

    # Filtre optionnel: définir PYTEST_K pour cibler certains tests
    # Exemple: PYTEST_K=map python run_tests.py
    k_expr = os.environ.get("PYTEST_K")
    if k_expr:
        args += ["-k", k_expr]

    # Lancer PyTest depuis la racine (découverte automatique des tests)
    return int(pytest.main(args))


if __name__ == "__main__":
    raise SystemExit(main())