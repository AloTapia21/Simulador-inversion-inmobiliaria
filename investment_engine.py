"""Motor financiero puro para el simulador de inversión inmobiliaria.

Este módulo no depende de Streamlit, de modo que los cálculos se pueden probar
sin iniciar la interfaz web.
"""

from math import isfinite


HORIZONTE_ANIOS = 30


def calcular_tir(flujos, max_iter=200, tol=1e-7):
    """Calcula la TIR anual mediante bisección en el rango -99,99% a 500%.

    Retorna ``None`` cuando no hay flujos de ambos signos o no existe una raíz
    dentro del rango. La bisección evita las divergencias que puede producir
    Newton-Raphson cerca de una tasa de -100%.
    """
    if len(flujos) < 2 or not any(f < 0 for f in flujos) or not any(f > 0 for f in flujos):
        return None

    def vpn(tasa):
        return sum(flujo / (1 + tasa) ** periodo for periodo, flujo in enumerate(flujos))

    izquierda, derecha = -0.9999, 5.0
    vpn_izq, vpn_der = vpn(izquierda), vpn(derecha)
    if not (isfinite(vpn_izq) and isfinite(vpn_der)) or vpn_izq * vpn_der > 0:
        return None

    for _ in range(max_iter):
        medio = (izquierda + derecha) / 2
        vpn_medio = vpn(medio)
        if abs(vpn_medio) < tol or (derecha - izquierda) / 2 < tol:
            return medio
        if vpn_izq * vpn_medio <= 0:
            derecha = medio
        else:
            izquierda, vpn_izq = medio, vpn_medio

    return (izquierda + derecha) / 2


def calcular_plan_hipotecario(capital, tasa_anual, plazo_anios, horizonte=HORIZONTE_ANIOS):
    """Genera un calendario anual a partir de una amortización mensual exacta."""
    if capital < 0 or tasa_anual < 0 or plazo_anios <= 0 or horizonte < 0:
        raise ValueError("Los parámetros hipotecarios no pueden ser negativos y el plazo debe ser positivo")

    total_meses = plazo_anios * 12
    tasa_mensual = tasa_anual / 12
    if capital == 0:
        cuota_mensual = 0.0
    elif tasa_mensual:
        cuota_mensual = capital * tasa_mensual / (1 - (1 + tasa_mensual) ** (-total_meses))
    else:
        cuota_mensual = capital / total_meses

    saldos = [float(capital)]
    pagos_anuales = [0.0]
    intereses_anuales = [0.0]
    amortizaciones_anuales = [0.0]
    pagos_mensuales = []
    saldo = float(capital)
    meses_pagados = 0

    for _anio in range(1, horizonte + 1):
        pago_anual = interes_anual = amortizacion_anual = 0.0
        for _mes in range(12):
            if meses_pagados >= total_meses or saldo <= 1e-7:
                pago = interes = amortizacion = 0.0
            else:
                interes = saldo * tasa_mensual
                amortizacion = min(cuota_mensual - interes, saldo)
                pago = interes + amortizacion
                saldo = max(0.0, saldo - amortizacion)
                meses_pagados += 1
            pagos_mensuales.append(pago)
            pago_anual += pago
            interes_anual += interes
            amortizacion_anual += amortizacion

        saldos.append(saldo)
        pagos_anuales.append(pago_anual)
        intereses_anuales.append(interes_anual)
        amortizaciones_anuales.append(amortizacion_anual)

    return {
        "cuota_mensual": cuota_mensual,
        "saldos": saldos,
        "pagos_anuales": pagos_anuales,
        "pagos_mensuales": pagos_mensuales,
        "intereses_anuales": intereses_anuales,
        "amortizaciones_anuales": amortizaciones_anuales,
    }


