"""Diccionario de conceptos y supuestos mostrados por la interfaz."""


GLOSARIO = {
    "UF": {
        "categoria": "Entradas",
        "definicion": "Unidad de Fomento usada para convertir a CLP el precio, el arriendo referencial y las remodelaciones.",
        "formula": "Monto CLP = monto UF × valor UF ingresado.",
    },
    "Valor del departamento": {
        "categoria": "Entradas",
        "definicion": "Precio de compra expresado en UF y convertido a pesos con la UF ingresada.",
        "formula": "Valor CLP = valor en UF × UF en CLP.",
    },
    "Pie del departamento": {
        "categoria": "Financiamiento",
        "definicion": "Porcentaje del precio que se paga al inicio. Puede configurarse en 0% para analizar financiamiento total como supuesto teórico.",
        "formula": "Pie CLP = valor del departamento × porcentaje de pie.",
    },
    "Gastos de cierre": {
        "categoria": "Financiamiento",
        "definicion": "Costos iniciales asociados a la compra. El simulador los trata como un porcentaje del precio y como capital aportado.",
        "formula": "Gastos de cierre = valor del departamento × porcentaje de cierre.",
    },
    "Monto hipotecario": {
        "categoria": "Financiamiento",
        "definicion": "Parte del precio financiada por el crédito.",
        "formula": "Hipoteca = valor del departamento − pie.",
    },
    "Tasa hipotecaria": {
        "categoria": "Financiamiento",
        "definicion": "Tasa nominal anual usada por el modelo de amortización. Se divide por 12 para calcular la tasa mensual.",
        "formula": "Tasa mensual = tasa anual / 12.",
    },
    "Dividendo mensual": {
        "categoria": "Financiamiento",
        "definicion": "Cuota hipotecaria constante calculada con amortización francesa. Deja de cobrarse al terminar el plazo.",
        "formula": "Cuota = capital × tasa mensual / [1 − (1 + tasa mensual)^−meses].",
    },
    "Interés hipotecario": {
        "categoria": "Financiamiento",
        "definicion": "Costo financiero mensual aplicado al saldo pendiente.",
        "formula": "Interés del mes = saldo anterior × tasa mensual.",
    },
    "Amortización": {
        "categoria": "Financiamiento",
        "definicion": "Parte del dividendo que reduce la deuda.",
        "formula": "Amortización = dividendo − interés.",
    },
    "Saldo hipotecario": {
        "categoria": "Financiamiento",
        "definicion": "Deuda pendiente después de cada pago mensual.",
        "formula": "Saldo nuevo = saldo anterior − amortización.",
    },
    "Arriendo bruto": {
        "categoria": "Operación",
        "definicion": "Ingreso contractual antes de vacancia, comisiones y gastos.",
        "formula": "Arriendo anual = arriendo mensual × 12.",
    },
    "Crecimiento del arriendo": {
        "categoria": "Operación",
        "definicion": "Aumento nominal anual aplicado al arriendo desde el segundo año.",
        "formula": "Arriendo año n = arriendo inicial × (1 + crecimiento)^(n−1).",
    },
    "Vacancia": {
        "categoria": "Operación",
        "definicion": "Porcentaje del arriendo anual que se pierde por periodos sin arrendatario.",
        "formula": "Pérdida por vacancia = arriendo bruto × vacancia.",
    },
    "Comisión de administración": {
        "categoria": "Operación",
        "definicion": "Porcentaje del arriendo destinado a administrar la propiedad.",
        "formula": "Comisión = arriendo bruto × porcentaje de administración.",
    },
    "Reserva de contingencias": {
        "categoria": "Operación",
        "definicion": "Provisión calculada como porcentaje del arriendo para imprevistos.",
        "formula": "Reserva = arriendo bruto × porcentaje de reserva.",
    },
    "Gastos comunes": {
        "categoria": "Operación",
        "definicion": "Cargo mensual asumido por el propietario. El modelo lo mantiene constante en CLP.",
        "formula": "Gasto anual = gasto mensual × 12.",
    },
    "Contribuciones": {
        "categoria": "Operación",
        "definicion": "Pago anual ingresado por el usuario. El modelo lo mantiene constante en CLP.",
        "formula": "Se usa directamente el monto anual ingresado.",
    },
    "Seguro hipotecario": {
        "categoria": "Operación",
        "definicion": "Costo anual de seguros ingresado por el usuario, separado del dividendo y constante en CLP.",
        "formula": "Se usa directamente el monto anual ingresado.",
    },
    "Mantención": {
        "categoria": "Operación",
        "definicion": "Costo anual estimado como porcentaje del valor del departamento al inicio de cada año.",
        "formula": "Mantención = valor al inicio del año × porcentaje de mantención.",
    },
    "Remodelaciones": {
        "categoria": "Operación",
        "definicion": "Egresos extraordinarios predefinidos en UF para los años 5, 10, 15, 20 y 25.",
        "formula": "Costo CLP = remodelación en UF × valor UF ingresado.",
    },
    "Flujo neto anual": {
        "categoria": "Resultados",
        "definicion": "Caja anual que deja la propiedad antes de una eventual venta.",
        "formula": "Arriendo bruto − vacancia − gastos − dividendos del año.",
    },
    "Flujo acumulado": {
        "categoria": "Resultados",
        "definicion": "Suma del desembolso inicial y todos los flujos netos anuales hasta la fecha.",
        "formula": "−capital inicial + suma de flujos netos.",
    },
    "Plusvalía": {
        "categoria": "Venta",
        "definicion": "Crecimiento nominal anual supuesto para el precio del departamento.",
        "formula": "Valor año n = valor inicial × (1 + plusvalía)^n.",
    },
    "Costo de venta": {
        "categoria": "Venta",
        "definicion": "Porcentaje del precio proyectado descontado al vender.",
        "formula": "Costo = precio de venta × porcentaje de venta.",
    },
    "Ganancia neta del departamento": {
        "categoria": "Resultados",
        "definicion": "Ganancia nominal después de recuperar deuda, costos, aportes y flujos operacionales.",
        "formula": "Precio de venta − saldo hipotecario − costo de venta + flujo acumulado.",
    },
    "Capital aportado al departamento": {
        "categoria": "Resultados",
        "definicion": "Pie, gastos de cierre y todos los flujos negativos que el inversionista debió financiar.",
        "formula": "Capital inicial + suma de déficits anuales.",
    },
    "Cap Rate neto": {
        "categoria": "Indicadores",
        "definicion": "Rendimiento operacional del primer año antes del financiamiento.",
        "formula": "Ingreso neto operacional del año 1 / valor del departamento.",
    },
    "TIR": {
        "categoria": "Indicadores",
        "definicion": "Tasa que lleva a cero el valor presente de los aportes, flujos y liquidación del departamento.",
        "formula": "Se resuelve por bisección entre −99,99% y 500%.",
    },
    "Múltiplo del capital (MOIC)": {
        "categoria": "Indicadores",
        "definicion": "Capital final equivalente por cada peso nominal aportado al departamento.",
        "formula": "(Ganancia neta + capital aportado) / capital aportado.",
    },
    "CAGR": {
        "categoria": "Indicadores",
        "definicion": "Tasa anual compuesta aproximada derivada del múltiplo del capital.",
        "formula": "MOIC^(1 / años) − 1. No ajusta el momento de aportes posteriores; para eso se usa la TIR.",
    },
    "Inversión inicial del ETF": {
        "categoria": "ETF",
        "definicion": "Pie hipotético invertido en el ETF aunque el departamento use un pie diferente o igual a 0%.",
        "formula": "Valor del departamento × porcentaje de inversión inicial ETF.",
    },
    "Aporte mensual al ETF": {
        "categoria": "ETF",
        "definicion": "Aporte solicitado para la comparación. Solo considera el déficit entre dividendo y arriendo bruto; no incorpora otros gastos del departamento.",
        "formula": "máx(dividendo mensual − arriendo mensual, 0).",
    },
    "Saldo del ETF": {
        "categoria": "ETF",
        "definicion": "Valor acumulado de la inversión inicial y los aportes mensuales, capitalizados con una tasa efectiva mensual.",
        "formula": "Saldo nuevo = saldo anterior × (1 + tasa efectiva mensual) + aporte mensual.",
    },
    "Ganancia neta del ETF": {
        "categoria": "ETF",
        "definicion": "Rentabilidad acumulada sin contar como ganancia el dinero aportado.",
        "formula": "Saldo ETF − inversión inicial − aportes mensuales acumulados.",
    },
    "Sensibilidad": {
        "categoria": "Análisis",
        "definicion": "Recalcula el escenario cambiando plusvalía o tasa hipotecaria y manteniendo las demás entradas constantes.",
        "formula": "Cada fila es una simulación completa independiente.",
    },
}


SUPUESTOS_Y_LIMITACIONES = [
    "Todos los valores y tasas de crecimiento se modelan en términos nominales; no se descuenta inflación.",
    "La UF ingresada se mantiene constante durante toda la proyección.",
    "Gastos comunes, contribuciones y seguro se mantienen constantes en CLP.",
    "No se modelan impuestos personales, tributación de la ganancia de capital ni costos de prepago del crédito.",
    "El escenario con 0% de pie es matemático y no implica disponibilidad real de ese financiamiento.",
    "El aporte mensual del ETF excluye gastos operacionales del inmueble; por eso no representa igualdad total de desembolsos.",
    "Una comparación económica más rigurosa igualaría todos los desembolsos, impuestos y fechas de cada alternativa y compararía sus TIR.",
    "La rentabilidad del ETF se capitaliza mensualmente usando la tasa anual efectiva seleccionada.",
    "Los resultados son estimaciones educativas y no constituyen asesoría financiera.",
]
