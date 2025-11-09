#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from enum import Enum

# -------------------------------
# PROGRAMA INTERATIVO
# -------------------------------

def main():
    print("=== SISTEMA DE ALUGUEL IMOBILIÁRIA R.M ===\n")

    tipo_str = input("Digite o tipo de imóvel (apartamento, casa ou estudio): ").strip().lower()
    if tipo_str not in ["apartamento", "casa", "estudio"]:
        print("Tipo de imóvel inválido. Encerrando.")
        return

    quartos = int(input("Quantos quartos? (1 ou 2): ") or 1)
    tem_criancas = input("Tem crianças? (s/n): ").strip().lower() == 's'

    garagem = False
    vagas_estudio = 0

    if tipo_str in ["apartamento", "casa"]:
        garagem = input("Deseja incluir garagem? (s/n): ").strip().lower() == 's'
    elif tipo_str == "estudio":
        vagas_estudio = int(input("Quantas vagas de estacionamento? ") or 0)

    parcelas = int(input("Em quantas parcelas deseja dividir o contrato (1 a 5)? ") or 1)
    if parcelas < 1 or parcelas > 5:
        print("Número de parcelas inválido. Deve ser entre 1 e 5.")
        return

    # --- Cálculo ---
    tipo = TipoImovel(tipo_str)
    entrada = OrcamentoEntrada(tipo, quartos, tem_criancas, garagem, vagas_estudio, parcelas)
    calc = CalculadoraOrcamento()
    resultado = calc.calcular(entrada)

    # --- Exibição ---
    print("\n=== RESULTADO DO ORÇAMENTO ===")
    print(f"Tipo de imóvel: {tipo.value.capitalize()}")
    print(f"Aluguel base: R$ {resultado.aluguel_base:.2f}")
    print(f"Adicionais: R$ {resultado.adicionais:.2f}")
    print(f"Desconto: R$ {resultado.desconto:.2f}")
    print(f"Aluguel final: R$ {resultado.aluguel_mensal_final:.2f}")
    print(f"Parcela contrato: R$ {resultado.parcela_contrato:.2f}")
    print(f"Total mensal com contrato: R$ {resultado.total_mensal_com_contrato:.2f}")

    # --- Gera CSV ---
    gerar_csv_parcelas(resultado, "orcamento.csv", meses=12, incluir_contrato_ate=parcelas)
    print("\nArquivo 'orcamento.csv' gerado com sucesso!")


# -------------------------------
# CLASSES E LÓGICA
# -------------------------------

class TipoImovel(Enum):
    APARTAMENTO = "apartamento"
    CASA = "casa"
    ESTUDIO = "estudio"


class OrcamentoEntrada:
    def __init__(self, tipo, quartos, tem_criancas, garagem, vagas_estudio, parcelas_contrato):
        self.tipo = tipo
        self.quartos = quartos
        self.tem_criancas = tem_criancas
        self.garagem = garagem
        self.vagas_estudio = vagas_estudio
        self.parcelas_contrato = parcelas_contrato


class OrcamentoResultado:
    def __init__(self, aluguel_base, adicionais, desconto, aluguel_mensal_final, parcela_contrato, total_mensal_com_contrato):
        self.aluguel_base = aluguel_base
        self.adicionais = adicionais
        self.desconto = desconto
        self.aluguel_mensal_final = aluguel_mensal_final
        self.parcela_contrato = parcela_contrato
        self.total_mensal_com_contrato = total_mensal_com_contrato


class CalculadoraOrcamento:
    VALOR_CONTRATO = 2000.00

    VALORES_BASE = {
        TipoImovel.APARTAMENTO: 700.00,
        TipoImovel.CASA: 900.00,
        TipoImovel.ESTUDIO: 1200.00
    }

    def calcular(self, entrada: OrcamentoEntrada) -> OrcamentoResultado:
        tipo = entrada.tipo
        aluguel_base = self.VALORES_BASE[tipo]
        adicionais = 0
        desconto = 0

        # ---- ACRÉSCIMOS POR QUARTO ----
        if tipo == TipoImovel.APARTAMENTO and entrada.quartos == 2:
            adicionais += 200.00
        elif tipo == TipoImovel.CASA and entrada.quartos == 2:
            adicionais += 250.00

        # ---- GARAGEM / ESTACIONAMENTO ----
        if tipo in [TipoImovel.APARTAMENTO, TipoImovel.CASA]:
            if entrada.garagem:
                adicionais += 300.00
        elif tipo == TipoImovel.ESTUDIO:
            if entrada.vagas_estudio >= 2:
                adicionais += 250.00
                if entrada.vagas_estudio > 2:
                    adicionais += 60.00 * (entrada.vagas_estudio - 2)
            elif entrada.vagas_estudio == 1:
                adicionais += 250.00  # valor mínimo

        # ---- DESCONTO PARA APARTAMENTOS SEM CRIANÇAS ----
        if tipo == TipoImovel.APARTAMENTO and not entrada.tem_criancas:
            desconto = 0.05 * (aluguel_base + adicionais)

        aluguel_final = (aluguel_base + adicionais) - desconto

        # ---- CONTRATO PARCELADO ----
        parcela_contrato = self.VALOR_CONTRATO / entrada.parcelas_contrato
        total_mensal_com_contrato = aluguel_final + parcela_contrato

        return OrcamentoResultado(
            aluguel_base,
            adicionais,
            desconto,
            aluguel_final,
            parcela_contrato,
            total_mensal_com_contrato
        )


# -------------------------------
# GERAR CSV COM 12 PARCELAS
# -------------------------------

def gerar_csv_parcelas(resultado: OrcamentoResultado, nome_arquivo: str, meses=12, incluir_contrato_ate=5):
    with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Mês", "Aluguel Mensal", "Parcela Contrato", "Total no Mês"])

        for mes in range(1, meses + 1):
            parcela_contrato = resultado.parcela_contrato if mes <= incluir_contrato_ate else 0
            total = resultado.aluguel_mensal_final + parcela_contrato
            writer.writerow([
                mes,
                f"{resultado.aluguel_mensal_final:.2f}",
                f"{parcela_contrato:.2f}",
                f"{total:.2f}"
            ])


# -------------------------------
# EXECUÇÃO PRINCIPAL
# -------------------------------

if __name__ == "__main__":
    main()
