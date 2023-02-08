from import_b3 import DeclaraImpostoAcoes


relatorio_negociacoes = "negociacao-2022.xlsx"
relatorio_movimentacoes = "movimentacao-2022.xlsx"
relatorio_ipos = "ofertas-publicas-2022.xlsx"
ano = 2022


def main():
    declaracao2022 = DeclaraImpostoAcoes(
        ano, relatorio_negociacoes, relatorio_movimentacoes, relatorio_ipos)

    print("======================================================")
    print("INFO: ")
    print("- 15% SWING TRADE / 20% DAYTRADE")
    print("- ISENÇÃO LIMITE DE R$ 20.000 EM VENDAS SOMENTE PARA AÇÕES")
    print("- BDR/ETF/FII NÃO TEM INSENÇÃO DE LIMITE")
    print("- DIVIDENDOS E ALUGUEIS SAO ISENTOS")
    print("- JCP 15% RETIDO NA FONTE")

    print("======================================================")
    print("BENS E DIREITOS")
    print("======================================================")
    print(declaracao2022.bensDireitos())
    print("======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - LUCRO ISENTO POR MÊS")
    print("======================================================")
    print(declaracao2022.calculaRendimentos('lucro_isento'))
    print("======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - LUCRO ISENTO NO ANO")
    print("======================================================")
    print(declaracao2022.calculaRendimentos('lucro_isento_no_ano'))
    print("======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - PREJUÍZO POR MÊS")
    print("======================================================")
    print(declaracao2022.calculaRendimentos('prejuizo'))
    print("======================================================")
    print("PROVENTOS - DIVIDENDO")
    print("======================================================")
    print(declaracao2022.somaProventos('dividendo'))
    print("======================================================")
    print("PROVENTOS - RENDIMENTO")
    print("======================================================")
    print(declaracao2022.somaProventos('rendimento'))
    print("======================================================")
    print("PROVENTOS - JCP")
    print("======================================================")
    print(declaracao2022.somaProventos('jcp'))
    print("======================================================")
    print("EVENTOS EXOTICOS")
    print("======================================================")
    print(declaracao2022.eventosExoticos())


if __name__ == "__main__":
    main()
