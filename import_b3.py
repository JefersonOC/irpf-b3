import os
import pandas as pd
import numpy as np
import warnings
import cnpjs

warnings.filterwarnings('ignore')


class DeclaraImpostoAcoes():
    # Separar o ticker da tabela de movimentações
    def _ticker(self, palavra):
        return palavra[0:palavra.find(' - ', 0)].strip()

    # Remove o 'L' dos tickers de IPO para agrupar com os tickers da mesma empresa sem o 'L'
    def _removeL(self, palavra):
        x = 0
        while palavra.find('L', x) != -1 and x < len(palavra)-1:
            x = palavra.find('L', x+1)
            if palavra.find('L', x) == len(palavra)-1:
                return palavra[0:len(palavra)-1]
        return palavra

    # Remove o 'F' dos tickers fracionarios para agrupar com os tickers da mesma empresa sem o 'F'
    def _removeF(self, palavra):
        x = 0
        while palavra.find('F', x) != -1 and x < len(palavra)-1:
            x = palavra.find('F', x+1)
            if palavra.find('F', x) == len(palavra)-1:
                return palavra[0:len(palavra)-1]
        return palavra

    # Insere CNPJ nos dados das empresas
    def _CNPJ(self, ticker):
        if ticker in cnpjs.STOCKS:
            return cnpjs.STOCKS[ticker]

        # STOCKS CAN END IN F
        elif ticker.endswith("F") and ticker[:-1] in cnpjs.STOCKS:
            ticker = ticker[:-1]
            return cnpjs.STOCKS[ticker]

        # ETF and FII code can end in 11 or 11B
        # if len(ticker) == 6 and ticker.endswith("11"):
        #     ticker = ticker[:-2]
        # elif len(ticker) == 7 and ticker.endswith("11B"):
        #     ticker = ticker[:-3]

        if ticker in cnpjs.FIIS:
            return cnpjs.FIIS[ticker]
        if ticker in cnpjs.ETFS:
            return cnpjs.ETFS[ticker]
        return "UNKNOWN"

    # Printa a declaraçao das posições no final do ano
    def _declaraPapeis(self, acoes, corretora):
        for i in range(len(acoes)):
            if acoes.iloc[i]['Código de Negociação'] in cnpjs.STOCKS:
                msg = f"{acoes.iloc[i]['CNPJ']}\n{acoes.iloc[i]['Quantidade']} AÇÕES do ativo ({acoes.iloc[i]['Código de Negociação']}) - Custódia: {corretora}\nR$ {str(round(acoes.iloc[i]['Valor'],2)).replace('.',',')} \n"
                print(msg)

            if acoes.iloc[i]['Código de Negociação'] in cnpjs.FIIS:
                msg = f"{acoes.iloc[i]['CNPJ']}\n{acoes.iloc[i]['Quantidade']} FIIS do ativo ({acoes.iloc[i]['Código de Negociação']}) - Custódia: {corretora}\nR$ {str(round(acoes.iloc[i]['Valor'],2)).replace('.',',')} \n"
                print(msg)

    def __init__(self, ano, rel_negociacoes, rel_movimentacoes, rel_ipos):
        self.ano = ano
        self.taxa_b3 = 0.0003
        self.imp_dedo_duro = 0.00005

        self.dir_projeto = os.getcwd()
        self.dir_relatorios = self.dir_projeto + '/relatorios_b3/'
        self.dir_saldos = self.dir_projeto + '/saldo_anos_anteriores/'

        self.negociacoes = self._padronizaNegociacoes(rel_negociacoes)
        self.movimentacoes = self._padronizaMovimentacoes(rel_movimentacoes)
        self.ipos = self._padronizaIpos(rel_ipos)
        self.saldo_ano_anterior = self._padronizaSaldoAnterior()
        self.dados = self._agrupaDados()

        self.rendimentos = None
        self.proventos = None

    def _padronizaNegociacoes(self, nome_arquivo):
        negociacoes = pd.read_excel(
            self.dir_relatorios + nome_arquivo, decimal=',')
        negociacoes = negociacoes[['Instituição', 'Data do Negócio',
                                   'Tipo de Movimentação', 'Código de Negociação', 'Quantidade', 'Preço', 'Valor']]
        negociacoes['Código de Negociação'] = negociacoes['Código de Negociação'].apply(
            self._removeF)  # aplicação da função remove_f na tabela
        return negociacoes

    def _padronizaMovimentacoes(self, nome_arquivo):
        movimentacoes = pd.read_excel(
            self.dir_relatorios + nome_arquivo, decimal=',')
        movimentacoes.drop(['Entrada/Saída'], axis=1, inplace=True)
        movimentacoes['Produto'] = movimentacoes['Produto'].apply(
            lambda x: self._ticker(x))  # Separa o ticker
        movimentacoes.rename(mapper={'Data': 'Data do Negócio', 'Movimentação': 'Tipo de Movimentação',
                             'Produto': 'Código de Negociação', 'Preço unitário': 'Preço', 'Valor da Operação': 'Valor'}, axis=1, inplace=True)
        return movimentacoes

    def _padronizaIpos(self, nome_arquivo):
        ipos = pd.read_excel(self.dir_relatorios + nome_arquivo, decimal=',')
        ipos['Código de Negociação'] = ipos['Código de Negociação'].apply(
            lambda x: self._removeL(x))
        ipos['Tipo de Movimentação'] = 'Compra'
        ipos.rename(
            mapper={'Data de liquidação': 'Data do Negócio'}, axis=1, inplace=True)
        ipos = ipos[['Instituição', 'Data do Negócio', 'Tipo de Movimentação',
                     'Código de Negociação', 'Quantidade', 'Preço', 'Valor']]
        return ipos

    def _padronizaSaldoAnterior(self):
        saldo_ano_anterior = pd.read_excel(
            self.dir_saldos + 'saldo_acoes_' + str(self.ano-1) + '.xlsx', decimal=',')
        saldo_ano_anterior['Data do Negócio'] = '31/12/'+str(self.ano-1)
        saldo_ano_anterior['Tipo de Movimentação'] = 'Compra'
        return saldo_ano_anterior

    def _agrupaDados(self):
        dados = pd.concat([self.negociacoes, self.movimentacoes,
                          self.ipos, self.saldo_ano_anterior])
        dados['Quantidade'] = dados['Quantidade'].astype('int64')
        dados['Preço'][dados['Preço'] == '-'] = 0
        dados['Preço'] = dados['Preço'].astype(float)
        dados['Valor'][dados['Valor'] == '-'] = 0
        dados['Valor'] = dados['Valor'].astype(float)
        dados['Data do Negócio'] = pd.to_datetime(
            dados['Data do Negócio'], dayfirst=True)
        dados = dados.sort_values(
            by=['Data do Negócio'], ascending=True).reset_index(drop=True)
        return dados

    def eventosExoticos(self):
        eventos_exoticos = (
            (self.dados['Tipo de Movimentação'] == 'Atualização') |
            (self.dados['Tipo de Movimentação'] == 'Cisão')
        )
        return self.dados[eventos_exoticos]

    def trataEventosExoticos(self, filtro, coluna, novo_valor):
        self.dados[coluna][filtro] = novo_valor

    def bensDireitos(self):
        instituicoes = self.dados['Instituição'].unique()
        saldo = {}
        negociacoes_instituicao = {}
        saldo_total = pd.DataFrame()

        for instituicao in instituicoes:
            saldo[instituicao] = pd.DataFrame(
                columns=['Instituição', 'Código de Negociação', 'Quantidade', 'Preço', 'Valor'])
            negociacoes_instituicao[instituicao] = self.dados[self.dados['Instituição'] == instituicao]
            tickers = negociacoes_instituicao[instituicao]['Código de Negociação'].unique(
            )

            for ticker in tickers:
                quantidade = 0
                valor = 0
                operacoes = negociacoes_instituicao[instituicao][negociacoes_instituicao[instituicao]
                                                                 ['Código de Negociação'] == ticker]
                operacoes.sort_values(
                    by=['Data do Negócio'], ascending=True).reset_index(drop=True)
                for i in range(len(operacoes)):
                    if operacoes.iloc[i]['Tipo de Movimentação'] == 'Compra':
                        quantidade += operacoes.iloc[i]['Quantidade']
                        valor += operacoes.iloc[i]['Valor']*(1 + self.taxa_b3)
                    elif operacoes.iloc[i]['Tipo de Movimentação'] == 'Venda':
                        if quantidade > 0:
                            valor = (
                                quantidade - operacoes.iloc[i]['Quantidade'])*valor/quantidade
                        quantidade -= operacoes.iloc[i]['Quantidade']
                    elif operacoes.iloc[i]['Tipo de Movimentação'] == 'Desdobro' or operacoes.iloc[i]['Tipo de Movimentação'] == 'Bonificação em Ativos':
                        quantidade += operacoes.iloc[i]['Quantidade']

                if quantidade != 0 and pd.isna(quantidade) == False:
                    nova_linha = {'Instituição': instituicao,
                                  'Código de Negociação': ticker,
                                  'Quantidade': [int(quantidade)],
                                  'Preço': [round(valor/quantidade, 2)],
                                  'Valor': valor
                                  }
                    nova_linha = pd.DataFrame(data=nova_linha)
                    saldo[instituicao] = pd.concat(
                        [saldo[instituicao], nova_linha])
                    saldo[instituicao] = saldo[instituicao][saldo[instituicao]
                                                            ['Quantidade'] > 0]
                    saldo[instituicao].reset_index(drop=True, inplace=True)

            # Insere CNPJ da ação
            saldo[instituicao]['CNPJ'] = saldo[instituicao]['Código de Negociação'].apply(
                lambda x: self._CNPJ(x))

            if saldo[instituicao].empty:
                saldo.pop(instituicao)
            else:
                print(instituicao, '\n')
                self._declaraPapeis(saldo[instituicao], instituicao)
                saldo_total = pd.concat([saldo_total, saldo[instituicao][[
                                        'Instituição', 'Código de Negociação', 'Quantidade', 'Preço', 'Valor']]])

        # Grava as posições do ano em arquivo .xlsx (Excel)
        nome_arquivo = 'saldo_acoes_' + str(self.ano) + '.xlsx'
        saldo_total.to_excel(self.dir_saldos + nome_arquivo,
                             sheet_name='Posições ' + '31.12.' + str(self.ano), index=False)
        # print(f'O arquivo "{nome_arquivo}" com o saldo do ano {self.ano} foi criado na pasta "{self.dir_saldos}"!\nMantenha-o nessa pasta para utilizá-lo novamente no próximo ano.')

    def calculaVendasStocks(self, tipo=None):
        if type(self.rendimentos) != type(pd.DataFrame):
            vendas = self.dados[(self.dados['Tipo de Movimentação'] == 'Venda') & (
                self.dados['Código de Negociação'].isin(cnpjs.STOCKS))]
            vendas = vendas.sort_values(
                by=['Data do Negócio'], ascending=True).reset_index(drop=True)
            vendas['Mês'] = vendas['Data do Negócio'].dt.month

            vendas['Valor'] = vendas['Valor']*(1 - self.taxa_b3)
            vendas['Preço'] = vendas['Valor']/vendas['Quantidade']

            operacoes_ticker = []
            resumo_pre_venda = pd.DataFrame(
                columns=['Quantidade', 'Preço', 'Valor'])

            for registro in vendas.index:
                operacoes_ticker.append(
                    self.dados[self.dados['Código de Negociação'] == vendas['Código de Negociação'].iloc[registro]])
                operacoes_ticker[registro] = operacoes_ticker[registro][operacoes_ticker[registro]
                                                                        ['Data do Negócio'] < vendas['Data do Negócio'].iloc[registro]]
                quantidade = 0
                valor = 0
                for i in range(len(operacoes_ticker[registro])):
                    if operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Compra':
                        quantidade += operacoes_ticker[registro].iloc[i]['Quantidade']
                        valor += operacoes_ticker[registro].iloc[i]['Valor']*(
                            1 + self.taxa_b3)
                        preco_medio_atual = valor/quantidade
                    elif operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Venda':
                        quantidade -= operacoes_ticker[registro].iloc[i]['Quantidade']
                        valor = preco_medio_atual*quantidade
                    elif operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Desdobro' or operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Bonificação em Ativos':
                        quantidade += operacoes_ticker[registro].iloc[i]['Quantidade']
                        preco_medio_atual = valor/quantidade

                if quantidade == 0:
                    nova_linha = {'Quantidade': [0],
                                  'Preço': [0],
                                  'Valor': [0]
                                  }
                else:
                    nova_linha = {'Quantidade': [quantidade],
                                  'Preço': [valor/quantidade],
                                  'Valor': [valor]
                                  }

                nova_linha = pd.DataFrame(data=nova_linha)
                resumo_pre_venda = pd.concat([resumo_pre_venda, nova_linha])

            resumo_pre_venda.reset_index(drop=True, inplace=True)

            realizacoes = vendas.copy()
            realizacoes['Lucro/Prejuizo'] = vendas['Valor'] - \
                resumo_pre_venda['Preço']*vendas['Quantidade']
            realizacoes_por_mes = realizacoes.groupby(
                by='Mês')['Lucro/Prejuizo'].sum()*(1-self.imp_dedo_duro)
            vendas_por_mes = vendas.groupby(by='Mês')['Valor'].sum()
            vendas_por_mes.name = 'Total de Vendas'
            self.rendimentos = pd.concat(
                [vendas_por_mes, realizacoes_por_mes], axis=1)

        if tipo == 'lucro_taxado':
            lucro_isento = self.rendimentos[(self.rendimentos['Total de Vendas'] >= 20000) & (
                self.rendimentos['Lucro/Prejuizo'] >= 0)]
            return lucro_isento.rename(columns={'Lucro/Prejuizo': 'Lucro Taxado'})

        if tipo == 'lucro_isento':
            lucro_isento = self.rendimentos[(self.rendimentos['Total de Vendas'] < 20000) & (
                self.rendimentos['Lucro/Prejuizo'] >= 0)]
            return lucro_isento.rename(columns={'Lucro/Prejuizo': 'Lucro Isento'})

        if tipo == 'lucro_taxado_no_ano':
            lucro_isento = self.rendimentos[(self.rendimentos['Total de Vendas'] >= 20000) & (
                self.rendimentos['Lucro/Prejuizo'] >= 0)]
            return lucro_isento.rename(columns={'Lucro/Prejuizo': 'Lucro Taxado Ano'}).sum().to_frame().rename(columns={0: self.ano})

        if tipo == 'lucro_isento_no_ano':
            lucro_isento = self.rendimentos[(self.rendimentos['Total de Vendas'] < 20000) & (
                self.rendimentos['Lucro/Prejuizo'] >= 0)]
            return lucro_isento.rename(columns={'Lucro/Prejuizo': 'Lucro Isento Ano'}).sum().to_frame().rename(columns={0: self.ano})

        if tipo == 'prejuizo':
            prejuizo = self.rendimentos[self.rendimentos['Lucro/Prejuizo'] < 0]
            return prejuizo.rename(columns={'Lucro/Prejuizo': 'Prejuizo'})

    def calculaVendasFIIs(self, tipo=None):
        if type(self.rendimentos) != type(pd.DataFrame):
            vendas = self.dados[(self.dados['Tipo de Movimentação'] == 'Venda') & (
                self.dados['Código de Negociação'].isin(cnpjs.FIIS))]
            vendas = vendas.sort_values(
                by=['Data do Negócio'], ascending=True).reset_index(drop=True)
            vendas['Mês'] = vendas['Data do Negócio'].dt.month

            vendas['Valor'] = vendas['Valor']*(1 - self.taxa_b3)
            vendas['Preço'] = vendas['Valor']/vendas['Quantidade']

            operacoes_ticker = []
            resumo_pre_venda = pd.DataFrame(
                columns=['Quantidade', 'Preço', 'Valor'])

            for registro in vendas.index:
                operacoes_ticker.append(
                    self.dados[self.dados['Código de Negociação'] == vendas['Código de Negociação'].iloc[registro]])
                operacoes_ticker[registro] = operacoes_ticker[registro][operacoes_ticker[registro]
                                                                        ['Data do Negócio'] < vendas['Data do Negócio'].iloc[registro]]
                quantidade = 0
                valor = 0
                for i in range(len(operacoes_ticker[registro])):
                    if operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Compra':
                        quantidade += operacoes_ticker[registro].iloc[i]['Quantidade']
                        valor += operacoes_ticker[registro].iloc[i]['Valor']*(
                            1 + self.taxa_b3)
                        preco_medio_atual = valor/quantidade
                    elif operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Venda':
                        quantidade -= operacoes_ticker[registro].iloc[i]['Quantidade']
                        valor = preco_medio_atual*quantidade
                    elif operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Desdobro' or operacoes_ticker[registro].iloc[i]['Tipo de Movimentação'] == 'Bonificação em Ativos':
                        quantidade += operacoes_ticker[registro].iloc[i]['Quantidade']
                        preco_medio_atual = valor/quantidade

                if quantidade == 0:
                    nova_linha = {'Quantidade': [0],
                                  'Preço': [0],
                                  'Valor': [0]
                                  }
                else:
                    nova_linha = {'Quantidade': [quantidade],
                                  'Preço': [valor/quantidade],
                                  'Valor': [valor]
                                  }

                nova_linha = pd.DataFrame(data=nova_linha)
                resumo_pre_venda = pd.concat([resumo_pre_venda, nova_linha])

            resumo_pre_venda.reset_index(drop=True, inplace=True)

            realizacoes = vendas.copy()
            realizacoes['Lucro/Prejuizo'] = vendas['Valor'] - \
                resumo_pre_venda['Preço']*vendas['Quantidade']
            realizacoes_por_mes = realizacoes.groupby(
                by='Mês')['Lucro/Prejuizo'].sum()*(1-self.imp_dedo_duro)
            vendas_por_mes = vendas.groupby(by='Mês')['Valor'].sum()
            vendas_por_mes.name = 'Total de Vendas'
            self.rendimentos = pd.concat(
                [vendas_por_mes, realizacoes_por_mes], axis=1)

        if tipo == 'lucro_taxado':
            lucro_isento = self.rendimentos[(
                self.rendimentos['Lucro/Prejuizo'] >= 0)]
            return lucro_isento.rename(columns={'Lucro/Prejuizo': 'Lucro Taxado'})

        if tipo == 'lucro_taxado_no_ano':
            lucro_isento = self.rendimentos[(
                self.rendimentos['Lucro/Prejuizo'] >= 0)]
            return lucro_isento.rename(columns={'Lucro/Prejuizo': 'Lucro Taxado Ano'}).sum().to_frame().rename(columns={0: self.ano})

        if tipo == 'prejuizo':
            prejuizo = self.rendimentos[self.rendimentos['Lucro/Prejuizo'] < 0]
            return prejuizo.rename(columns={'Lucro/Prejuizo': 'Prejuizo'})

    def somaProventos(self, tipo=None):
        if type(self.proventos) != type(pd.DataFrame):
            filtro_prov = (self.dados['Tipo de Movimentação'] == 'Dividendo') | (
                self.dados['Tipo de Movimentação'] == 'Juros Sobre Capital Próprio') | (
                self.dados['Tipo de Movimentação'] == 'Rendimento')
            proventos = self.dados[filtro_prov]
            proventos = proventos.groupby(by=['Tipo de Movimentação', 'Código de Negociação'])[
                'Valor'].sum().to_frame().reset_index()
            proventos['CNPJ'] = proventos['Código de Negociação'].apply(
                lambda x: self._CNPJ(x))
            self.proventos = proventos

        if tipo == 'rendimento':
            return self.proventos[self.proventos['Tipo de Movimentação'] == 'Rendimento'][['Código de Negociação', 'Valor', 'CNPJ']]

        if tipo == 'dividendo':
            return self.proventos[self.proventos['Tipo de Movimentação'] == 'Dividendo'][['Código de Negociação', 'Valor', 'CNPJ']]

        if tipo == 'jcp':
            return self.proventos[self.proventos['Tipo de Movimentação'] == 'Juros Sobre Capital Próprio'][['Código de Negociação', 'Valor', 'CNPJ']]
