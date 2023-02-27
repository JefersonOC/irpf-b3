from import_b3 import DeclaraImpostoAcoes


ano = 2023
relatorio_negociacoes = str(ano) + "/negociacao-" + str(ano) + ".xlsx"
relatorio_movimentacoes = str(ano) + "/movimentacao-" + str(ano) + ".xlsx"
relatorio_ipos = str(ano) + "/ofertas-publicas-" + str(ano) + ".xlsx"


def main():
    declaracao = DeclaraImpostoAcoes(
        ano, relatorio_negociacoes, relatorio_movimentacoes, relatorio_ipos)

    print("======================================================")
    print("INFO: ")
    print("- 15% SWING TRADE / 20% DAYTRADE")
    print("- ISENÇÃO LIMITE DE R$ 20.000 EM VENDAS SOMENTE PARA AÇÕES")
    print("- BDR/ETF/FII NÃO TEM INSENÇÃO DE LIMITE")
    print("- DIVIDENDOS E ALUGUEIS SAO ISENTOS")
    print("- JCP 15% RETIDO NA FONTE")

    # AÇÔES e FIIS
    print("\n======================================================")
    print("BENS E DIREITOS")
    print("======================================================")
    print(declaracao.bensDireitos())

    # AÇÕES
    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - LUCRO ISENTO POR MÊS")
    print("======================================================")
    print(declaracao.calculaVendasStocks('lucro_isento'))

    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - LUCRO TAXADO POR MÊS")
    print("======================================================")
    print(declaracao.calculaVendasStocks('lucro_taxado'))

    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - LUCRO ISENTO NO ANO")
    print("======================================================")
    print(declaracao.calculaVendasStocks('lucro_isento_no_ano'))

    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - LUCRO TAXADO NO ANO")
    print("======================================================")
    print(declaracao.calculaVendasStocks('lucro_taxado_no_ano'))

    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE AÇÕES - PREJUÍZO POR MÊS")
    print("======================================================")
    print(declaracao.calculaVendasStocks('prejuizo'))

    # FIIS
    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE FIIS - LUCRO TAXADO POR MÊS")
    print("======================================================")
    print(declaracao.calculaVendasFIIs('lucro_taxado'))

    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE FIIS - LUCRO TAXADO NO ANO")
    print("======================================================")
    print(declaracao.calculaVendasFIIs('lucro_taxado_no_ano'))

    print("\n======================================================")
    print("RENDIMENTOS COM VENDAS DE FIIS - PREJUÍZO POR MÊS")
    print("======================================================")
    print(declaracao.calculaVendasFIIs('prejuizo'))

    # DIVIDENDOS AÇÕES
    print("\n======================================================")
    print("PROVENTOS AÇÕES - DIVIDENDO")
    print("======================================================")
    print(declaracao.somaProventos('dividendo'))

    print("\n======================================================")
    print("PROVENTOS AÇÕES - JCP")
    print("======================================================")
    print(declaracao.somaProventos('jcp'))

    # RENDIMENTOS FIIS
    print("\n======================================================")
    print("PROVENTOS FIIS - RENDIMENTO")
    print("======================================================")
    print(declaracao.somaProventos('rendimento'))

    # EXCEÇÕES
    print("\n======================================================")
    print("EVENTOS EXOTICOS")
    print("======================================================")
    print(declaracao.eventosExoticos())


if __name__ == "__main__":
    main()