def compute_simulation(p):
    """Calcula los flujos inmobiliarios y un ETF con aportes equivalentes."""
    uf = p["uf"]
    val_uf = p["val_uf"]
    if uf <= 0 or val_uf <= 0:
        raise ValueError("La UF y el valor del departamento deben ser positivos")
    if p["arriendo_uf"] < 0:
        raise ValueError("El arriendo no puede ser negativo")
    if not 0 <= p["pie"] <= 1 or not 0 <= p.get("etf_pie", p["pie"]) <= 1:
        raise ValueError("Los porcentajes de pie deben estar entre 0% y 100%")
    if not 1 <= p["yr_venta"] <= HORIZONTE_ANIOS:
        raise ValueError(f"El año de venta debe estar entre 1 y {HORIZONTE_ANIOS}")

    val_clp = uf * val_uf
    pie_clp = val_clp * p["pie"]
    cierre = val_clp * p["gastos_cierre"]
    cap_total = pie_clp + cierre
    hipot = val_clp * (1 - p["pie"])

    plan = calcular_plan_hipotecario(hipot, p["tasa"], p["plazo"])
    div_m = plan["cuota_mensual"]
    saldo_h = plan["saldos"]
    pagos_hipoteca = plan["pagos_anuales"]
    pagos_mensuales = plan["pagos_mensuales"]
    interes_anual = plan["intereses_anuales"]
    amort_anual = plan["amortizaciones_anuales"]
    rent_m0 = uf * p["arriendo_uf"]

    years = list(range(HORIZONTE_ANIOS + 1))
    val_d, arr_b, gastos = [], [], []
    flujo_n, flujo_a, gan_v = [], [], []
    etf_b, etf_saldo_hist, etf_aportes_hist = [], [], []
    etf_aporte_mensual_hist, etf_aportes_anuales = [], []

    flujo_acum = -cap_total
    etf_capital_inicial = val_clp * p.get("etf_pie", p["pie"])
    etf_saldo = etf_capital_inicial
    etf_aportes = etf_capital_inicial
    tasa_etf_mensual = (1 + p["etf_ret"]) ** (1 / 12) - 1

    for yr in years:
        vd = val_clp * (1 + p["plusvalia"]) ** yr
        val_d.append(vd)

        if yr == 0:
            arr_b.append(0.0)
            gastos.append(0.0)
            flujo_n.append(-cap_total)
            flujo_a.append(-cap_total)
            gan_v.append(None)
            etf_b.append(0.0)
            etf_saldo_hist.append(etf_saldo)
            etf_aportes_hist.append(etf_aportes)
            etf_aporte_mensual_hist.append(0.0)
            etf_aportes_anuales.append(0.0)
            continue

        rent_anual = rent_m0 * 12 * (1 + p["rent_gr"]) ** (yr - 1)
        arr_b.append(rent_anual)

        vac_loss = rent_anual * p["vacancia"]
        adm_loss = rent_anual * p["adm"]
        res_loss = rent_anual * p["reserva"]
        gcom_anual = p["gcom"] * 12
        cont_anual = p["contrib"]
        seg_anual = p["seguro"]
        valor_inicio_anio = val_clp * (1 + p["plusvalia"]) ** (yr - 1)
        mant_anual = valor_inicio_anio * p["mant"]
        remo = uf * p["remodelaciones"].get(yr, 0)
        gasto = vac_loss + adm_loss + res_loss + gcom_anual + cont_anual + seg_anual + mant_anual + remo
        gastos.append(gasto)

        flujo = rent_anual - gasto - pagos_hipoteca[yr]
        flujo_n.append(flujo)
        flujo_acum += flujo
        flujo_a.append(flujo_acum)

        costo_vta = vd * p["costo_venta"]
        gan_v.append(vd - saldo_h[yr] - costo_vta + flujo_acum)

        # Regla solicitada para el benchmark: el ETF parte con un pie hipotético
        # independiente del pie del departamento. Cada mes recibe solamente la
        # diferencia positiva entre dividendo y arriendo bruto. Los gastos del
        # inmueble no forman parte de este aporte y se informan como limitación.
        aporte_anual_etf = 0.0
        aporte_representativo = 0.0
        for mes_del_anio in range(12):
            indice_mes = (yr - 1) * 12 + mes_del_anio
            aporte_mes = max(0.0, pagos_mensuales[indice_mes] - rent_anual / 12)
            etf_saldo = etf_saldo * (1 + tasa_etf_mensual) + aporte_mes
            etf_aportes += aporte_mes
            aporte_anual_etf += aporte_mes
            if mes_del_anio == 0:
                aporte_representativo = aporte_mes
        etf_saldo_hist.append(etf_saldo)
        etf_aportes_hist.append(etf_aportes)
        etf_b.append(etf_saldo - etf_aportes)
        etf_aporte_mensual_hist.append(aporte_representativo)
        etf_aportes_anuales.append(aporte_anual_etf)

    cap_rate_neto = (
        rent_m0 * 12 * (1 - p["vacancia"] - p["adm"] - p["reserva"])
        - (p["gcom"] * 12 + p["contrib"] + p["seguro"])
        - val_clp * p["mant"]
    ) / val_clp

    yr_venta = p["yr_venta"]
    gan_yr = gan_v[yr_venta] if yr_venta > 0 else None
    capital_aportado = cap_total + sum(max(0.0, -flujo_n[i]) for i in range(1, yr_venta + 1))
    roi = ((gan_yr + capital_aportado) / capital_aportado) if gan_yr is not None and capital_aportado > 0 else None
    cagr = (roi ** (1 / yr_venta) - 1) if roi is not None and roi > 0 and yr_venta > 0 else None
    etf_yr = etf_b[yr_venta]
    yr_pos = next((i for i in range(1, HORIZONTE_ANIOS + 1) if flujo_n[i] > 0), None)

    flujos_tir = [-cap_total]
    for i in range(1, yr_venta + 1):
        flujo = flujo_n[i]
        if i == yr_venta:
            liquidacion = val_d[i] - saldo_h[i] - val_d[i] * p["costo_venta"]
            flujo += liquidacion
        flujos_tir.append(flujo)

    return {
        "years": years,
        "val_d": val_d,
        "arr_b": arr_b,
        "gastos": gastos,
        "flujo_n": flujo_n,
        "flujo_a": flujo_a,
        "saldo_h": saldo_h,
        "gan_v": gan_v,
        "etf_b": etf_b,
        "etf_saldo": etf_saldo_hist,
        "etf_aportes": etf_aportes_hist,
        "etf_capital_inicial": etf_capital_inicial,
        "etf_aporte_mensual": etf_aporte_mensual_hist,
        "etf_aportes_anuales": etf_aportes_anuales,
        "interes_anual": interes_anual,
        "amort_anual": amort_anual,
        "pagos_hipoteca": pagos_hipoteca,
        "cap_total": cap_total,
        "capital_aportado": capital_aportado,
        "val_clp": val_clp,
        "pie_clp": pie_clp,
        "hipot": hipot,
        "div_m": div_m,
        "rent_m0": rent_m0,
        "cap_rate_neto": cap_rate_neto,
        "gan_yr": gan_yr,
        "roi": roi,
        "cagr": cagr,
        "tir": calcular_tir(flujos_tir),
        "etf_yr": etf_yr,
        "yr_pos": yr_pos,
        "yr_venta": yr_venta,
    }
