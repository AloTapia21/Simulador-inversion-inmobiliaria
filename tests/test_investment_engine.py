import unittest

from investment_engine import calcular_plan_hipotecario, calcular_tir, compute_simulation


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


class SimulacionTests(unittest.TestCase):
    def test_no_cobra_dividendos_despues_del_plazo(self):
        resultado = compute_simulation(parametros_base(plazo=15, yr_venta=20))

        self.assertAlmostEqual(resultado["saldo_h"][15], 0, places=4)
        self.assertEqual(resultado["pagos_hipoteca"][16:], [0.0] * 15)

    def test_etf_reporta_ganancia_y_no_saldo_total(self):
        resultado = compute_simulation(
            parametros_base(pie=1.0, etf_pie=1.0, tasa=0.0, plazo=15, yr_venta=1, etf_ret=0.10)
        )

        self.assertAlmostEqual(resultado["etf_b"][1], resultado["cap_total"] * 0.10)
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

    def test_rechaza_un_pie_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            compute_simulation(parametros_base(pie=1.01))


if __name__ == "__main__":
    unittest.main()
