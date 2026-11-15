"""Punto de entrada compatible para el despliegue histórico de Streamlit Cloud.

El simulador vive en ``streamlit/``. Este lanzador mantiene funcionando las
instalaciones que todavía apuntan al archivo que antiguamente estaba en la
raíz del repositorio, sin duplicar el código de la aplicación.
"""

from pathlib import Path
import runpy
import sys


APP_DIR = Path(__file__).resolve().parent / "streamlit"
APP_FILE = APP_DIR / "Simulardor inversion.py"

# Los módulos propios (investment_engine y glossary) están junto a la app.
sys.path.insert(0, str(APP_DIR))
runpy.run_path(str(APP_FILE), run_name="__main__")
