import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from datetime import datetime

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

section[data-testid="stSidebar"] {
    background: var(--ink);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .stSlider > div > div > div { background: var(--teal) !important; }

.main .block-container {
    background: var(--navy);
    padding-top: 1.5rem;
    max-width: 1400px;
}

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

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
    font-size: 1.35rem;
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

.verdict {
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    margin: 1rem 0;
    border: 1px solid;
}
.verdict-win  { background: rgba(0,201,167,0.08);  border-color: rgba(0,201,167,0.3); }
.verdict-warn { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.3); }
.verdict-lose { background: rgba(244,63,94,0.08);  border-color: rgba(244,63,94,0.3);  }

.guide-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.guide-name { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.3rem; }
.guide-desc { font-size: 0.82rem; color: var(--muted); line-height: 1.5; }

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

div[data-testid="stNumberInput"] input {
    background: var(--slate);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 6px;
}

hr { border-color: var(--border); }
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ────────────────────────────────────────────────────────────────
def fmt_clp(v, decimals=0):
    """Número completo con separadores de miles."""
    if v is None: return "—"
    neg = v < 0
    s = f"${abs(v):,.{decimals}f}"
    return f"({s})" if neg else s

def fmt_clp_short(v):
    """Número abreviado para KPI cards."""
    if v is None: return "—"
    neg = v < 0
    a = abs(v)
    if a >= 1_000_000_000:   s = f"${a/1e9:.2f}B"
    elif a >= 1_000_000:     s = f"${a/1e6:.1f}M"
    elif a >= 1_000:         s = f"${a/1e3:.0f}K"
    else:                    s = f"${a:,.0f}"
    return f"({s})" if neg else s

def fmt_pct(v):
    if v is None: return "—"
    return f"{v*100:.1f}%"


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


# ─── TIR ─────────────────────────────────────────────────────────────────────
def calcular_tir(flujos, max_iter=1000, tol=1e-6):
    if len(flujos) < 2: return None
    tasa = 0.1
    for _ in range(max_iter):
        vpn  = sum(f / (1+tasa)**i for i, f in enumerate(flujos))
        dvpn = sum(-i*f / (1+tasa)**(i+1) for i, f in enumerate(flujos))
        if abs(dvpn) < 1e-10: break
        nueva = tasa - vpn / dvpn
        if abs(nueva - tasa) < tol:
            return nueva if -0.5 < nueva < 5 else None
        tasa = nueva
    return None


# ─── MOTOR DE CÁLCULO ────────────────────────────────────────────────────────
def compute_simulation(p):
    uf       = p['uf']
    val_uf   = p['val_uf']
    val_clp  = uf * val_uf
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
    val_d, arr_b, gastos   = [], [], []
    flujo_n, flujo_a       = [], []
    saldo_h, gan_v, etf_b  = [], [], []
    interes_anual, amort_anual = [], []

    deficit_acum = -cap_total
    etf_saldo    = cap_total

    for yr in years:
        vd = val_clp * (1 + p['plusvalia']) ** yr
        val_d.append(vd)

        if yr == 0:
            arr_b.append(0); gastos.append(0)
            flujo_n.append(-cap_total); flujo_a.append(-cap_total)
            saldo_h.append(hipot); gan_v.append(None); etf_b.append(cap_total)
            interes_anual.append(0); amort_anual.append(0)
            continue

        rent_anual   = rent_m0 * 12 * (1 + p['rent_gr']) ** (yr - 1)
        arr_b.append(rent_anual)

        # Gastos — gcom, contrib, seguro ya vienen en CLP
        vac_loss   = rent_anual * p['vacancia']
        adm_loss   = rent_anual * p['adm']
        res_loss   = rent_anual * p['reserva']
        gcom_anual = p['gcom'] * 12
        cont_anual = p['contrib']
        seg_anual  = p['seguro']
        mant_anual = vd * p['mant']
        remo       = uf * p['remodelaciones'].get(yr, 0)

        gast = vac_loss + adm_loss + res_loss + gcom_anual + cont_anual + seg_anual + mant_anual + remo
        gastos.append(gast)

        fn = rent_anual - gast - div_m * 12
        flujo_n.append(fn)
        deficit_acum += fn
        flujo_a.append(deficit_acum)

        # Amortización e interés
        sh_prev    = saldo_h[-1]
        interes_yr = sh_prev * tasa_m * 12 if tasa_m > 0 else 0
        amort_yr   = div_m * 12 - interes_yr
        interes_anual.append(max(0, interes_yr))
        amort_anual.append(max(0, amort_yr))

        if tasa_m > 0:
            sh = hipot * (1 + tasa_m) ** (yr * 12) - div_m * ((1 + tasa_m) ** (yr * 12) - 1) / tasa_m
        else:
            sh = max(0, hipot - div_m * yr * 12)
        saldo_h.append(max(0, sh))

        costo_vta = vd * p['costo_venta']
        gan_v.append(vd - max(0, sh) - costo_vta + deficit_acum)

        subsidio_mes = max(0, div_m - (rent_anual / 12) * (1 - p['vacancia'] - p['adm'] - p['reserva']) +
                          (gcom_anual + cont_anual + seg_anual) / 12 + mant_anual / 12)
        etf_saldo = etf_saldo * (1 + p['etf_ret']) + subsidio_mes * 12
        etf_b.append(etf_saldo)

    cap_rate_neto = (rent_m0 * 12 * (1 - p['vacancia'] - p['adm'] - p['reserva']) -
                     (p['gcom'] * 12 + p['contrib'] + p['seguro']) -
                     val_clp * p['mant']) / val_clp

    yr_venta = p['yr_venta']
    gan_yr   = gan_v[yr_venta] if yr_venta > 0 else None
    roi      = (gan_yr / cap_total) if (gan_yr and cap_total > 0) else None
    cagr     = ((gan_yr / cap_total) ** (1 / yr_venta) - 1) if (gan_yr and gan_yr > 0 and yr_venta > 0) else None
    etf_yr   = etf_b[yr_venta]
    yr_pos   = next((i for i in range(1, 31) if flujo_n[i] > 0), None)

    # TIR
    flujos_tir = [-cap_total]
    for i in range(1, yr_venta + 1):
        f = flujo_n[i]
        if i == yr_venta:
            liq = val_d[i] - saldo_h[i] - val_d[i] * p['costo_venta']
            f   = flujo_n[i] + liq
        flujos_tir.append(f)
    tir = calcular_tir(flujos_tir)

    return {
        'years': years, 'val_d': val_d, 'arr_b': arr_b, 'gastos': gastos,
        'flujo_n': flujo_n, 'flujo_a': flujo_a,
        'saldo_h': saldo_h, 'gan_v': gan_v, 'etf_b': etf_b,
        'interes_anual': interes_anual, 'amort_anual': amort_anual,
        'cap_total': cap_total, 'val_clp': val_clp,
        'pie_clp': pie_clp, 'hipot': hipot, 'div_m': div_m,
        'rent_m0': rent_m0, 'cap_rate_neto': cap_rate_neto,
        'gan_yr': gan_yr, 'roi': roi, 'cagr': cagr, 'tir': tir,
        'etf_yr': etf_yr, 'yr_pos': yr_pos, 'yr_venta': yr_venta,
    }


