import unittest

from investment_engine import (
    CAMBIO_TASA_HABITACIONAL_2026_S2,
    EXENCION_HABITACIONAL_2026_S2,
    calcular_contribucion_habitacional,
    calcular_plan_hipotecario,
    calcular_tir,
    compute_simulation,
)


def parametros_base(**cambios):
    parametros = {
        "uf": 40_000,
        "val_uf": 5_000,
        "arriendo_uf": 25,
        "rent_gr": 0.04,
        "vacancia": 0.08,
        "adm": 0.08,
        "gcom": 100_000,
        "contrib": 320_000,
        "contrib_gr": 0.03,
        "seguro": 120_000,
        "mant": 0.005,
        "reserva": 0.05,
        "pie": 0.20,
        "tasa": 0.04,
        "plazo": 15,
        "gastos_cierre": 0.025,
        "costo_venta": 0.025,
        "plusvalia": 0.055,
        "etf_ret": 0.10,
        "etf_pie": 0.20,
        "yr_venta": 20,
        "remodelaciones": {5: 80},
    }
    parametros.update(cambios)
    return parametros


class PlanHipotecarioTests(unittest.TestCase):
    def test_credito_sin_interes_termina_en_su_plazo(self):
        plan = calcular_plan_hipotecario(1_200, 0, 1, horizonte=3)

        self.assertAlmostEqual(plan["cuota_mensual"], 100)
        self.assertAlmostEqual(plan["pagos_anuales"][1], 1_200)
        self.assertAlmostEqual(plan["saldos"][1], 0)
        self.assertEqual(plan["pagos_anuales"][2:], [0.0, 0.0])

    def test_interes_mas_amortizacion_es_igual_al_pago(self):
        plan = calcular_plan_hipotecario(100_000_000, 0.04, 20)

        for pago, interes, amortizacion in zip(
            plan["pagos_anuales"], plan["intereses_anuales"], plan["amortizaciones_anuales"]
        ):
            self.assertAlmostEqual(pago, interes + amortizacion, places=5)


class ContribucionesTests(unittest.TestCase):
    def test_avaluo_bajo_exencion_no_paga_contribuciones(self):
        resultado = calcular_contribucion_habitacional(EXENCION_HABITACIONAL_2026_S2 - 1)

        self.assertEqual(resultado["avaluo_afecto"], 0)
        self.assertEqual(resultado["total_anual"], 0)

    def test_calcula_primer_tramo_habitacional(self):
        avaluo = 100_000_000
        resultado = calcular_contribucion_habitacional(avaluo)
        esperado = (avaluo - EXENCION_HABITACIONAL_2026_S2) * 0.00893

        self.assertAlmostEqual(resultado["contribucion_neta"], esperado)
        self.assertEqual(resultado["sobretasa_fiscal"], 0)
        self.assertAlmostEqual(resultado["cuota"], esperado / 4)

    def test_calcula_dos_tramos_y_sobretasa_fiscal(self):
        avaluo = 300_000_000
        resultado = calcular_contribucion_habitacional(avaluo)
        neta_esperada = (
            (CAMBIO_TASA_HABITACIONAL_2026_S2 - EXENCION_HABITACIONAL_2026_S2) * 0.00893
            + (avaluo - CAMBIO_TASA_HABITACIONAL_2026_S2) * 0.01042
        )
        sobretasa_esperada = (avaluo - EXENCION_HABITACIONAL_2026_S2) * 0.00025

        self.assertAlmostEqual(resultado["contribucion_neta"], neta_esperada)
        self.assertAlmostEqual(resultado["sobretasa_fiscal"], sobretasa_esperada)
        self.assertAlmostEqual(resultado["total_anual"], neta_esperada + sobretasa_esperada)


class SimulacionTests(unittest.TestCase):
    def test_no_cobra_dividendos_despues_del_plazo(self):
        resultado = compute_simulation(parametros_base(plazo=15, yr_venta=20))

        self.assertAlmostEqual(resultado["saldo_h"][15], 0, places=4)
        self.assertEqual(resultado["pagos_hipoteca"][16:], [0.0] * 15)

    def test_etf_reporta_ganancia_y_no_saldo_total(self):
        resultado = compute_simulation(
            parametros_base(pie=1.0, etf_pie=1.0, tasa=0.0, plazo=15, yr_venta=1, etf_ret=0.10)
        )

        self.assertAlmostEqual(resultado["etf_b"][1], resultado["etf_capital_inicial"] * 0.10)
        self.assertGreater(resultado["etf_saldo"][1], resultado["etf_b"][1])

    def test_pie_etf_es_independiente_del_pie_del_departamento(self):
        resultado = compute_simulation(parametros_base(pie=0.0, etf_pie=0.20))

        self.assertEqual(resultado["pie_clp"], 0)
        self.assertAlmostEqual(resultado["etf_capital_inicial"], resultado["val_clp"] * 0.20)

    def test_aporte_etf_es_solo_diferencia_positiva_entre_dividendo_y_arriendo(self):
        resultado = compute_simulation(
            parametros_base(
                pie=0.0,
                etf_pie=0.20,
                tasa=0.0,
                plazo=15,
                etf_ret=0.0,
                yr_venta=1,
            )
        )
        aporte_esperado = max(0, resultado["div_m"] - resultado["rent_m0"])

        self.assertAlmostEqual(resultado["etf_aporte_mensual"][1], aporte_esperado)
        self.assertAlmostEqual(resultado["etf_aportes_anuales"][1], aporte_esperado * 12)
        self.assertAlmostEqual(resultado["etf_b"][1], 0)

    def test_tir_de_un_flujo_que_duplica_en_un_ano_es_cien_por_ciento(self):
        self.assertAlmostEqual(calcular_tir([-100, 200]), 1.0, places=5)

    def test_mantencion_del_primer_anio_usa_el_valor_de_compra(self):
        parametros = parametros_base(
            vacancia=0,
            adm=0,
            reserva=0,
            gcom=0,
            contrib=0,
            seguro=0,
            remodelaciones={},
        )
        resultado = compute_simulation(parametros)

        self.assertAlmostEqual(resultado["gastos"][1], resultado["val_clp"] * parametros["mant"])

    def test_contribuciones_se_distribuyen_en_sus_trimestres_de_vencimiento(self):
        resultado = compute_simulation(parametros_base())
        contribuciones = [
            trimestre["contribuciones"] for trimestre in resultado["flujos_trimestrales"][1]
        ]

        self.assertEqual(contribuciones, [0, 160_000, 80_000, 80_000])
        self.assertAlmostEqual(
            sum(trimestre["flujo_neto"] for trimestre in resultado["flujos_trimestrales"][1]),
            resultado["flujo_n"][1],
        )

    def test_contribuciones_crecen_con_el_reajuste_seleccionado(self):
        resultado = compute_simulation(parametros_base(contrib=400_000, contrib_gr=0.05))

        self.assertAlmostEqual(resultado["contribuciones_anuales"][1], 400_000)
        self.assertAlmostEqual(resultado["contribuciones_anuales"][2], 420_000)

    def test_rechaza_un_pie_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            compute_simulation(parametros_base(pie=1.01))


if __name__ == "__main__":
    unittest.main()
