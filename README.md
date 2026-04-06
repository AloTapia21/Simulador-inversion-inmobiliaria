# Simulador de Inversión Inmobiliaria

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Demo](https://img.shields.io/badge/Demo-Live-brightgreen?logo=streamlit)](https://simulador-inversion-inmobiliaria-hzmgqovfpwqsriekxk5goc.streamlit.app/)

Herramienta interactiva para evaluar y comparar inversiones en departamentos de la Región Metropolitana de Chile versus alternativas financieras (ETF), desarrollada en Python con Streamlit.

## Demo

**[Ver app en vivo →](https://simulador-inversion-inmobiliaria-hzmgqovfpwqsriekxk5goc.streamlit.app/)**

## Funcionalidades

| Módulo | Descripción |
|---|---|
| Dashboard KPIs | TIR, ROI, CAGR, Cap Rate y Ganancia Neta en tiempo real |
| Proyección de flujos | Gráfico de amortización a 30 años |
| Análisis de sensibilidad | Impacto de plusvalía y tasa hipotecaria |
| Comparador de propiedades | Evalúa hasta 5 propiedades en paralelo |
| Exportación PDF | Reporte descargable con todos los indicadores |
| Escenarios rápidos | Presets Conservador, Base y Optimista |
| Guía de indicadores | Explicación de cada métrica inmobiliaria |

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/AloTapia21/Simulador-inversion-inmobiliaria.git
cd Simulador-inversion-inmobiliaria

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
streamlit run "Simulardor inversion.py"
```

## Tecnologías

- [Python](https://www.python.org/) — lenguaje base
- [Streamlit](https://streamlit.io/) — framework de la interfaz web
- [Plotly](https://plotly.com/python/) — gráficos interactivos
- [ReportLab](https://www.reportlab.com/) — generación de PDF

## Autor

**Alonso Tapia D.**

## Licencia

Distribuido bajo la licencia MIT. Ver [LICENSE](LICENSE) para más información.