# ─── GENERADOR PDF ───────────────────────────────────────────────────────────
def generar_pdf(R, params, zona_key, arr_clp, tasa_h, plusvalia, yr_venta, etf_ret):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable, KeepTogether)

    buf = io.BytesIO()
    # Usamos landscape A4 para que la tabla de flujos quepa sin cortes
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)

    PAGE_W = 27.7*cm  # ancho util landscape A4

    C_DARK  = colors.HexColor('#0f1923')
    C_TEAL  = colors.HexColor('#00c9a7')
    C_AMBER = colors.HexColor('#f59e0b')
    C_ROSE  = colors.HexColor('#f43f5e')
    C_MUTED = colors.HexColor('#8a9bb0')
    C_LIGHT = colors.HexColor('#f0f4f8')
    C_WHITE = colors.white
    C_BDR   = colors.HexColor('#d1dce8')
    C_VENTA = colors.HexColor('#003d32')

    title_s   = ParagraphStyle('t',  fontSize=16, fontName='Helvetica-Bold', textColor=C_DARK,  spaceAfter=3)
    sub_s     = ParagraphStyle('s',  fontSize=8,  fontName='Helvetica',      textColor=C_MUTED, spaceAfter=8)
    section_s = ParagraphStyle('sc', fontSize=9,  fontName='Helvetica-Bold', textColor=C_TEAL,  spaceBefore=10, spaceAfter=4)
    small_s   = ParagraphStyle('sm', fontSize=6.5,fontName='Helvetica',      textColor=C_MUTED, spaceAfter=2)
    label_s   = ParagraphStyle('lb', fontSize=7,  fontName='Helvetica-Bold', textColor=C_DARK)

    def tbl_style_base(header_bg=C_DARK, font_size=8, padding=4):
        return [
            ('BACKGROUND',   (0,0), (-1,0),  header_bg),
            ('TEXTCOLOR',    (0,0), (-1,0),  C_WHITE),
            ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',     (0,0), (-1,-1), font_size),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),  [C_LIGHT, C_WHITE]),
            ('GRID',         (0,0), (-1,-1), 0.4, C_BDR),
            ('PADDING',      (0,0), (-1,-1), padding),
            ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN',        (1,0), (-1,-1), 'RIGHT'),
            ('ALIGN',        (0,0), (0,-1),  'LEFT'),
        ]

    story = []

    # ── ENCABEZADO ──
    story.append(Paragraph("Simulador de Inversion Inmobiliaria", title_s))
    story.append(Paragraph(
        f"Region Metropolitana  |  Zona {zona_key}  |  Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Desarrollado por Alonso Tapia D.",
        sub_s))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_TEAL, spaceAfter=8))

    # ── BLOQUE SUPERIOR: Parametros + KPIs lado a lado ──
    gan   = R['gan_yr']; tir = R['tir']; roi = R['roi']
    diff  = (gan or 0) - R['etf_yr']
    verdict = ("BUENA INVERSION" if (gan and diff>0 and roi and roi>=1.5)
               else ("REVISAR" if (gan and diff>=0) else "ETF GANA"))
    v_color = C_TEAL if "BUENA" in verdict else (C_AMBER if "REVISAR" in verdict else C_ROSE)

    # Parametros (izquierda)
    inp_data = [
        [Paragraph("PARAMETROS DE ENTRADA", label_s), "", "", ""],
        ["Valor depto",      fmt_clp(R['val_clp']),    "Arriendo inicial",  fmt_clp(arr_clp)+"/mes"],
        [f"Pie ({int(params['pie']*100)}%)", fmt_clp(R['pie_clp']), "Hipotecario", fmt_clp(R['hipot'])],
        ["Tasa hipotecaria", fmt_pct(tasa_h),          "Dividendo mensual", fmt_clp(R['div_m'])],
        ["Plazo credito",    f"{params['plazo']} anos",  "Capital invertido", fmt_clp(R['cap_total'])],
        ["Plusvalia zona",   fmt_pct(plusvalia),        "Ano de venta",      str(yr_venta)],
        ["Vacancia",         fmt_pct(params['vacancia']), "ETF comparacion",  fmt_pct(etf_ret)],
        ["Crecim. arriendo", fmt_pct(params['rent_gr']), "Flujo + desde ano", str(R['yr_pos']) if R['yr_pos'] else "No alcanza"],
    ]
    col_inp = PAGE_W * 0.48
    t_inp = Table(inp_data, colWidths=[col_inp*0.38, col_inp*0.28, col_inp*0.34*0.9, col_inp*0.34*1.1])
    st_inp = tbl_style_base(font_size=7.5, padding=3.5)
    st_inp += [
        ('SPAN',        (0,0), (-1,0)),
        ('ALIGN',       (0,0), (-1,0), 'LEFT'),
        ('BACKGROUND',  (0,0), (-1,0), colors.HexColor('#1a2332')),
        ('FONTNAME',    (1,1), (1,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (3,1), (3,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (1,1), (1,-1), C_DARK),
        ('TEXTCOLOR',   (3,1), (3,-1), C_DARK),
    ]
    t_inp.setStyle(TableStyle(st_inp))

    # KPIs (derecha)
    kpi_data = [
        [Paragraph("INDICADORES CLAVE", label_s), "", ""],
        ["Ganancia Neta Total",    fmt_clp(gan),                   "Precio - Deuda - Costos + Flujos"],
        ["ROI sobre capital",      f"{roi:.2f}x" if roi else "-",  "Bueno > 2x a 10 anos"],
        ["TIR",                    fmt_pct(tir) if tir else "-",   f"Bueno > 8% | Tasa credito: {fmt_pct(tasa_h)}"],
        ["CAGR anual",             fmt_pct(R['cagr']),              "Rentabilidad compuesta anual"],
        ["Cap Rate neto ano 1",    fmt_pct(R['cap_rate_neto']),     "Benchmark RM: 2%-4%"],
        [f"vs ETF {fmt_pct(etf_ret)}", fmt_clp(diff),             "Diferencia a favor del depto"],
        [f"Valor depto ano {yr_venta}", fmt_clp(R['val_d'][yr_venta]), f"Con plusvalia {fmt_pct(plusvalia)}"],
        ["Saldo hipoteca al vender", fmt_clp(R['saldo_h'][yr_venta]), "Deuda pendiente con banco"],
    ]
    col_kpi = PAGE_W * 0.48
    t_kpi = Table(kpi_data, colWidths=[col_kpi*0.38, col_kpi*0.28, col_kpi*0.34])
    st_kpi = tbl_style_base(font_size=7.5, padding=3.5)
    st_kpi += [
        ('SPAN',       (0,0), (-1,0)),
        ('ALIGN',      (0,0), (-1,0), 'LEFT'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a2332')),
        ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',  (0,1), (0,-1), C_DARK),
    ]
    t_kpi.setStyle(TableStyle(st_kpi))

    # Veredicto
    verd_data = [[Paragraph(f"VEREDICTO: {verdict}", ParagraphStyle('v', fontSize=9, fontName='Helvetica-Bold', textColor=C_WHITE))]]
    t_verd = Table(verd_data, colWidths=[col_kpi])
    t_verd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), v_color),
        ('PADDING',    (0,0), (-1,-1), 6),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
    ]))

    # Combinar en dos columnas
    bloque_sup = Table(
        [[t_inp, Spacer(0.04*PAGE_W, 1), t_kpi]],
        colWidths=[PAGE_W*0.48, PAGE_W*0.04, PAGE_W*0.48]
    )
    bloque_sup.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(KeepTogether([bloque_sup]))

    # Veredicto a ancho completo
    story.append(Spacer(1, 4))
    t_verd2 = Table([[Paragraph(f"  VEREDICTO: {verdict}", ParagraphStyle('v2', fontSize=10, fontName='Helvetica-Bold', textColor=C_WHITE))]],
                    colWidths=[PAGE_W])
    t_verd2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), v_color),
        ('PADDING',    (0,0), (-1,-1), 7),
    ]))
    story.append(t_verd2)
    story.append(Spacer(1, 8))

    # ── TABLA FLUJOS CLAVE ──
    story.append(Paragraph("FLUJOS ANOS CLAVE", section_s))
    key_yrs = sorted(set([1,3,5,7,10,12,15,20,25,30,yr_venta]))
    key_yrs = [y for y in key_yrs if y <= 30]

    # Encabezados con saltos de linea para que quepan
    fl_hdr = ["Ano", "Valor\nDepto", "Arr.\nBruto", "Gastos\nOp.", "Flujo\nNeto", "Flujo\nAcum.", "Gan.Neta\nVenta", "Saldo\nHipoteca", "ETF\nBase", "Quien\ngana"]
    fl = [fl_hdr]
    for y in key_yrs:
        g  = R['gan_v'][y] if y > 0 else None
        e  = R['etf_b'][y] if y > 0 else None
        winner = ""
        if g is not None and e is not None:
            winner = "Depto" if g > e else "ETF"
        fl.append([
            str(y)+("*" if y==yr_venta else ""),
            fmt_clp(R['val_d'][y]),
            fmt_clp(R['arr_b'][y])    if y>0 else "-",
            fmt_clp(R['gastos'][y])   if y>0 else "-",
            fmt_clp(R['flujo_n'][y]),
            fmt_clp(R['flujo_a'][y]),
            fmt_clp(g)                 if g is not None else "-",
            fmt_clp(R['saldo_h'][y]),
            fmt_clp(e)                 if e is not None else "-",
            winner,
        ])

    # Anchos calculados para que todo quepa en PAGE_W
    cw = [1.0*cm, 3.1*cm, 2.8*cm, 2.8*cm, 2.8*cm, 3.0*cm, 3.1*cm, 3.1*cm, 3.0*cm, 1.8*cm]
    t3 = Table(fl, colWidths=cw, repeatRows=1)
    s3 = tbl_style_base(font_size=7, padding=3)
    s3 += [('FONTSIZE', (0,0), (-1,0), 6.5),
           ('ALIGN',    (0,0), (0,-1), 'CENTER'),
           ('ALIGN',    (-1,0),(-1,-1),'CENTER')]
    for i, y in enumerate(key_yrs):
        if y == yr_venta:
            s3 += [('BACKGROUND', (0,i+1), (-1,i+1), C_VENTA),
                   ('TEXTCOLOR',  (0,i+1), (-1,i+1), C_TEAL),
                   ('FONTNAME',   (0,i+1), (-1,i+1), 'Helvetica-Bold')]
    t3.setStyle(TableStyle(s3))
    story.append(t3)
    story.append(Spacer(1, 3))
    story.append(Paragraph("* Ano de venta planificado  |  Flujos negativos en parentesis  |  Valores en CLP nominales", small_s))
    story.append(Spacer(1, 8))

    # ── SENSIBILIDAD ──
    story.append(Paragraph("ANALISIS DE SENSIBILIDAD A LA PLUSVALIA", section_s))
    pvs = [plusvalia-0.02, plusvalia-0.01, plusvalia, plusvalia+0.01, plusvalia+0.02]
    pvs = [p for p in pvs if 0 < p <= 0.15]

    sens_hdr = ["Plusvalia/ano", "Valor depto", "Ganancia Neta", "ROI", "TIR", "vs ETF", "Resultado"]
    sens = [sens_hdr]
    for pv in pvs:
        r2  = compute_simulation(dict(params, plusvalia=pv))
        g2  = r2['gan_yr']; d2 = (g2 or 0) - r2['etf_yr']
        ib  = abs(pv - plusvalia) < 0.001
        res = ("Buena" if (g2 and d2>0 and r2['roi'] and r2['roi']>=1.5)
               else ("Revisar" if (g2 and d2>=0) else "ETF gana"))
        roi2 = r2['roi']; tir2 = r2['tir']
        sens.append([
            fmt_pct(pv) + (" (base)" if ib else ""),
            fmt_clp(r2['val_d'][yr_venta]),
            fmt_clp(g2),
            f"{roi2:.2f}x" if roi2 else "-",
            fmt_pct(tir2) if tir2 else "-",
            fmt_clp(d2),
            res,
        ])

    cw_s = [3.2*cm, 3.8*cm, 3.8*cm, 2.0*cm, 2.0*cm, 3.5*cm, 3.0*cm]
    t4 = Table(sens, colWidths=cw_s, repeatRows=1)
    st4 = tbl_style_base(font_size=8, padding=4)
    # Resaltar fila base
    for i, pv in enumerate(pvs):
        if abs(pv - plusvalia) < 0.001:
            st4 += [('BACKGROUND', (0,i+1), (-1,i+1), colors.HexColor('#e8f8f5')),
                    ('FONTNAME',   (0,i+1), (-1,i+1), 'Helvetica-Bold'),
                    ('TEXTCOLOR',  (0,i+1), (-1,i+1), C_DARK)]
    t4.setStyle(TableStyle(st4))
    story.append(KeepTogether([t4]))

    # ── PIE DE PAGINA ──
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BDR))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "Simulador educativo  |  Valores en CLP nominales  |  No constituye asesoria financiera  |  "
        "Desarrollado por Alonso Tapia D.  |  Fuentes: SII, CMF, BCCh",
        small_s))

    doc.build(story)
    buf.seek(0)
    return buf.read()



# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:Syne;font-size:1.3rem;font-weight:800;color:#00c9a7;margin-bottom:0">🏢 SIMULADOR</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.72rem;color:#8a9bb0;letter-spacing:0.1em;text-transform:uppercase;margin-top:0">Inversión Inmobiliaria RM</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.68rem;color:#3d5166;margin-top:0.2rem;margin-bottom:0">Desarrollado por</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.78rem;color:#00c9a7;font-weight:600;margin-top:0rem;letter-spacing:0.03em">Alonso Tapia D.</p>', unsafe_allow_html=True)
    st.divider()

    # ── Escenarios rápidos ──
    st.markdown('<div class="section-title">Escenario Rápido</div>', unsafe_allow_html=True)
    col_s1, col_s2, col_s3 = st.columns(3)
    escenario = None
    with col_s1:
        if st.button("🐢 Cons.", use_container_width=True): escenario = "conservador"
    with col_s2:
        if st.button("📊 Base",  use_container_width=True): escenario = "base"
    with col_s3:
        if st.button("🚀 Opt.",  use_container_width=True): escenario = "optimista"

    esc_vals = {
        "conservador": dict(dep_uf=4000, arr_clp=900_000,   plus=3.0, tasa=4.5, vac=12.0, rent_gr=3.0),
        "base":        dict(dep_uf=5000, arr_clp=1_035_000, plus=5.5, tasa=4.0, vac=8.0,  rent_gr=4.0),
        "optimista":   dict(dep_uf=6000, arr_clp=1_400_000, plus=7.5, tasa=3.5, vac=5.0,  rent_gr=6.0),
    }
    ev = esc_vals.get(escenario, esc_vals["base"])

    st.divider()
    st.markdown('<div class="section-title">Datos del Departamento</div>', unsafe_allow_html=True)
    uf_val   = st.number_input("Valor UF (CLP)", value=39842, step=100, format="%d")
    dep_uf   = st.number_input("Valor depto (UF)", value=ev['dep_uf'], step=50, format="%d")
    arr_clp  = st.number_input("Arriendo inicial (CLP/mes)", value=ev['arr_clp'], step=10_000, format="%d")
    arr_uf   = arr_clp / uf_val
    st.markdown(f'<p style="font-size:0.72rem;color:#8a9bb0;margin-top:-0.5rem">≈ {arr_uf:.1f} UF/mes (referencial)</p>', unsafe_allow_html=True)
    rent_gr  = st.slider("Crecimiento arriendo anual", 2.0, 8.0, float(ev['rent_gr']), 0.5, format="%.1f%%") / 100
    vacancia = st.slider("Vacancia anual", 0.0, 20.0, float(ev['vac']), 1.0, format="%.0f%%") / 100
    adm      = st.slider("Comisión administradora", 0.0, 15.0, 8.0, 1.0, format="%.0f%%") / 100
    gcom     = st.number_input("Gastos comunes (CLP/mes)", value=100_000, step=5_000, format="%d")
    contrib  = st.number_input("Contribuciones SII (CLP/año)", value=320_000, step=10_000, format="%d")
    seguro   = st.number_input("Seguro hipotecario (CLP/año)", value=120_000, step=5_000, format="%d")
    mant     = st.slider("Mantención anual (% valor)", 0.1, 2.0, 0.5, 0.1, format="%.1f%%") / 100
    reserva  = st.slider("Reserva contingencias (% arr.)", 0.0, 10.0, 5.0, 1.0, format="%.0f%%") / 100

    st.divider()
    st.markdown('<div class="section-title">Financiamiento</div>', unsafe_allow_html=True)
    pie_pct  = st.number_input("Pie inicial (%)", value=20.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f") / 100
    tasa_h   = st.number_input("Tasa hipotecaria anual (%)", value=float(ev['tasa']), min_value=0.0, max_value=30.0, step=0.01, format="%.2f") / 100
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
        plusvalia = st.slider("Plusvalía nominal/año", 1.0, 10.0, float(ev['plus']), 0.5, format="%.1f%%") / 100
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
R      = compute_simulation(params)
yrs    = R['years']
gan    = R['gan_yr']
etf    = R['etf_yr']
diff   = (gan or 0) - etf
roi    = R['roi']
cagr   = R['cagr']
tir    = R['tir']
yr_pos = R['yr_pos']


# ─── HEADER ──────────────────────────────────────────────────────────────────
col_header, col_pdf_btn = st.columns([4, 1])
with col_header:
    st.markdown(f"""
    <div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:0.3rem">
      <h1 style="font-family:Syne;font-size:2rem;font-weight:800;color:#e8edf2;margin:0">Simulador Inversión Inmobiliaria</h1>
      <span class="badge badge-amber">Región Metropolitana · Chile</span>
    </div>
    <p style="color:#8a9bb0;font-size:0.85rem;margin-bottom:0.8rem">
      Depto de <b style="color:#e8edf2">{dep_uf:,} UF</b> · ${R['val_clp']:,.0f} CLP ·
      Arriendo <b style="color:#e8edf2">${arr_clp:,.0f}/mes</b> · Zona {zona_key} ·
      Vendiendo en año <b style="color:#00c9a7">{yr_venta}</b>
    </p>
    """, unsafe_allow_html=True)

with col_pdf_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📄 Exportar PDF", use_container_width=True):
        with st.spinner("Generando reporte..."):
            pdf_bytes = generar_pdf(R, params, zona_key, arr_clp, tasa_h, plusvalia, yr_venta, etf_ret)
        st.download_button(
            label="⬇️ Descargar PDF",
            data=pdf_bytes,
            file_name=f"simulacion_{dep_uf}UF_ano{yr_venta}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Dashboard", "📈  Flujos & Proyecciones", "📉  Sensibilidad", "🔁  Comparador", "📖  Guía de Indicadores"
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── KPI Row 1 ──
    k1, k2, k3, k4, k5 = st.columns(5)
    subsidio_m = max(0, R['div_m'] - R['rent_m0']*(1-vacancia-adm-reserva) +
                     ((gcom+(contrib+seguro)/12) + R['val_clp']*mant/12))
    metrics_row1 = [
        (k1, "Capital invertido",    fmt_clp_short(R['cap_total']), fmt_clp(R['cap_total']),      ""),
        (k2, "Dividendo mensual",    fmt_clp_short(R['div_m']),     fmt_clp(R['div_m']),           "amber"),
        (k3, "Arriendo mes 1 (CLP)", fmt_clp_short(R['rent_m0']),   f"≈ {arr_uf:.1f} UF/mes",     ""),
        (k4, "Cap Rate neto año 1",  fmt_pct(R['cap_rate_neto']),   "Benchmark RM: 2%–4%",        "positive" if R['cap_rate_neto'] >= 0.02 else "negative"),
        (k5, "Subsidio mes 1",       fmt_clp_short(subsidio_m),     "De tu bolsillo/mes",         "negative" if subsidio_m > 0 else "positive"),
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

    # ── KPI Row 2 ──
    k6, k7, k8, k9, k10 = st.columns(5)
    metrics_row2 = [
        (k6,  "Valor depto año " + str(yr_venta), fmt_clp_short(R['val_d'][yr_venta]), f"Plusvalía {plusvalia*100:.1f}%/año", "positive"),
        (k7,  "Ganancia neta al vender",          fmt_clp_short(gan),                  "Precio − Deuda − Costos + Flujos",    "positive" if (gan and gan > 0) else "negative"),
        (k8,  "ROI sobre capital propio",          f"{roi:.2f}x" if roi else "—",       fmt_clp(R['cap_total']) + " inv.",     "positive" if (roi and roi >= 1) else "negative"),
        (k9,  "TIR",                               fmt_pct(tir) if tir else "—",        f"Tasa crédito: {tasa_h*100:.1f}%",   "positive" if (tir and tir > tasa_h) else "negative"),
        (k10, "vs ETF " + fmt_pct(etf_ret) + "/año", fmt_clp_short(diff),              "Depto − ETF mismo capital",           "positive" if diff >= 0 else "negative"),
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
        verdict_cls = "verdict-win"; icon = "✅"
        msg = f"<b>Buena inversión</b> — El depto supera al ETF por <b>{fmt_clp(diff)}</b> al año {yr_venta}. " \
              f"ROI <b>{roi:.2f}x</b> · TIR <b>{fmt_pct(tir)}</b> · CAGR <b>{fmt_pct(cagr)}</b>. " \
              f"{'Flujo positivo en año ' + str(yr_pos) + '.' if yr_pos else 'Flujo negativo — apuesta a la plusvalía.'}"
    elif gan and diff >= 0:
        verdict_cls = "verdict-warn"; icon = "⚠️"
        msg = f"<b>Inversión aceptable</b> — Depto supera levemente al ETF ({fmt_clp(diff)}). " \
              f"ROI {roi:.2f}x · TIR {fmt_pct(tir)}."
    else:
        verdict_cls = "verdict-lose"; icon = "❌"
        msg = f"<b>El ETF gana en este escenario</b> — El ETF daría <b>{fmt_clp(-diff)}</b> más al año {yr_venta}. " \
              f"TIR {fmt_pct(tir)} vs tasa crédito {tasa_h*100:.1f}%."
    st.markdown(f'<div class="verdict {verdict_cls}" style="font-size:0.88rem">{icon} {msg}</div>',
                unsafe_allow_html=True)

    # ── CHARTS ROW ──
    c_left, c_right = st.columns(2)

    with c_left:
        vd_yr = R['val_d'][yr_venta]; sh_yr = R['saldo_h'][yr_venta]
        cv_yr = vd_yr * cv_pct;       fa_yr = R['flujo_a'][yr_venta]
        gan_neta_val = vd_yr - sh_yr - cv_yr + fa_yr
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
            x=["Precio\nventa", "− Deuda\nbanco", "− Costos\nventa", "+ Flujos\nacum.", "GANANCIA\nNETA"],
            y=[vd_yr, -sh_yr, -cv_yr, fa_yr, 0],
            connector=dict(line=dict(color="rgba(61,81,102,0.5)")),
            increasing=dict(marker=dict(color=TEAL)),
            decreasing=dict(marker=dict(color=ROSE)),
            totals=dict(marker=dict(color=AMBER)),
            text=wf_text, textposition="outside",
            textfont=dict(size=8, color="#e8edf2"),
        ))
        layout_wf = base_layout(f"Desglose ganancia neta — año {yr_venta}", height=360)
        layout_wf['yaxis']['tickformat'] = "$,.0f"
        layout_wf['margin'] = dict(l=10, r=10, t=40, b=60)
        fig.update_layout(**layout_wf)
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        cr = R['cap_rate_neto'] * 100
        cr_color = TEAL if cr >= 2 else (AMBER if cr >= 1 else ROSE)
        cr_label = "✅ Bueno" if cr >= 2 else ("⚠️ Bajo" if cr >= 1 else "❌ Muy bajo")
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:0.3rem">
          <span style="font-family:Syne;font-size:2rem;font-weight:800;color:{cr_color}">{cr:.2f}%</span>
          <span style="font-size:0.8rem;color:#8a9bb0;margin-left:0.5rem">{cr_label} · Cap Rate Neto</span>
        </div>""", unsafe_allow_html=True)
        benchmarks = [
            ("Tu Cap Rate", cr, cr_color),
            ("Mínimo aceptable", 2.0, "rgba(245,158,11,0.6)"),
            ("Benchmark RM", 3.0, "rgba(0,201,167,0.4)"),
            ("Excelente", 4.5, "rgba(0,201,167,0.2)"),
        ]
        fig2 = go.Figure()
        for label, val, color in benchmarks:
            fig2.add_trace(go.Bar(name=label, x=[val], y=[label], orientation='h',
                marker=dict(color=color), text=[f"{val:.2f}%"], textposition="outside",
                textfont=dict(size=10, color="#e8edf2")))
        fig2.add_vline(x=cr, line=dict(color=cr_color, width=3))
        layout_cr = base_layout("Cap Rate Neto Año 1", height=240)
        layout_cr['xaxis'] = dict(range=[0,6], showgrid=True, gridcolor=GRID_COLOR,
                                   ticksuffix="%", tickfont=dict(size=10), zeroline=False)
        layout_cr['yaxis'] = dict(showgrid=False, zeroline=False, tickfont=dict(size=10))
        layout_cr['showlegend'] = False; layout_cr['barmode'] = 'overlay'
        layout_cr['margin'] = dict(l=10, r=80, t=50, b=20)
        fig2.update_layout(**layout_cr)
        st.plotly_chart(fig2, use_container_width=True)

        # TIR vs Tasa
        st.markdown('<div class="section-title" style="margin-top:0.3rem">TIR vs Tasa del Crédito</div>', unsafe_allow_html=True)
        tir_v = (tir or 0) * 100
        tir_col = TEAL if (tir and tir > tasa_h) else ROSE
        fig3 = go.Figure(go.Bar(
            x=["TIR inversión", f"Tasa crédito ({tasa_h*100:.1f}%)"],
            y=[tir_v, tasa_h*100],
            marker_color=[tir_col, "rgba(61,81,102,0.6)"],
            text=[f"{tir_v:.1f}%", f"{tasa_h*100:.1f}%"],
            textposition="outside", textfont=dict(size=11, color="#e8edf2")))
        ly3 = base_layout("", height=180)
        ly3['yaxis']['ticksuffix'] = "%"
        ly3['margin'] = dict(l=0, r=10, t=10, b=10); ly3['showlegend'] = False
        fig3.update_layout(**ly3)
        st.plotly_chart(fig3, use_container_width=True)

    # ── DONUT + RESUMEN ──
    c_pie, c_info = st.columns([1, 1.6])
    with c_pie:
        pie_clp_v = R['pie_clp']
        cier_clp  = R['val_clp'] * gc_pct
        div_tot   = R['div_m'] * 12 * yr_venta
        total_out = pie_clp_v + cier_clp + div_tot
        fig4 = go.Figure(go.Pie(
            labels=["Pie inicial", "Gastos cierre", f"Dividendos {yr_venta} años"],
            values=[pie_clp_v, cier_clp, div_tot], hole=0.55,
            marker=dict(colors=[TEAL, AMBER, SKY], line=dict(color=PLOT_BG, width=2)),
            textinfo="label+percent", textfont=dict(size=9),
            hovertemplate="%{label}: $%{value:,.0f}<extra></extra>"))
        fig4.update_layout(**base_layout(f"Desembolso total a {yr_venta} años", height=290))
        fig4.update_layout(showlegend=False)
        fig4.add_annotation(text=f"{fmt_clp_short(total_out)}<br><span style='font-size:9px'>total salida</span>",
                            x=0.5, y=0.5, showarrow=False, align="center",
                            font=dict(family="Syne", size=12, color="#e8edf2"))
        st.plotly_chart(fig4, use_container_width=True)

    with c_info:
        st.markdown('<div class="section-title">Resumen financiero</div>', unsafe_allow_html=True)
        info_rows = [
            ("Valor depto",                    fmt_clp(R['val_clp'])),
            (f"Pie inicial ({int(pie_pct*100)}%)", fmt_clp(R['pie_clp'])),
            ("Gastos cierre",                  fmt_clp(R['val_clp'] * gc_pct)),
            ("Capital total invertido",         fmt_clp(R['cap_total'])),
            ("Monto hipotecario",               fmt_clp(R['hipot'])),
            ("Tasa mensual",                   fmt_pct(tasa_h / 12)),
            ("Dividendo mensual",               fmt_clp(R['div_m'])),
            ("Dividendo anual",                 fmt_clp(R['div_m'] * 12)),
            ("Arriendo bruto mes 1",            fmt_clp(R['rent_m0'])),
            ("Flujo neto año 1",                fmt_clp(R['flujo_n'][1])),
            (f"Saldo hipoteca año {yr_venta}",  fmt_clp(R['saldo_h'][yr_venta])),
            (f"Valor depto año {yr_venta}",     fmt_clp(R['val_d'][yr_venta])),
            ("Ganancia neta total",             fmt_clp(R['gan_yr'])),
            ("TIR",                             fmt_pct(tir) if tir else "—"),
            ("ROI",                             f"{roi:.2f}x" if roi else "—"),
        ]
        rows_html = "".join(
            f'<tr><td style="color:#8a9bb0;font-size:0.8rem;padding:0.35rem 0">{k}</td>'
            f'<td style="text-align:right;font-weight:500;font-size:0.85rem;padding:0.35rem 0;'
            f'color:{"#00c9a7" if i >= len(info_rows)-3 else "#e8edf2"}">{v}</td></tr>'
            for i, (k, v) in enumerate(info_rows))
        st.markdown(f'<table style="width:100%;border-collapse:collapse">{rows_html}</table>',
                    unsafe_allow_html=True)




# ════════════════════════════════════════════════════════════════════════════
# TAB 2: FLUJOS & PROYECCIONES
# ════════════════════════════════════════════════════════════════════════════
with tab2:

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yrs[1:], y=[g/1e6 if g else None for g in R['gan_v'][1:]],
        name="Ganancia Neta Depto", line=dict(color=TEAL, width=2.5),
        fill="tozeroy", fillcolor="rgba(0,201,167,0.07)",
        hovertemplate="Año %{x} · Depto: $%{y:.1f}M<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=yrs[1:], y=[e/1e6 for e in R['etf_b'][1:]],
        name=f"ETF {etf_ret*100:.0f}% neto", line=dict(color=AMBER, width=2.5, dash="dash"),
        hovertemplate="Año %{x} · ETF: $%{y:.1f}M<extra></extra>"))
    if yr_venta > 0 and R['gan_yr']:
        fig.add_vline(x=yr_venta, line=dict(color=SKY, dash="dot", width=1.5))
        fig.add_annotation(x=yr_venta, y=(R['gan_yr']/1e6), text=f"  Año {yr_venta}",
                           showarrow=False, font=dict(color=SKY, size=10), xanchor="left")
    fig.add_hline(y=0, line=dict(color="rgba(244,63,94,0.4)", width=1))
    layout = base_layout("Ganancia neta acumulada: Depto vs ETF (CLP millones)", height=380)
    layout['yaxis']['ticksuffix'] = "M"
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        colors_fn = [TEAL if f >= 0 else ROSE for f in R['flujo_n'][1:]]
        fig2 = go.Figure(go.Bar(x=yrs[1:], y=[f/1e6 for f in R['flujo_n'][1:]],
            marker_color=colors_fn, hovertemplate="Año %{x} · Flujo: $%{y:.2f}M<extra></extra>"))
        fig2.add_hline(y=0, line=dict(color=FONT_COLOR, width=1))
        layout2 = base_layout("Flujo neto anual (CLP millones)", height=300)
        layout2['yaxis']['ticksuffix'] = "M"
        fig2.update_layout(**layout2)
        if R['yr_pos']:
            fig2.add_annotation(x=R['yr_pos'], y=0.05, text=f"Positivo año {R['yr_pos']}",
                                showarrow=False, font=dict(color=TEAL, size=9), yref="paper")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=yrs, y=[v/1e6 for v in R['val_d']],
            name="Valor depto", line=dict(color=TEAL, width=2),
            fill="tozeroy", fillcolor="rgba(0,201,167,0.05)"))
        fig3.add_trace(go.Scatter(x=yrs, y=[s/1e6 for s in R['saldo_h']],
            name="Deuda banco", line=dict(color=ROSE, width=2, dash="dash"),
            fill="tozeroy", fillcolor="rgba(244,63,94,0.05)"))
        layout3 = base_layout("Valor depto vs Deuda hipotecaria (CLP millones)", height=300)
        layout3['yaxis']['ticksuffix'] = "M"
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, use_container_width=True)

    # ── GRÁFICO AMORTIZACIÓN ──
    st.markdown('<div class="section-title">Amortización — Composición del dividendo año a año</div>', unsafe_allow_html=True)
    fig_am = go.Figure()
    fig_am.add_trace(go.Bar(x=yrs[1:], y=[i/1e6 for i in R['interes_anual'][1:]],
        name="Interés", marker_color=ROSE,
        hovertemplate="Año %{x} · Interés: $%{y:,.2f}M<extra></extra>"))
    fig_am.add_trace(go.Bar(x=yrs[1:], y=[a/1e6 for a in R['amort_anual'][1:]],
        name="Amortización capital", marker_color=TEAL,
        hovertemplate="Año %{x} · Amort: $%{y:,.2f}M<extra></extra>"))
    fig_am.add_trace(go.Scatter(x=yrs[1:], y=[s/1e6 for s in R['saldo_h'][1:]],
        name="Saldo deuda", line=dict(color=AMBER, width=2, dash="dot"), yaxis="y2",
        hovertemplate="Año %{x} · Saldo: $%{y:,.1f}M<extra></extra>"))
    layout_am = base_layout("Dividendo anual: Interés vs Amortización de capital (millones CLP)", height=380)
    layout_am['barmode'] = 'stack'
    layout_am['yaxis']['ticksuffix'] = "M"
    layout_am['yaxis2'] = dict(overlaying='y', side='right', ticksuffix="M",
                                gridcolor=GRID_COLOR, zeroline=False, tickfont=dict(size=10))
    fig_am.update_layout(**layout_am)
    fig_am.add_annotation(
        text="Los primeros años casi todo el dividendo es interés. Con el tiempo, más capital se amortiza y la deuda baja más rápido.",
        x=0.5, y=-0.08, showarrow=False, xref="paper", yref="paper",
        font=dict(size=9, color=FONT_COLOR))
    st.plotly_chart(fig_am, use_container_width=True)

    # ── TABLA ──
    st.markdown('<div class="section-title">Tabla completa de flujos año a año</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([3, 1])
    with col_t2:
        show_all = st.checkbox("Mostrar todos los años", value=False)
    display_yrs = yrs if show_all else [0] + list(range(1, min(16, 31)))
    rows = []
    for y in display_yrs:
        g = R['gan_v'][y]; etf_s = R['etf_b'][y] if y > 0 else None
        winner = ""
        if y > 0 and g is not None and etf_s is not None:
            winner = "🏠 Depto" if g > etf_s else "📈 ETF"
        rows.append({
            "Año": y, "Valor Depto": fmt_clp(R['val_d'][y]),
            "Arriendo Bruto": fmt_clp(R['arr_b'][y]) if y > 0 else "—",
            "Gastos Op.": fmt_clp(R['gastos'][y]) if y > 0 else "—",
            "Flujo Neto": fmt_clp(R['flujo_n'][y]),
            "Flujo Acum.": fmt_clp(R['flujo_a'][y]),
            "Saldo Hipoteca": fmt_clp(R['saldo_h'][y]),
            "Gan. Neta Venta": fmt_clp(g) if y > 0 else "—",
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
            for v in r.values()) + "</tr>"
    st.markdown(f'<div style="overflow-x:auto"><table class="comp-table">{header_html}{data_html}</table></div>',
                unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:0.72rem;color:#8a9bb0;margin-top:0.5rem">🟢 Fila resaltada = año {yr_venta} (tu año de venta planificado)</p>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3: SENSIBILIDAD
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p style="color:#8a9bb0;font-size:0.85rem;margin-bottom:1rem">Muestra cómo cambia la rentabilidad según distintos niveles de plusvalía y tasa hipotecaria. La fila con ★ es tu escenario base.</p>', unsafe_allow_html=True)

    # ── Sensibilidad plusvalía ──
    st.markdown('<div class="section-title">Sensibilidad a la Plusvalía</div>', unsafe_allow_html=True)
    pvs = [plusvalia - 0.02, plusvalia - 0.01, plusvalia, plusvalia + 0.01, plusvalia + 0.02]
    pvs = [p for p in pvs if 0 < p <= 0.15]

    sg, sr, st_tir, sl = [], [], [], []
    for pv in pvs:
        r2 = compute_simulation(dict(params, plusvalia=pv))
        sl.append(fmt_pct(pv) + (" ◄" if abs(pv - plusvalia) < 0.001 else ""))
        sg.append((r2['gan_yr'] or 0) / 1e6)
        sr.append(r2['roi'] or 0)
        st_tir.append((r2['tir'] or 0) * 100)

    fig_s = make_subplots(rows=1, cols=2, subplot_titles=["Ganancia Neta (M CLP)", "ROI y TIR (%)"])
    bc = [TEAL if abs(pvs[i]-plusvalia) < 0.001 else "rgba(0,201,167,0.4)" for i in range(len(pvs))]
    fig_s.add_trace(go.Bar(x=sl, y=sg, marker_color=bc,
        text=[f"${v:.1f}M" for v in sg], textposition="outside",
        textfont=dict(size=9), name="Ganancia"), row=1, col=1)
    fig_s.add_trace(go.Scatter(x=sl, y=sr, mode="lines+markers",
        line=dict(color=AMBER, width=2), name="ROI (x)", marker=dict(size=8)), row=1, col=2)
    fig_s.add_trace(go.Scatter(x=sl, y=st_tir, mode="lines+markers",
        line=dict(color=SKY, width=2), name="TIR (%)", marker=dict(size=8)), row=1, col=2)
    fig_s.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="DM Sans", color=FONT_COLOR), height=340,
        margin=dict(l=0,r=10,t=40,b=10), legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified")
    fig_s.update_xaxes(showgrid=False, zeroline=False)
    fig_s.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
    st.plotly_chart(fig_s, use_container_width=True)

    hdr_s = "<tr><th>Plusvalía/año</th><th>Valor depto</th><th>Ganancia Neta</th><th>ROI</th><th>TIR</th><th>vs ETF</th><th>Resultado</th></tr>"
    rows_s = ""
    for pv in pvs:
        r2 = compute_simulation(dict(params, plusvalia=pv))
        g2 = r2['gan_yr']; d2 = (g2 or 0) - r2['etf_yr']
        ib = abs(pv - plusvalia) < 0.001
        res = "✅ Buena" if (g2 and d2>0 and r2['roi'] and r2['roi']>=1.5) else ("⚠️ Revisar" if (g2 and d2>=0) else "❌ ETF gana")
        bg = 'background:rgba(0,201,167,0.08)' if ib else ''
        roi2 = r2['roi']; tir2 = r2['tir']
        rows_s += f'<tr style="{bg}"><td><b>{"★ " if ib else ""}{fmt_pct(pv)}</b></td><td>{fmt_clp(r2["val_d"][yr_venta])}</td><td>{fmt_clp(g2)}</td><td>{f"{roi2:.2f}x" if roi2 else "—"}</td><td>{fmt_pct(tir2) if tir2 else "—"}</td><td>{fmt_clp(d2)}</td><td>{res}</td></tr>'
    st.markdown(f'<table class="comp-table">{hdr_s}{rows_s}</table>', unsafe_allow_html=True)

    # ── Sensibilidad tasa ──
    st.markdown('<div class="section-title" style="margin-top:1.5rem">Sensibilidad a la Tasa Hipotecaria</div>', unsafe_allow_html=True)
    tasas = [max(0.02, tasa_h - 0.01), max(0.02, tasa_h - 0.005), tasa_h, tasa_h + 0.005, tasa_h + 0.01]
    hdr_t = "<tr><th>Tasa anual</th><th>Dividendo mensual</th><th>Ganancia Neta</th><th>ROI</th><th>TIR</th><th>Subsidio mes 1</th></tr>"
    rows_t = ""
    for ta in tasas:
        r2 = compute_simulation(dict(params, tasa=ta))
        ib = abs(ta - tasa_h) < 0.0001
        sub2 = max(0, r2['div_m'] - r2['rent_m0']*(1-vacancia-adm-reserva) +
                   ((gcom+(contrib+seguro)/12) + r2['val_clp']*mant/12))
        bg = 'background:rgba(0,201,167,0.08)' if ib else ''
        roi2 = r2['roi']; tir2 = r2['tir']
        rows_t += f'<tr style="{bg}"><td><b>{"★ " if ib else ""}{fmt_pct(ta)}</b></td><td>{fmt_clp(r2["div_m"])}</td><td>{fmt_clp(r2["gan_yr"])}</td><td>{f"{roi2:.2f}x" if roi2 else "—"}</td><td>{fmt_pct(tir2) if tir2 else "—"}</td><td>{fmt_clp(sub2)}/mes</td></tr>'
    st.markdown(f'<table class="comp-table">{hdr_t}{rows_t}</table>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.72rem;color:#8a9bb0;margin-top:0.4rem">★ = escenario base configurado en el panel lateral</p>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4: COMPARADOR
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p style="color:#8a9bb0;font-size:0.85rem">Configura hasta 5 propiedades distintas y compáralas en paralelo. La Simulación 1 toma los parámetros del panel lateral.</p>', unsafe_allow_html=True)

    n_sims = st.radio("¿Cuántas propiedades comparar?", [2, 3, 4, 5], horizontal=True, index=1)
    sim_params = [dict(params)]
    sim_names  = ["Sim 1 (actual)"]

    cols_sims = st.columns(n_sims - 1)
    for i, col in enumerate(cols_sims):
        idx = i + 2
        with col:
            st.markdown(f'<div class="section-title">Simulación {idx}</div>', unsafe_allow_html=True)
            name      = st.text_input("Nombre", value=f"Propiedad {idx}", key=f"name_{idx}")
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

    metrics_comp = [
        ("Valor depto",              [fmt_clp(r['val_clp']) for r in results]),
        ("Capital invertido",        [fmt_clp(r['cap_total']) for r in results]),
        ("Dividendo mensual",        [fmt_clp(r['div_m']) for r in results]),
        ("Arriendo mes 1",           [fmt_clp(r['rent_m0']) for r in results]),
        ("Cap Rate neto año 1",      [fmt_pct(r['cap_rate_neto']) for r in results]),
        ("Plusvalía/año",            [fmt_pct(p['plusvalia']) for p in sim_params[:n_sims]]),
        ("Año de venta",             [str(r['yr_venta']) for r in results]),
        ("Valor depto al vender",    [fmt_clp(r['val_d'][r['yr_venta']]) for r in results]),
        ("Saldo hipoteca al vender", [fmt_clp(r['saldo_h'][r['yr_venta']]) for r in results]),
        ("Ganancia Neta Total",      [fmt_clp(r['gan_yr']) for r in results]),
        ("ROI sobre capital",        [f"{r['roi']:.2f}x" if r['roi'] else "—" for r in results]),
        ("TIR",                      [fmt_pct(r['tir']) if r['tir'] else "—" for r in results]),
        ("CAGR anual",               [fmt_pct(r['cagr']) for r in results]),
        ("ETF equivalente",          [fmt_clp(r['etf_yr']) for r in results]),
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
    st.markdown(f'<div style="overflow-x:auto"><table class="comp-table">{header_html}{rows_html}</table></div>',
                unsafe_allow_html=True)

    colors_c = [TEAL, AMBER, SKY, PURPLE, ROSE]
    gans_comp = [r['gan_yr'] or 0 for r in results]
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=names, y=[g/1e6 for g in gans_comp],
        marker_color=[colors_c[i] for i in range(n_sims)],
        text=[fmt_clp(g) for g in gans_comp],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="%{x}: $%{y:.1f}M<extra></extra>"))
    layout_c = base_layout("Ganancia neta total por propiedad (CLP millones)", height=340)
    layout_c['yaxis']['ticksuffix'] = "M"; layout_c['showlegend'] = False
    fig_comp.update_layout(**layout_c)
    st.plotly_chart(fig_comp, use_container_width=True)

    fig_lines = go.Figure()
    for i, (r, name) in enumerate(zip(results, names)):
        fig_lines.add_trace(go.Scatter(
            x=yrs[1:], y=[g/1e6 if g else None for g in r['gan_v'][1:]],
            name=name, line=dict(color=colors_c[i], width=2),
            hovertemplate=f"{name} Año %{{x}}: $%{{y:.1f}}M<extra></extra>"))
    fig_lines.add_hline(y=0, line=dict(color="rgba(255,255,255,0.15)", width=1))
    layout_l = base_layout("Evolución ganancia neta acumulada — todas las simulaciones", height=360)
    layout_l['yaxis']['ticksuffix'] = "M"
    fig_lines.update_layout(**layout_l)
    st.plotly_chart(fig_lines, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 5: GUÍA DE INDICADORES
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p style="color:#8a9bb0;font-size:0.85rem;margin-bottom:1.2rem">Guía para entender cada indicador del simulador y cómo interpretarlo para tomar mejores decisiones.</p>', unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown('<div class="section-title">Inputs críticos — qué significan</div>', unsafe_allow_html=True)
        guide_inputs = [
            ("📐 Plusvalía nominal/año", f"Tu zona: {plusvalia*100:.1f}%",
             "El motor principal de rentabilidad. Con crédito hipotecario, la plusvalía actúa sobre el 100% del depto pero tú solo pusiste el pie — esto se llama apalancamiento financiero y multiplica tu retorno sobre capital propio."),
            ("🏘️ Cap Rate neto", f"Tu caso: {R['cap_rate_neto']*100:.2f}%",
             "Arriendo neto anual ÷ valor del depto. Mide si el depto 'se paga solo' operacionalmente. Benchmark RM: 2%–4% neto. Menor a 2% = vives de la plusvalía. Mayor a 4% = excelente operación."),
            ("📉 Vacancia", f"Usas: {vacancia*100:.0f}%",
             "Porcentaje del año sin arrendatario. 8% ≈ 1 mes sin ingresos. Zonas consolidadas: 5%–8%. Zonas emergentes: 10%–20%. Impacta directamente el flujo y el punto de equilibrio."),
            ("📈 Crecimiento arriendo", f"Usas: {rent_gr*100:.1f}%/año",
             "A qué ritmo suben los arriendos. Históricamente RM: 4%–6% nominal. Afecta cuándo el flujo se vuelve positivo."),
            ("🏦 Tasa hipotecaria", f"Usas: {tasa_h*100:.2f}% anual",
             f"Define tu dividendo mensual de {fmt_clp(R['div_m'])}. A mayor tasa, mayor flujo negativo los primeros años. Negociar la tasa puede cambiar significativamente el resultado."),
        ]
        for name, value, desc in guide_inputs:
            st.markdown(f"""
            <div class="guide-card">
              <div class="guide-name">{name} <span class="badge badge-amber">{value}</span></div>
              <div class="guide-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="section-title">Indicadores de resultado — cómo leerlos</div>', unsafe_allow_html=True)
        guide_outputs = [
            ("💰 Ganancia Neta de Venta", f"Tu caso año {yr_venta}: {fmt_clp(R['gan_yr'])}",
             "LA MÉTRICA MÁS IMPORTANTE. Precio de venta − deuda banco − costos de venta + flujos acumulados. Lo que queda en tu bolsillo al vender."),
            ("📊 TIR (Tasa Interna de Retorno)", fmt_pct(tir) if tir else "—",
             f"La rentabilidad anual equivalente de toda la inversión. Compárala con tu tasa de crédito ({tasa_h*100:.1f}%). Si TIR > tasa crédito, la inversión crea valor. Buena TIR > 8%."),
            ("🔄 ROI (Return on Investment)", f"{roi:.2f}x" if roi else "—",
             "Ganancia neta ÷ capital propio invertido. ROI de 2x = duplicaste tu inversión. El apalancamiento hace que el ROI sea mucho mayor que la plusvalía del depto."),
            ("📊 Flujo Neto Anual", f"Año 1: {fmt_clp(R['flujo_n'][1])}",
             "Arriendo − Gastos − Dividendo. Si es negativo, pones dinero de tu bolsillo mensualmente. " +
             (f"En tu caso se vuelve positivo en el año {R['yr_pos']}." if R['yr_pos'] else "En tu escenario el flujo no llega a positivo en 30 años.")),
            ("🏦 vs ETF", f"Diferencia año {yr_venta}: {fmt_clp(diff)}",
             f"Compara con invertir el mismo dinero en ETF al {etf_ret*100:.0f}% neto. Comparación JUSTA: ambas alternativas cuestan lo mismo de tu bolsillo. El depto gana a largo plazo gracias al apalancamiento."),
            ("⚖️ Cuándo conviene vender", "",
             "Matemáticamente: cuando Ganancia Neta Depto > saldo ETF. Prácticamente: no antes del año 7–8. El apalancamiento funciona mejor mientras más tiempo pasa."),
        ]
        for name, value, desc in guide_outputs:
            badge = f'<span class="badge badge-green">{value}</span>' if value else ""
            st.markdown(f"""
            <div class="guide-card">
              <div class="guide-name">{name} {badge}</div>
              <div class="guide-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:1.5rem">Marco de decisión — semáforo de la inversión</div>', unsafe_allow_html=True)
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.markdown("""
        <div class="verdict verdict-win">
          <b style="color:#00c9a7">✅ BUENA inversión si...</b><br><br>
          <span style="font-size:0.82rem;color:#8a9bb0">
          • Plusvalía zona ≥ 5.5%<br>
          • Cap Rate neto > 2.5%<br>
          • TIR > tasa del crédito<br>
          • Flujo positivo antes del año 12<br>
          • Depto supera ETF en año 10
          </span>
        </div>""", unsafe_allow_html=True)
    with c_s2:
        st.markdown("""
        <div class="verdict verdict-warn">
          <b style="color:#f59e0b">⚠️ REVISAR si...</b><br><br>
          <span style="font-size:0.82rem;color:#8a9bb0">
          • Plusvalía entre 3%–5%<br>
          • Cap Rate < 2%<br>
          • TIR ≈ tasa del crédito<br>
          • Flujo negativo por más de 15 años<br>
          • Depto supera ETF solo después del año 20
          </span>
        </div>""", unsafe_allow_html=True)
    with c_s3:
        st.markdown("""
        <div class="verdict verdict-lose">
          <b style="color:#f43f5e">❌ MALA inversión si...</b><br><br>
          <span style="font-size:0.82rem;color:#8a9bb0">
          • Plusvalía < 3%<br>
          • Cap Rate neto < 1.5%<br>
          • TIR < tasa del crédito<br>
          • Flujo nunca positivo en 30 años<br>
          • ETF gana en año 30
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="guide-card" style="margin-top:1rem;border-left:3px solid #00c9a7">
      <div class="guide-name">💡 La clave: el depto es una apuesta a la PLUSVALÍA, no al arriendo</div>
      <div class="guide-desc">
      El banco financia el 80% del depto, pero el 100% de la plusvalía es tuya. Con 5.5% nominal de plusvalía anual,
      un depto de $200M sube $11M/año — pero tú solo pusiste $44M de capital propio. Eso es apalancamiento financiero
      y explica por qué el depto puede superar al ETF a largo plazo, a pesar de los flujos negativos iniciales.
      </div>
    </div>""", unsafe_allow_html=True)


# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;border-top:1px solid rgba(61,81,102,0.4);padding-top:1rem;text-align:center">
  <p style="font-size:0.72rem;color:#8a9bb0">
    Simulador educativo · Valores en CLP nominales · No constituye asesoría financiera<br>
    Desarrollado por Alonso Tapia D. · Fuentes: SII, CMF, BCCh · Benchmark RM basado en datos históricos 2015–2024
  </p>
</div>
""", unsafe_allow_html=True)