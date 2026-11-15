# VETA · Inversión inmobiliaria

Este repositorio contiene dos aplicaciones complementarias para evaluar y controlar inversiones inmobiliarias:

| Carpeta | Aplicación | Uso principal |
|---|---|---|
| [`streamlit/`](streamlit/) | Simulador financiero en Python | Evaluar una compra, proyectar flujos y comparar escenarios antes de invertir. |
| [`html/`](html/) | VETA, aplicación web Next.js | Guardar proyectos y comparar mensualmente la estimación con los resultados reales. |

## Aplicación web

VETA está preparada para desplegarse en Vercel y usa Supabase para autenticación y datos. Permite:

- mantener varios departamentos o proyectos;
- editar todos los supuestos financieros;
- registrar arriendo, dividendo, vacancia, administración, gastos comunes, contribuciones, seguro, mantenciones, arreglos y otros desembolsos;
- revisar flujo estimado versus real, diferencias y acumulados;
- compartir una inversión con copropietarios y asignar cada pago o ingreso a una o varias personas;
- registrar el monto CLP y la UF histórica de pie, dividendos, arriendos y demás movimientos;
- estimar valor actual, deuda, patrimonio y TIR con el motor financiero;
- separar pie contractual, bono pie, desembolso efectivo y una eventual devolución de IVA;
- modelar la exención DFL2 de las primeras viviendas y el escenario opcional del 5% desde 2027 para múltiples propiedades;
- proyectar el resultado de venta;
- exportar el historial a CSV para abrirlo en Google Sheets;
- usar una interfaz responsive desde computador o teléfono.

Consulta la [guía de la aplicación web](html/README.md) para configurar Supabase y Vercel.

## Simulador Streamlit

La ruta recomendada para un despliegue nuevo en Streamlit Community Cloud es
`streamlit/Simulardor inversion.py`. El repositorio conserva además un lanzador
compatible en la raíz para que los despliegues antiguos sigan funcionando.

```bash
cd streamlit
python -m venv .venv
pip install -r requirements.txt
streamlit run "Simulardor inversion.py"
```

La metodología y las funciones del simulador están documentadas en [`streamlit/README.md`](streamlit/README.md).

## Verificación

```bash
# Web
cd html
npm ci
npm run lint
npm run typecheck
npm test
npm run build

# Motor financiero
cd ../streamlit
python -m unittest discover -s tests -v
```

## Licencia

MIT. Consulta [LICENSE](LICENSE).
