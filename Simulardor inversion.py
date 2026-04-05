import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador Inversión Inmobiliaria",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --navy:   #0f1923;
    --ink:    #1a2332;
    --slate:  #263545;
    --steel:  #3d5166;
    --teal:   #00c9a7;
    --teal2:  #00a88d;
    --amber:  #f59e0b;
    --rose:   #f43f5e;
    --sky:    #38bdf8;
    --text:   #e8edf2;
    --muted:  #8a9bb0;
    --card:   rgba(26,35,50,0.85);
    --border: rgba(61,81,102,0.4);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--navy);
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--ink);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .stSlider > div > div > div { background: var(--teal) !important; }

/* Main background */
.main .block-container {
    background: var(--navy);
    padding-top: 1.5rem;
    max-width: 1400px;
}

/* Headers */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Metric cards */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    backdrop-filter: blur(8px);
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
}
.metric-value.positive { color: var(--teal); }
.metric-value.negative { color: var(--rose); }
.metric-value.amber    { color: var(--amber); }
.metric-sub {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.25rem;
}

/* Section titles */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--teal);
    border-left: 3px solid var(--teal);
    padding-left: 0.75rem;
    margin: 1.5rem 0 0.75rem;
}

/* Pill badges */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-green  { background: rgba(0,201,167,0.15); color: var(--teal);  border: 1px solid rgba(0,201,167,0.3); }
.badge-red    { background: rgba(244,63,94,0.15);  color: var(--rose);  border: 1px solid rgba(244,63,94,0.3); }
.badge-amber  { background: rgba(245,158,11,0.15); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }

/* Table */
.comp-table { width:100%; border-collapse: collapse; }
.comp-table th {
    background: var(--slate);
    padding: 0.6rem 1rem;
    text-align: left;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
}
.comp-table td {
    padding: 0.55rem 1rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
}
.comp-table tr:last-child td { border-bottom: none; }
.comp-table tr:hover td { background: rgba(61,81,102,0.2); }
.winner-row td { color: var(--teal) !important; font-weight: 600; }

/* Verdict banner */
.verdict {
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    margin: 1rem 0;
    border: 1px solid;
}
.verdict-win  { background: rgba(0,201,167,0.08);  border-color: rgba(0,201,167,0.3); }
.verdict-warn { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.3); }
.verdict-lose { background: rgba(244,63,94,0.08);  border-color: rgba(244,63,94,0.3);  }

/* Indicator guide cards */
.guide-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.guide-name { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.3rem; }
.guide-desc { font-size: 0.82rem; color: var(--muted); line-height: 1.5; }

/* Streamlit overrides */
div[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    letter-spacing: 0.05em;
}
div.stButton > button {
    background: var(--teal);
    color: var(--navy);
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.4rem;
}
div.stButton > button:hover { background: var(--teal2); color: var(--navy); }

/* Number input */
div[data-testid="stNumberInput"] input {
    background: var(--slate);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 6px;
}

hr { border-color: var(--border); }

/* Plotly background matching */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ─── COMPUTATION ENGINE ──────────────────────────────────────────────────────

def compute_simulation(p):
    """Full 30-year cash flow model. Returns dict of results."""
    uf     = p['uf']
    val_uf = p['val_uf']
    val_clp = uf * val_uf
    pie_clp  = val_clp * p['pie']
    cierre   = val_clp * p['gastos_cierre']
    cap_total = pie_clp + cierre
    hipot    = val_clp * (1 - p['pie'])
    tasa_m   = p['tasa'] / 12
    meses    = p['plazo'] * 12

    if tasa_m > 0:
        div_m = hipot * tasa_m / (1 - (1 + tasa_m) ** (-meses))
    else:
        div_m = hipot / meses

    rent_m0 = uf * p['arriendo_uf']

    years   = list(range(31))
    val_d   = []   # valor depto
    arr_b   = []   # arriendo bruto anual
    gastos  = []   # gastos op anual
    flujo_n = []   # flujo neto anual
    flujo_a = []   # flujo acumulado
    saldo_h = []   # saldo hipoteca
    gan_v   = []   # ganancia neta si vende ese año
    etf_b   = []   # saldo ETF base

    deficit_acum = -cap_total
    etf_saldo    = cap_total  # ETF starts with same capital

    for yr in years:
        # Valor depto
        vd = val_clp * (1 + p['plusvalia']) ** yr
        val_d.append(vd)

        if yr == 0:
            arr_b.append(0)
            gastos.append(0)
            flujo_n.append(-cap_total)
            flujo_a.append(-cap_total)
            saldo_h.append(hipot)
            gan_v.append(None)
            etf_b.append(cap_total)
            continue

        # Arriendo bruto año yr
        rent_anual = rent_m0 * 12 * (1 + p['rent_gr']) ** (yr - 1)
        arr_b.append(rent_anual)

        # Gastos operacionales
        vac_loss = rent_anual * p['vacancia']
        adm_loss = rent_anual * p['adm']
        res_loss = rent_anual * p['reserva']
        gcom_anual = p['gcom'] * 12
        contrib_anual = p['contrib']
        seg_anual = p['seguro']
        mant_anual = vd * p['mant']

        remo = 0
        if yr in p['remodelaciones']:
            remo = uf * p['remodelaciones'][yr]

        gast = vac_loss + adm_loss + res_loss + gcom_anual + contrib_anual + seg_anual + mant_anual + remo
        gastos.append(gast)

        # Flujo neto
        fn = rent_anual - gast - div_m * 12
        flujo_n.append(fn)
        deficit_acum += fn
        flujo_a.append(deficit_acum)

        # Saldo hipoteca
        if tasa_m > 0:
            sh = hipot * (1 + tasa_m) ** (yr * 12) - div_m * ((1 + tasa_m) ** (yr * 12) - 1) / tasa_m
        else:
            sh = max(0, hipot - div_m * yr * 12)
        saldo_h.append(max(0, sh))

        # Ganancia neta de venta
        costo_vta = vd * p['costo_venta']
        gv = vd - max(0, sh) - costo_vta + deficit_acum
        gan_v.append(gv)

        # ETF base: cada año aporta el subsidio (si flujo negativo, ese dinero va al ETF)
        subsidio_mes = max(0, div_m - (rent_anual / 12) * (1 - p['vacancia'] - p['adm'] - p['reserva']) +
                          (gcom_anual + contrib_anual + seg_anual) / 12 + mant_anual / 12)
        etf_saldo = etf_saldo * (1 + p['etf_ret']) + subsidio_mes * 12
        etf_b.append(etf_saldo)

    # KPIs
    cap_rate_neto = (rent_m0 * 12 * (1 - p['vacancia'] - p['adm'] - p['reserva']) -
                     (p['gcom'] * 12 + p['contrib'] + p['seguro']) -
                     val_clp * p['mant']) / val_clp

    yr_venta = p['yr_venta']
    gan_yr   = gan_v[yr_venta] if yr_venta > 0 else None
    roi      = (gan_yr / cap_total) if (gan_yr and cap_total > 0) else None
    cagr     = ((gan_yr / cap_total) ** (1 / yr_venta) - 1) if (gan_yr and gan_yr > 0 and yr_venta > 0) else None
    etf_yr   = etf_b[yr_venta]

    # Año flujo positivo
    yr_pos = next((i for i in range(1, 31) if flujo_n[i] > 0), None)

    return {
        'years': years,
        'val_d': val_d, 'arr_b': arr_b, 'gastos': gastos,
        'flujo_n': flujo_n, 'flujo_a': flujo_a,
        'saldo_h': saldo_h, 'gan_v': gan_v, 'etf_b': etf_b,
        'cap_total': cap_total, 'val_clp': val_clp,
        'pie_clp': pie_clp, 'hipot': hipot, 'div_m': div_m,
        'rent_m0': rent_m0, 'cap_rate_neto': cap_rate_neto,
        'gan_yr': gan_yr, 'roi': roi, 'cagr': cagr,
        'etf_yr': etf_yr, 'yr_pos': yr_pos,
        'yr_venta': yr_venta,
    }


def fmt_clp(v, decimals=0):
    """Número completo con separadores de miles, sin abreviar."""
    if v is None: return "—"
    if v < 0:
        return f"(${abs(v):,.{decimals}f})"
    return f"${v:,.{decimals}f}"

def fmt_pct(v):
    if v is None: return "—"
    return f"{v*100:.1f}%"

def color_class(v):
    if v is None: return ""
    return "positive" if v >= 0 else "negative"


# ─── PLOTLY THEME ────────────────────────────────────────────────────────────
PLOT_BG    = "rgba(15,25,35,0)"
GRID_COLOR = "rgba(61,81,102,0.3)"
FONT_COLOR = "#8a9bb0"
TEAL       = "#00c9a7"
AMBER      = "#f59e0b"
ROSE       = "#f43f5e"
SKY        = "#38bdf8"
PURPLE     = "#a78bfa"

def base_layout(title="", height=360):
    return dict(
        title=dict(text=title, font=dict(family="Syne", size=13, color="#e8edf2"), x=0.0, xanchor="left"),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="DM Sans", color=FONT_COLOR, size=11),
        height=height,
        margin=dict(l=0, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_COLOR, zeroline=False, tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0, font=dict(size=10)),
        hovermode="x unified",
    )


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:Syne;font-size:1.3rem;font-weight:800;color:#00c9a7;margin-bottom:0">🏢 SIMULADOR</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.72rem;color:#8a9bb0;letter-spacing:0.1em;text-transform:uppercase;margin-top:0">Inversión Inmobiliaria RM</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.68rem;color:#3d5166;margin-top:0.2rem;margin-bottom:0">Desarrollado por</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.78rem;color:#00c9a7;font-weight:600;margin-top:0rem;letter-spacing:0.03em">Alonso Tapia D.</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="section-title">Datos del Departamento</div>', unsafe_allow_html=True)
    uf_val   = st.number_input("Valor UF (CLP)", value=39842, step=100, format="%d")
    dep_uf   = st.number_input("Valor depto (UF)", value=5000, step=50, format="%d")
    arr_clp  = st.number_input("Arriendo inicial (CLP/mes)", value=1_035_000, step=10_000, format="%d")
    arr_uf   = arr_clp / uf_val  # conversión automática a UF
    st.markdown(f'<p style="font-size:0.72rem;color:#8a9bb0;margin-top:-0.5rem">≈ {arr_uf:.1f} UF/mes (referencial)</p>', unsafe_allow_html=True)
    rent_gr  = st.slider("Crecimiento arriendo anual", 2.0, 8.0, 4.0, 0.5, format="%.1f%%") / 100
    vacancia = st.slider("Vacancia anual", 0.0, 20.0, 8.0, 1.0, format="%.0f%%") / 100
    adm      = st.slider("Comisión administradora", 0.0, 15.0, 8.0, 1.0, format="%.0f%%") / 100
    gcom     = st.number_input("Gastos comunes (CLP/mes)", value=100_000, step=5_000, format="%d")
    contrib  = st.number_input("Contribuciones SII (CLP/año)", value=320_000, step=10_000, format="%d")
    seguro   = st.number_input("Seguro hipotecario (CLP/año)", value=120_000, step=5_000, format="%d")
    mant     = st.slider("Mantención anual (% valor)", 0.1, 2.0, 0.5, 0.1, format="%.1f%%") / 100
    reserva  = st.slider("Reserva contingencias (% arr.)", 0.0, 10.0, 5.0, 1.0, format="%.0f%%") / 100

    st.divider()
    st.markdown('<div class="section-title">Financiamiento</div>', unsafe_allow_html=True)
    pie_pct  = st.number_input("Pie inicial (%)", value=20.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f") / 100
    tasa_h   = st.number_input("Tasa hipotecaria anual (%)", value=4.0, min_value=0.0, max_value=30.0, step=0.01, format="%.2f") / 100
    plazo    = st.selectbox("Plazo crédito (años)", [15, 20, 25, 30], index=3)
    gc_pct   = st.number_input("Gastos cierre (%)", value=2.5, min_value=0.0, max_value=20.0, step=0.1, format="%.1f") / 100
    cv_pct   = st.number_input("Costo venta (%)", value=2.5, min_value=0.0, max_value=20.0, step=0.1, format="%.1f") / 100

    st.divider()
    st.markdown('<div class="section-title">Plusvalía & Zona</div>', unsafe_allow_html=True)
    zona = st.selectbox("Zona RM", [
        "Premium — 7.5% (Vitacura, El Golf)",
        "Consolidada — 5.5% (Ñuñoa, La Reina)",
        "Emergente — 4.0% (San Miguel, Estación Central)",
        "Periférica — 3.0% (Maipú, Puente Alto)",
        "Personalizada",
    ], index=1)
    zona_map = {"Premium": 0.075, "Consolidada": 0.055, "Emergente": 0.040, "Periférica": 0.030}
    zona_key = zona.split("—")[0].strip()
    if zona_key == "Personalizada":
        plusvalia = st.slider("Plusvalía nominal/año", 1.0, 10.0, 5.5, 0.5, format="%.1f%%") / 100
    else:
        plusvalia = zona_map[zona_key]
        st.markdown(f'<span class="badge badge-amber">Plusvalía nominal: {plusvalia*100:.1f}%/año</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="section-title">Comparación ETF</div>', unsafe_allow_html=True)
    etf_ret = st.slider("Retorno ETF neto anual", 5.0, 15.0, 10.0, 0.5, format="%.1f%%") / 100

    st.divider()
    st.markdown('<div class="section-title">Año de Análisis de Venta</div>', unsafe_allow_html=True)
    yr_venta = st.slider("¿En qué año planeas vender?", 1, 30, 10)

    remos = {5: 80, 10: 150, 15: 200, 20: 250, 25: 200}

# ─── COMPUTE ─────────────────────────────────────────────────────────────────
params = dict(
    uf=uf_val, val_uf=dep_uf, arriendo_uf=arr_uf, rent_gr=rent_gr,
    vacancia=vacancia, adm=adm, gcom=gcom, contrib=contrib,
    seguro=seguro, mant=mant, reserva=reserva,
    pie=pie_pct, tasa=tasa_h, plazo=plazo,
    gastos_cierre=gc_pct, costo_venta=cv_pct,
    plusvalia=plusvalia, etf_ret=etf_ret,
    yr_venta=yr_venta, remodelaciones=remos,
)
R = compute_simulation(params)
yrs = R['years']


# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:0.5rem">
  <h1 style="font-family:Syne;font-size:2rem;font-weight:800;color:#e8edf2;margin:0">Simulador Inversión Inmobiliaria</h1>
  <span class="badge badge-amber">Región Metropolitana · Chile</span>
</div>
<p style="color:#8a9bb0;font-size:0.85rem;margin-bottom:1.2rem">
  Depto de <b style="color:#e8edf2">{dep_uf:,} UF</b> · ${R['val_clp']:,.0f} CLP · 
  Arriendo <b style="color:#e8edf2">${arr_clp:,.0f}/mes</b> · Zona {zona_key} · 
  Vendiendo en año <b style="color:#00c9a7">{yr_venta}</b>
</p>
""", unsafe_allow_html=True)


# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Dashboard", "📈  Flujos & Proyecciones", "🔁  Comparador", "📖  Guía de Indicadores"
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── KPI Row 1 ──
    k1, k2, k3, k4, k5 = st.columns(5)
    metrics_row1 = [
        (k1, "Capital invertido",   fmt_clp(R['cap_total']),       "",                      ""),
        (k2, "Dividendo mensual",   fmt_clp(R['div_m']),           "",                      "amber"),
        (k3, "Arriendo mes 1 (CLP)",  fmt_clp(R['rent_m0']),         f"≈ {arr_uf:.1f} UF/mes",        ""),
        (k4, "Cap Rate neto año 1", fmt_pct(R['cap_rate_neto']),   "Benchmark RM: 2%–4%",   "positive" if R['cap_rate_neto'] >= 0.02 else "negative"),
        (k5, "Subsidio mes 1",      fmt_clp(max(0, R['div_m'] - R['rent_m0']*(1-vacancia-adm-reserva)+((gcom+(contrib+seguro)/12)+R['val_clp']*mant/12))),
                                                                    "De tu bolsillo/mes",    "negative" if R['div_m'] > R['rent_m0'] else "positive"),
    ]
    for col, label, val, sub, cls in metrics_row1:
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value {cls}">{val}</div>
              <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI Row 2: Venta ──
    gan = R['gan_yr']
    etf = R['etf_yr']
    diff = (gan or 0) - etf
    roi  = R['roi']
    cagr = R['cagr']
    yr_pos = R['yr_pos']

    k6, k7, k8, k9, k10 = st.columns(5)
    metrics_row2 = [
        (k6,  "Valor depto año " + str(yr_venta), fmt_clp(R['val_d'][yr_venta]), f"Plusvalía {plusvalia*100:.1f}%/año", "positive"),
        (k7,  "Ganancia neta al vender",          fmt_clp(gan),                  f"Precio − Deuda − Costos + Flujos",    "positive" if (gan and gan > 0) else "negative"),
        (k8,  "ROI sobre capital propio",          f"{roi:.2f}x" if roi else "—", f"Sobre ${fmt_clp(R['cap_total'])} invertidos", "positive" if (roi and roi >= 1) else "negative"),
        (k9,  "CAGR anual",                        fmt_pct(cagr),                 f"Tasa compuesta a {yr_venta} años",   "positive" if (cagr and cagr > 0.05) else "amber"),
        (k10, "vs ETF " + fmt_pct(etf_ret) + "/año", fmt_clp(diff),              "Depto − ETF mismo capital",           "positive" if diff >= 0 else "negative"),
    ]
    for col, label, val, sub, cls in metrics_row2:
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value {cls}">{val}</div>
              <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── VERDICT BANNER ──
    if gan and diff > 0 and roi and roi >= 1.5:
        verdict_cls = "verdict-win"
        icon = "✅"
        msg  = f"<b>Buena inversión</b> — El depto supera al ETF por <b>{fmt_clp(diff)}</b> al año {yr_venta}. " \
               f"ROI de <b>{roi:.2f}x</b> sobre tu capital propio ({fmt_pct(cagr)} CAGR). " \
               f"{'El flujo se vuelve positivo en el año ' + str(yr_pos) + '.' if yr_pos else 'El flujo sigue negativo — tu apuesta es a la plusvalía.'}"
    elif gan and diff >= 0:
        verdict_cls = "verdict-warn"
        icon = "⚠️"
        msg  = f"<b>Inversión aceptable</b> — El depto supera levemente al ETF ({fmt_clp(diff)}). " \
               f"ROI {roi:.2f}x. Considera si el riesgo inmobiliario justifica el diferencial marginal."
    else:
        verdict_cls = "verdict-lose"
        icon = "❌"
        msg  = f"<b>El ETF gana en este escenario</b> — El ETF te daría <b>{fmt_clp(-diff)}</b> más que el depto al año {yr_venta}. " \
               f"Considera zona con mayor plusvalía o mayor horizonte de inversión."

    st.markdown(f'<div class="verdict {verdict_cls}" style="font-size:0.88rem">{icon} {msg}</div>',
                unsafe_allow_html=True)

    # ── CHARTS ROW ──
    c_left, c_right = st.columns(2)

    with c_left:
        # Waterfall ganancia neta
        vd_yr  = R['val_d'][yr_venta]
        sh_yr  = R['saldo_h'][yr_venta]
        cv_yr  = vd_yr * cv_pct
        fa_yr  = R['flujo_a'][yr_venta]

        gan_neta_val = vd_yr - sh_yr - cv_yr + fa_yr
        wf_x = ["Precio\nventa", "− Deuda\nbanco", "− Costos\nventa", "+ Flujos\nacum.", "GANANCIA\nNETA"]
        wf_y = [vd_yr, -sh_yr, -cv_yr, fa_yr, 0]
        wf_text = [
            f"${vd_yr:,.0f}",
            f"(${sh_yr:,.0f})",
            f"(${cv_yr:,.0f})",
            f"${fa_yr:,.0f}" if fa_yr >= 0 else f"(${abs(fa_yr):,.0f})",
            f"${gan_neta_val:,.0f}" if gan_neta_val >= 0 else f"(${abs(gan_neta_val):,.0f})",
        ]
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=wf_x,
            y=wf_y,
            connector=dict(line=dict(color="rgba(61,81,102,0.5)")),
            increasing=dict(marker=dict(color=TEAL)),
            decreasing=dict(marker=dict(color=ROSE)),
            totals=dict(marker=dict(color=AMBER)),
            text=wf_text,
            textposition="outside",
            textfont=dict(size=8, color="#e8edf2"),
        ))
        layout_wf = base_layout(f"Desglose ganancia neta — año {yr_venta}", height=360)
        layout_wf['yaxis']['tickformat'] = "$,.0f"
        layout_wf['margin'] = dict(l=10, r=10, t=40, b=60)
        fig.update_layout(**layout_wf)
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        # Cap Rate — barra horizontal clara con contexto
        cr = R['cap_rate_neto'] * 100
        cr_color = TEAL if cr >= 2 else (AMBER if cr >= 1 else ROSE)
        benchmarks = [
            ("Tu Cap Rate", cr, cr_color),
            ("Mínimo aceptable", 2.0, "rgba(245,158,11,0.6)"),
            ("Benchmark RM", 3.0, "rgba(0,201,167,0.4)"),
            ("Excelente", 4.5, "rgba(0,201,167,0.2)"),
        ]
        fig = go.Figure()
        for label, val, color in benchmarks:
            fig.add_trace(go.Bar(
                name=label, x=[val], y=[label],
                orientation='h',
                marker=dict(color=color, line=dict(width=0)),
                text=[f"{val:.2f}%"],
                textposition="outside",
                textfont=dict(size=10, color="#e8edf2"),
                hovertemplate=f"{label}: {val:.2f}%<extra></extra>",
            ))
        fig.add_vline(x=cr, line=dict(color=cr_color, width=3, dash="solid"))
        layout_cr = base_layout("Cap Rate Neto Año 1", height=280)
        layout_cr['xaxis'] = dict(
            range=[0, 6], showgrid=True, gridcolor=GRID_COLOR,
            ticksuffix="%", tickfont=dict(size=10), zeroline=False
        )
        layout_cr['yaxis'] = dict(showgrid=False, zeroline=False, tickfont=dict(size=10))
        layout_cr['showlegend'] = False
        layout_cr['barmode'] = 'overlay'
        layout_cr['margin'] = dict(l=10, r=80, t=50, b=20)
        fig.update_layout(**layout_cr)

        cr_label = "✅ Bueno" if cr >= 2 else ("⚠️ Bajo" if cr >= 1 else "❌ Muy bajo")
        cr_txt_color = "#00c9a7" if cr >= 2 else ("#f59e0b" if cr >= 1 else "#f43f5e")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:0.3rem">
          <span style="font-family:Syne;font-size:2rem;font-weight:800;color:{cr_txt_color}">{cr:.2f}%</span>
          <span style="font-size:0.8rem;color:#8a9bb0;margin-left:0.5rem">{cr_label}</span>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    # ── COST BREAKDOWN DONUT ──
    c_pie, c_info = st.columns([1, 1.6])
    with c_pie:
        pie_clp  = R['pie_clp']
        cier_clp = R['val_clp'] * gc_pct
        div_10   = R['div_m'] * 12 * yr_venta
        total_out = pie_clp + cier_clp + div_10

        fig = go.Figure(go.Pie(
            labels=["Pie inicial", "Gastos cierre", f"Dividendos {yr_venta} años"],
            values=[pie_clp, cier_clp, div_10],
            hole=0.55,
            marker=dict(colors=[TEAL, AMBER, SKY],
                        line=dict(color=PLOT_BG, width=2)),
            textinfo="label+percent",
            textfont=dict(size=9),
            hovertemplate="%{label}: $%{value:,.0f}<extra></extra>",
        ))
        fig.update_layout(**base_layout(f"Desembolso total a {yr_venta} años", height=290))
        fig.update_layout(showlegend=False)
        fig.add_annotation(text=f"{fmt_clp(total_out)}<br><span style='font-size:9px'>total salida</span>",
                           x=0.5, y=0.5, showarrow=False, align="center",
                           font=dict(family="Syne", size=12, color="#e8edf2"))
        st.plotly_chart(fig, use_container_width=True)

    with c_info:
        st.markdown('<div class="section-title">Resumen financiero</div>', unsafe_allow_html=True)
        info_rows = [
            ("Valor depto",        fmt_clp(R['val_clp'])),
            ("Pie inicial ({}%)".format(int(pie_pct*100)),  fmt_clp(R['pie_clp'])),
            ("Gastos cierre",      fmt_clp(R['val_clp'] * gc_pct)),
            ("Capital total invertido", fmt_clp(R['cap_total'])),
            ("Monto hipotecario",  fmt_clp(R['hipot'])),
            ("Tasa mensual",       fmt_pct(tasa_h / 12)),
            ("Dividendo mensual",  fmt_clp(R['div_m'])),
            ("Dividendo anual",    fmt_clp(R['div_m'] * 12)),
            ("Arriendo bruto mes 1", fmt_clp(R['rent_m0'])),
            ("Flujo neto año 1",   fmt_clp(R['flujo_n'][1])),
            (f"Saldo hipoteca año {yr_venta}", fmt_clp(R['saldo_h'][yr_venta])),
            (f"Valor depto año {yr_venta}",    fmt_clp(R['val_d'][yr_venta])),
            ("Ganancia neta total", fmt_clp(R['gan_yr'])),
        ]
        rows_html = "".join(
            f'<tr><td style="color:#8a9bb0;font-size:0.8rem;padding:0.35rem 0">{k}</td>'
            f'<td style="text-align:right;font-weight:500;font-size:0.85rem;padding:0.35rem 0;'
            f'color:{"#00c9a7" if i >= len(info_rows)-3 else "#e8edf2"}">{v}</td></tr>'
            for i, (k, v) in enumerate(info_rows)
        )
        st.markdown(f'<table style="width:100%;border-collapse:collapse">{rows_html}</table>',
                    unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2: FLUJOS & PROYECCIONES
# ════════════════════════════════════════════════════════════════════════════
with tab2:

    # Chart 1: Depto vs ETF
    fig = go.Figure()
    gan_plot = [g for g in R['gan_v']]
    etf_plot = R['etf_b']

    fig.add_trace(go.Scatter(
        x=yrs[1:], y=[g/1e6 if g else None for g in gan_plot[1:]],
        name="Ganancia Neta Depto", line=dict(color=TEAL, width=2.5),
        fill="tozeroy", fillcolor="rgba(0,201,167,0.07)",
        hovertemplate="Año %{x} · Depto: $%{y:.1f}M<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=yrs[1:], y=[e/1e6 for e in etf_plot[1:]],
        name=f"ETF {etf_ret*100:.0f}% neto", line=dict(color=AMBER, width=2.5, dash="dash"),
        hovertemplate="Año %{x} · ETF: $%{y:.1f}M<extra></extra>",
    ))
    # Mark year of sale
    if yr_venta > 0 and R['gan_yr']:
        fig.add_vline(x=yr_venta, line=dict(color=SKY, dash="dot", width=1.5))
        fig.add_annotation(x=yr_venta, y=(R['gan_yr']/1e6), text=f"  Año {yr_venta}", showarrow=False,
                           font=dict(color=SKY, size=10), xanchor="left")

    fig.add_hline(y=0, line=dict(color="rgba(244,63,94,0.4)", width=1))
    layout = base_layout("Ganancia neta acumulada: Depto vs ETF (CLP millones)", height=380)
    layout['yaxis']['ticksuffix'] = "M"
    layout['yaxis']['title'] = dict(text="CLP millones", font=dict(size=10))
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    # Charts Row 2
    col_a, col_b = st.columns(2)

    with col_a:
        # Flujo neto anual bar
        colors_fn = [TEAL if f >= 0 else ROSE for f in R['flujo_n'][1:]]
        fig2 = go.Figure(go.Bar(
            x=yrs[1:], y=[f/1e6 for f in R['flujo_n'][1:]],
            marker_color=colors_fn,
            hovertemplate="Año %{x} · Flujo: $%{y:.2f}M<extra></extra>",
        ))
        fig2.add_hline(y=0, line=dict(color=FONT_COLOR, width=1))
        layout2 = base_layout("Flujo neto anual (CLP millones)", height=300)
        layout2['yaxis']['ticksuffix'] = "M"
        fig2.update_layout(**layout2)
        if R['yr_pos']:
            fig2.add_annotation(x=R['yr_pos'], y=0.05,
                                 text=f"Positivo año {R['yr_pos']}",
                                 showarrow=False, font=dict(color=TEAL, size=9), yref="paper")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        # Valor depto vs saldo hipoteca
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=yrs, y=[v/1e6 for v in R['val_d']],
            name="Valor depto", line=dict(color=TEAL, width=2),
            fill="tozeroy", fillcolor="rgba(0,201,167,0.05)",
        ))
        fig3.add_trace(go.Scatter(
            x=yrs, y=[s/1e6 for s in R['saldo_h']],
            name="Deuda banco", line=dict(color=ROSE, width=2, dash="dash"),
            fill="tozeroy", fillcolor="rgba(244,63,94,0.05)",
        ))
        layout3 = base_layout("Valor depto vs Deuda hipotecaria (CLP millones)", height=300)
        layout3['yaxis']['ticksuffix'] = "M"
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, use_container_width=True)

    # Full cash flow table
    st.markdown('<div class="section-title">Tabla completa de flujos año a año</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([3, 1])
    with col_t2:
        show_all = st.checkbox("Mostrar todos los años", value=False)

    display_yrs = yrs if show_all else [0] + list(range(1, min(16, 31)))

    rows = []
    for y in display_yrs:
        gan = R['gan_v'][y]
        etf_s = R['etf_b'][y] if y > 0 else None
        winner = ""
        if y > 0 and gan is not None and etf_s is not None:
            winner = "🏠 Depto" if gan > etf_s else "📈 ETF"
        rows.append({
            "Año": y,
            "Valor Depto": fmt_clp(R['val_d'][y]),
            "Arriendo Bruto": fmt_clp(R['arr_b'][y]) if y > 0 else "—",
            "Gastos Op.": fmt_clp(R['gastos'][y]) if y > 0 else "—",
            "Flujo Neto": fmt_clp(R['flujo_n'][y]),
            "Flujo Acum.": fmt_clp(R['flujo_a'][y]),
            "Saldo Hipoteca": fmt_clp(R['saldo_h'][y]),
            "Gan. Neta Venta": fmt_clp(gan) if y > 0 else "—",
            "ETF Base": fmt_clp(etf_s) if etf_s else "—",
            "¿Quién gana?": winner,
        })

    header_html = "<tr>" + "".join(f"<th>{k}</th>" for k in rows[0].keys()) + "</tr>"
    data_html = ""
    for r in rows:
        is_yr_venta = (r["Año"] == yr_venta)
        is_yr_pos   = (R['yr_pos'] and r["Año"] == R['yr_pos'])
        row_style = 'style="background:rgba(0,201,167,0.08)"' if is_yr_venta else (
                    'style="background:rgba(56,189,248,0.05)"' if is_yr_pos else "")
        data_html += f"<tr {row_style}>" + "".join(
            f'<td style="color:{"#00c9a7" if is_yr_venta else "#e8edf2"}">{v}</td>'
            for v in r.values()
        ) + "</tr>"

    st.markdown(
        f'<div style="overflow-x:auto"><table class="comp-table">{header_html}{data_html}</table></div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<p style="font-size:0.72rem;color:#8a9bb0;margin-top:0.5rem">🟢 Fila resaltada = año {yr_venta} (tu año de venta planificado)</p>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3: COMPARADOR
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p style="color:#8a9bb0;font-size:0.85rem">Configura hasta 5 propiedades distintas y compáralas en paralelo. La Simulación 1 toma los parámetros del panel lateral.</p>', unsafe_allow_html=True)

    n_sims = st.radio("¿Cuántas propiedades comparar?", [2, 3, 4, 5], horizontal=True, index=1)

    # Sim 1 = current params
    sim_params = [dict(params)]
    sim_names  = ["Sim 1 (actual)"]

    cols_sims = st.columns(n_sims - 1)
    for i, col in enumerate(cols_sims):
        idx = i + 2
        with col:
            st.markdown(f'<div class="section-title">Simulación {idx}</div>', unsafe_allow_html=True)
            name = st.text_input("Nombre", value=f"Propiedad {idx}", key=f"name_{idx}")
            dep_uf_i  = st.number_input("Valor (UF)", value=[4200, 6500, 3800, 7000][i], key=f"uf_{idx}", step=50)
            arr_clp_i = st.number_input("Arriendo (CLP/mes)", value=[876_000, 1_275_000, 797_000, 1_395_000][i], key=f"arr_{idx}", step=10_000, format="%d")
            arr_i     = arr_clp_i / uf_val
            plus_i    = st.number_input("Plusvalía %/año", value=[5.5, 7.5, 4.0, 5.5][i], key=f"plus_{idx}", step=0.5) / 100
            yr_v_i    = st.number_input("Año de venta", value=[10, 15, 8, 12][i], key=f"yrv_{idx}", min_value=1, max_value=30)
            tasa_i    = st.number_input("Tasa hipot. %", value=[4.2, 4.0, 3.8, 4.5][i], key=f"tasa_{idx}", step=0.01, format="%.2f") / 100
            sim_names.append(name)
            p_i = dict(params)
            p_i.update(val_uf=dep_uf_i, arriendo_uf=arr_i, plusvalia=plus_i,
                       yr_venta=yr_v_i, tasa=tasa_i)
            sim_params.append(p_i)

    results = [compute_simulation(p) for p in sim_params[:n_sims]]
    names   = sim_names[:n_sims]

    st.markdown('<div class="section-title" style="margin-top:2rem">Cuadro comparativo</div>', unsafe_allow_html=True)

    # Build comparison table
    metrics_comp = [
        ("Valor depto",           [fmt_clp(r['val_clp']) for r in results]),
        ("Capital invertido",     [fmt_clp(r['cap_total']) for r in results]),
        ("Dividendo mensual",     [fmt_clp(r['div_m']) for r in results]),
        ("Arriendo mes 1",        [fmt_clp(r['rent_m0']) for r in results]),
        ("Cap Rate neto año 1",   [fmt_pct(r['cap_rate_neto']) for r in results]),
        ("Plusvalía/año",         [fmt_pct(p['plusvalia']) for p in sim_params[:n_sims]]),
        ("Año de venta",          [str(r['yr_venta']) for r in results]),
        ("Valor depto al vender", [fmt_clp(r['val_d'][r['yr_venta']]) for r in results]),
        ("Saldo hipoteca al vender", [fmt_clp(r['saldo_h'][r['yr_venta']]) for r in results]),
        ("Ganancia Neta Total",   [fmt_clp(r['gan_yr']) for r in results]),
        ("ROI sobre capital",     [f"{r['roi']:.2f}x" if r['roi'] else "—" for r in results]),
        ("CAGR anual",            [fmt_pct(r['cagr']) for r in results]),
        ("ETF equivalente",       [fmt_clp(r['etf_yr']) for r in results]),
    ]

    best_gan_idx = max(range(n_sims), key=lambda i: results[i]['gan_yr'] or -1e18)
    best_roi_idx = max(range(n_sims), key=lambda i: results[i]['roi'] or -1e18)

    th = "".join(f"<th>{n}</th>" for n in names)
    header_html = f"<tr><th>Indicador</th>{th}</tr>"
    rows_html = ""
    for label, vals in metrics_comp:
        is_gan = label == "Ganancia Neta Total"
        is_roi = label == "ROI sobre capital"
        tds = ""
        for i, v in enumerate(vals):
            is_winner = (is_gan and i == best_gan_idx) or (is_roi and i == best_roi_idx)
            tds += f'<td style="color:{"#00c9a7" if is_winner else "#e8edf2"};font-weight:{"700" if is_winner else "400"}">'
            tds += f'{"🏆 " if is_winner else ""}{v}</td>'
        rows_html += f"<tr><td style='color:#8a9bb0;font-size:0.8rem'>{label}</td>{tds}</tr>"

    st.markdown(
        f'<div style="overflow-x:auto"><table class="comp-table">{header_html}{rows_html}</table></div>',
        unsafe_allow_html=True
    )

    # Ganancia neta bar comparison
    fig_comp = go.Figure()
    colors_c = [TEAL, AMBER, SKY, PURPLE, ROSE]
    gans_comp = [r['gan_yr'] or 0 for r in results]
    fig_comp.add_trace(go.Bar(
        x=names, y=[g/1e6 for g in gans_comp],
        marker_color=[colors_c[i] for i in range(n_sims)],
        text=[fmt_clp(g) for g in gans_comp],
        textposition="outside",
        textfont=dict(size=10),
        hovertemplate="%{x}: $%{y:.1f}M<extra></extra>",
    ))
    layout_c = base_layout("Ganancia neta total por propiedad (CLP millones)", height=340)
    layout_c['yaxis']['ticksuffix'] = "M"
    layout_c['showlegend'] = False
    fig_comp.update_layout(**layout_c)
    st.plotly_chart(fig_comp, use_container_width=True)

    # Ganancia acumulada curves
    fig_lines = go.Figure()
    for i, (r, name) in enumerate(zip(results, names)):
        fig_lines.add_trace(go.Scatter(
            x=yrs[1:], y=[g/1e6 if g else None for g in r['gan_v'][1:]],
            name=name, line=dict(color=colors_c[i], width=2),
            hovertemplate=f"{name} Año %{{x}}: $%{{y:.1f}}M<extra></extra>",
        ))
    fig_lines.add_hline(y=0, line=dict(color="rgba(255,255,255,0.15)", width=1))
    layout_l = base_layout("Evolución ganancia neta acumulada — todas las simulaciones", height=360)
    layout_l['yaxis']['ticksuffix'] = "M"
    fig_lines.update_layout(**layout_l)
    st.plotly_chart(fig_lines, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4: GUÍA DE INDICADORES
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p style="color:#8a9bb0;font-size:0.85rem;margin-bottom:1.2rem">Guía para entender cada indicador del simulador y cómo interpretarlo para tomar mejores decisiones.</p>', unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown('<div class="section-title">Inputs críticos — qué significan</div>', unsafe_allow_html=True)
        guide_inputs = [
            ("📐 Plusvalía nominal/año", f"Tu zona: {plusvalia*100:.1f}%",
             "El motor principal de rentabilidad. Mide cuánto sube el valor del depto anualmente. "
             "Con crédito hipotecario, la plusvalía actúa sobre el 100% del depto pero tú solo pusiste el pie — "
             "esto se llama apalancamiento financiero y multiplica tu retorno sobre capital propio."),
            ("🏘️ Cap Rate neto", f"Tu caso: {R['cap_rate_neto']*100:.2f}%",
             "Arriendo neto anual ÷ valor del depto. Mide si el depto 'se paga solo' operacionalmente. "
             "Benchmark RM: 2%–4% neto. Menor a 2% = vives de la plusvalía, no del arriendo. "
             "Mayor a 4% = excelente operación."),
            ("📉 Vacancia", f"Usas: {vacancia*100:.0f}%",
             "Porcentaje del año sin arrendatario. 8% ≈ 1 mes sin ingresos. "
             "Zonas consolidadas: 5%–8%. Zonas emergentes o mal gestionadas: 10%–20%. "
             "Impacta directamente el flujo y el punto de equilibrio."),
            ("📈 Crecimiento arriendo", f"Usas: {rent_gr*100:.1f}%/año",
             "A qué ritmo suben los arriendos. Históricamente RM: 4%–6% nominal (incluye IPC). "
             "Afecta directamente cuándo el flujo se vuelve positivo. "
             "Con menor crecimiento, necesitas más años para compensar el dividendo."),
            ("🏦 Tasa hipotecaria", f"Usas: {tasa_h*100:.2f}% anual",
             f"Define tu dividendo mensual de {fmt_clp(R['div_m'])}. "
             "A mayor tasa, mayor flujo negativo los primeros años y menor rentabilidad total. "
             "Negociar la tasa puede cambiar significativamente el resultado."),
        ]
        for name, value, desc in guide_inputs:
            st.markdown(f"""
            <div class="guide-card">
              <div class="guide-name">{name} <span class="badge badge-amber">{value}</span></div>
              <div class="guide-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="section-title">Indicadores de resultado — cómo leerlos</div>', unsafe_allow_html=True)
        gan_str = fmt_clp(R['gan_yr'])
        roi_str = f"{R['roi']:.2f}x" if R['roi'] else "—"
        cap_str = fmt_pct(R['cap_rate_neto'])

        guide_outputs = [
            ("💰 Ganancia Neta de Venta", f"Tu caso año {yr_venta}: {gan_str}",
             "LA MÉTRICA MÁS IMPORTANTE. Es lo que queda en tu bolsillo al vender: "
             "precio de venta − deuda banco − costos de venta + todos los flujos acumulados. "
             "Incluye todo: plusvalía, arriendos cobrados y dividendos pagados."),
            ("🔄 ROI (Return on Investment)", f"Tu caso: {roi_str}",
             "Ganancia neta ÷ capital propio invertido. ROI de 2x = duplicaste tu inversión. "
             "El apalancamiento hace que el ROI sobre capital propio sea MUCHO mayor que la plusvalía del depto. "
             "Referencia: ROI > 2x a 10 años es excelente."),
            ("📊 Flujo Neto Anual", f"Año 1: {fmt_clp(R['flujo_n'][1])}",
             "Arriendo − Gastos − Dividendo. Si es negativo, pones dinero de tu bolsillo mensualmente. "
             "Normal tener flujo negativo los primeros años. " +
             (f"En tu caso se vuelve positivo en el año {R['yr_pos']}." if R['yr_pos'] else "En tu escenario el flujo no llega a positivo en 30 años.")),
            ("🏦 vs ETF", f"Diferencia año {yr_venta}: {fmt_clp(diff)}",
             f"Compara el depto con invertir el mismo dinero (pie + subsidio mensual) en ETF al {etf_ret*100:.0f}% neto. "
             "La comparación es JUSTA porque ambas alternativas cuestan lo mismo de tu bolsillo. "
             "El depto gana a largo plazo gracias al apalancamiento."),
            ("⚖️ Cuándo conviene vender", "",
             "Matemáticamente: cuando la Ganancia Neta Depto supera el saldo ETF. "
             "Prácticamente: no antes del año 7–8, cuando la plusvalía acumulada empieza a superar el costo total. "
             "El apalancamiento funciona mejor mientras más tiempo pasa."),
        ]
        for name, value, desc in guide_outputs:
            badge = f'<span class="badge badge-green">{value}</span>' if value else ""
            st.markdown(f"""
            <div class="guide-card">
              <div class="guide-name">{name} {badge}</div>
              <div class="guide-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    # Decision framework
    st.markdown('<div class="section-title" style="margin-top:1.5rem">Marco de decisión — semáforo de la inversión</div>', unsafe_allow_html=True)
    c_s1, c_s2, c_s3 = st.columns(3)

    with c_s1:
        st.markdown("""
        <div class="verdict verdict-win">
          <b style="color:#00c9a7">✅ BUENA inversión si...</b><br><br>
          <span style="font-size:0.82rem;color:#8a9bb0">
          • Plusvalía zona ≥ 5.5%<br>
          • Arriendo ≥ 0.45% del precio/mes<br>
          • Cap Rate neto > 2.5%<br>
          • Flujo positivo antes del año 12<br>
          • TIR proyectada > 8%<br>
          • Depto supera ETF en año 10
          </span>
        </div>""", unsafe_allow_html=True)

    with c_s2:
        st.markdown("""
        <div class="verdict verdict-warn">
          <b style="color:#f59e0b">⚠️ REVISAR si...</b><br><br>
          <span style="font-size:0.82rem;color:#8a9bb0">
          • Plusvalía entre 3%–5%<br>
          • Arriendo < 0.40% del precio<br>
          • Flujo negativo por más de 15 años<br>
          • Depto solo supera ETF después del año 20<br>
          • Tasa hipotecaria > 5.5%<br>
          • Vacancia esperada > 12%
          </span>
        </div>""", unsafe_allow_html=True)

    with c_s3:
        st.markdown("""
        <div class="verdict verdict-lose">
          <b style="color:#f43f5e">❌ MALA inversión si...</b><br><br>
          <span style="font-size:0.82rem;color:#8a9bb0">
          • Plusvalía < 3%<br>
          • Cap Rate neto < 1.5%<br>
          • Flujo nunca positivo en 30 años<br>
          • Ganancia Neta < saldo ETF a año 30<br>
          • TIR < tasa del crédito<br>
          • Arriendo < 0.35% del precio
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="guide-card" style="margin-top:1rem;border-left:3px solid #00c9a7">
      <div class="guide-name">💡 La clave: el depto es una apuesta a la PLUSVALÍA, no al arriendo</div>
      <div class="guide-desc">
      El banco financia el 80% del depto, pero el 100% de la plusvalía es tuya. Con 5.5% nominal de plusvalía anual, 
      un depto de $200M sube $11M/año — pero tú solo pusiste $44M de capital propio, así que en términos de ROI 
      sobre tu inversión ganaste 25% solo en valorización. Ese efecto (apalancamiento financiero) es la razón por la 
      que el depto puede superar al ETF a largo plazo, a pesar de los flujos negativos iniciales y el riesgo de gestión.
      </div>
    </div>""", unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;border-top:1px solid rgba(61,81,102,0.4);padding-top:1rem;text-align:center">
  <p style="font-size:0.72rem;color:#8a9bb0">
    Simulador educativo · Valores en CLP nominales · No constituye asesoría financiera<br>
    Fuentes: SII, CMF, BCCh · Benchmark RM basado en datos históricos 2015–2024
  </p>
</div>
""", unsafe_allow_html=True)