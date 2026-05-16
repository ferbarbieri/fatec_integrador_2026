import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine, text
import urllib

# 1. CONFIGURAÇÃO DA CONEXÃO

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=FatecShop;"
    "Trusted_Connection=yes;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}", 
    fast_executemany=True
)

def executar_carga_dw():
    print('=========================================')
    print('INICIANDO CARGA FULL DW VIA PYTHON')
    print('=========================================')
    
    with engine.begin() as conn:
        # =====================================================
        #  LIMPEZA FATO E DIMENSÕES / RESET IDENTITY
        # =====================================================
        print("Limpando tabelas e resetando chaves primárias...")
        conn.execute(text("TRUNCATE TABLE dw.fato_vendas;"))
        
        dimensoes = ['dw.dim_cliente', 'dw.dim_produto', 'dw.dim_vendedor', 'dw.dim_pagamento', 'dw.dim_entrega', 'dw.dim_data']
        for dim in dimensoes:
            conn.execute(text(f"DELETE FROM {dim};"))
            
        # O SQL Server não permite DBCC CHECKIDENT em tabelas sem coluna IDENTITY (como dim_data geralmente é)
        dims_com_identity = ['dw.dim_cliente', 'dw.dim_produto', 'dw.dim_vendedor', 'dw.dim_pagamento', 'dw.dim_entrega']
        for dim in dims_com_identity:
            conn.execute(text(f"DBCC CHECKIDENT ('{dim}', RESEED, 0);"))

        # =====================================================
        #  LEITURA DAS TABELAS DE ORIGEM
        # =====================================================
        print("Extraindo dados da origem...")
        df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
        df_enderecos = pd.read_sql("SELECT * FROM enderecos_clientes", conn)
        df_produtos = pd.read_sql("SELECT * FROM produtos", conn)
        df_subcategorias = pd.read_sql("SELECT * FROM subcategorias", conn)
        df_categorias = pd.read_sql("SELECT * FROM categorias", conn)
        df_vendedores = pd.read_sql("SELECT * FROM vendedores", conn)
        df_pagamentos = pd.read_sql("SELECT * FROM pagamentos", conn)
        df_entregas = pd.read_sql("SELECT * FROM entregas", conn)
        df_itens_pedido = pd.read_sql("SELECT * FROM itens_pedido", conn)
        df_pedidos = pd.read_sql("SELECT * FROM pedidos", conn)
        df_avaliacoes = pd.read_sql("SELECT * FROM avaliacoes", conn)

    # Obter data atual para cálculo de idade
    hoje = datetime.now()

    # =====================================================
    #  DIM_CLIENTE
    # =====================================================
    print('Carregando dim_cliente...')
    df_end_filtrado = df_enderecos[df_enderecos['principal_entrega'] == 1]
    dim_cliente = pd.merge(df_clientes, df_end_filtrado, on='id_cliente', how='left')
    
    # Cálculos de idade e faixas
    dim_cliente['data_nascimento'] = pd.to_datetime(dim_cliente['data_nascimento'])
    dim_cliente['idade'] = dim_cliente['data_nascimento'].apply(lambda x: hoje.year - x.year - ((hoje.month, hoje.day) < (x.month, x.day)) if pd.notnull(x) else np.nan)
    
    dim_cliente['faixa_etaria'] = np.select(
        [dim_cliente['idade'] < 25, dim_cliente['idade'] < 35, dim_cliente['idade'] < 45, dim_cliente['idade'] < 60],
        ['18-24', '25-34', '35-44', '45-59'], default='60+'
    )
    
    dim_cliente['faixa_renda'] = np.select(
        [dim_cliente['renda_mensal'] < 3000, dim_cliente['renda_mensal'] < 8000, dim_cliente['renda_mensal'] < 15000],
        ['Baixa', 'Media', 'Alta'], default='Premium'
    )
    
    dim_cliente['regiao'] = np.select(
        [dim_cliente['estado'].isin(['SP','RJ','MG','ES']), dim_cliente['estado'].isin(['RS','SC','PR']), 
         dim_cliente['estado'].isin(['BA','PE','CE']), dim_cliente['estado'].isin(['GO','MT','MS','DF'])],
        ['Sudeste', 'Sul', 'Nordeste', 'Centro-Oeste'], default='Outros'
    )
    
    dim_cliente_final = dim_cliente[[
        'id_cliente', 'nome_cliente', 'sexo', 'data_nascimento', 'idade', 
        'faixa_etaria', 'renda_mensal', 'faixa_renda', 'cidade', 'estado', 'regiao', 'data_cadastro'
    ]].rename(columns={'id_cliente': 'id_cliente_origem'})
    
    dim_cliente_final.to_sql('dim_cliente', con=engine, schema='dw', if_exists='append', index=False)

    # =====================================================
    #  DIM_PRODUTO
    # =====================================================
    print('Carregando dim_produto...')
    dim_produto = df_produtos.merge(df_subcategorias, on='id_subcategoria').merge(df_categorias, on='id_categoria')
    
    dim_produto['faixa_preco'] = np.select(
        [dim_produto['preco'] < 100, dim_produto['preco'] < 500, dim_produto['preco'] < 2000, dim_produto['preco'] < 5000],
        ['Ate 100', '100-499', '500-1999', '2000-4999'], default='5000+'
    )
    
    dim_produto_final = dim_produto[[
        'id_produto', 'nome_produto', 'marca', 'nome_categoria', 'nome_subcategoria', 'preco', 'faixa_preco', 'ativo'
    ]].rename(columns={'id_produto': 'id_produto_origem', 'nome_categoria': 'categoria', 'nome_subcategoria': 'subcategoria', 'preco': 'preco_base'})
    
    dim_produto_final.to_sql('dim_produto', con=engine, schema='dw', if_exists='append', index=False)

    # =====================================================
    #  DIM_VENDEDOR
    # =====================================================
    print('Carregando dim_vendedor...')
    df_vendedores['regiao'] = np.select(
        [df_vendedores['estado'].isin(['SP','RJ','MG','ES']), df_vendedores['estado'].isin(['RS','SC','PR']), 
         df_vendedores['estado'].isin(['BA','PE','CE']), df_vendedores['estado'].isin(['GO','MT','MS','DF'])],
        ['Sudeste', 'Sul', 'Nordeste', 'Centro-Oeste'], default='Outros'
    )
    
    dim_vendedor_final = df_vendedores[[
        'id_vendedor', 'nome_vendedor', 'cidade', 'estado', 'regiao', 'data_entrada'
    ]].rename(columns={'id_vendedor': 'id_vendedor_origem'})
    
    dim_vendedor_final.to_sql('dim_vendedor', con=engine, schema='dw', if_exists='append', index=False)

    # =====================================================
    #  DIM_PAGAMENTO
    # =====================================================
    print('Carregando dim_pagamento...')
    dim_pagamento = df_pagamentos[['tipo_pagamento', 'parcelas']].copy()
    dim_pagamento['faixa_parcelas'] = np.select(
        [dim_pagamento['parcelas'] == 1, dim_pagamento['parcelas'] <= 3, dim_pagamento['parcelas'] <= 6],
        ['1x', '2-3x', '4-6x'], default='7+x'
    )
    dim_pagamento_final = dim_pagamento[['tipo_pagamento', 'faixa_parcelas']].drop_duplicates()
    
    dim_pagamento_final.to_sql('dim_pagamento', con=engine, schema='dw', if_exists='append', index=False)

    # =====================================================
    #  DIM_ENTREGA
    # =====================================================
    print('Carregando dim_entrega...')
    dim_entrega = df_entregas[['tipo_entrega', 'data_envio', 'data_entrega_real', 'data_entrega_prevista']].copy()
    
    dim_entrega['data_envio'] = pd.to_datetime(dim_entrega['data_envio'])
    dim_entrega['data_entrega_real'] = pd.to_datetime(dim_entrega['data_entrega_real'])
    dim_entrega['data_entrega_prevista'] = pd.to_datetime(dim_entrega['data_entrega_prevista'])
    
    prazo_dias = (dim_entrega['data_entrega_real'] - dim_entrega['data_envio']).dt.days
    dim_entrega['faixa_prazo'] = np.select(
        [prazo_dias <= 3, prazo_dias <= 7, prazo_dias <= 15],
        ['Ate 3 dias', '4-7 dias', '8-15 dias'], default='15+ dias'
    )
    
    dim_entrega['entrega_atrasada'] = np.where(dim_entrega['data_entrega_real'] > dim_entrega['data_entrega_prevista'], 'Sim', 'Nao')
    dim_entrega_final = dim_entrega[['tipo_entrega', 'faixa_prazo', 'entrega_atrasada']].drop_duplicates()
    
    dim_entrega_final.to_sql('dim_entrega', con=engine, schema='dw', if_exists='append', index=False)

    # =====================================================
    #  DIM_DATA (Geração de Calendário Dinâmico)
    # =====================================================
    print('Carregando dim_data...')
    datas_ref = pd.date_range(start='2022-01-01', end='2030-12-31', freq='D')
    
    dim_data_final = pd.DataFrame({
        'sk_data': datas_ref.strftime('%Y%m%d').astype(int),
        'data_completa': datas_ref.date,
        'dia': datas_ref.day,
        'nome_dia_semana': datas_ref.strftime('%A'), # Nome em inglês, para bater com o SQL original
        'semana_ano': datas_ref.isocalendar().week.astype(int),
        'mes': datas_ref.month,
        'nome_mes': datas_ref.strftime('%B'),
        'trimestre': datas_ref.quarter,
        'semestre': np.where(datas_ref.month <= 6, 1, 2),
        'ano': datas_ref.year,
        'fim_semana': np.where(datas_ref.dayofweek.isin([5, 6]), 1, 0) # 5=Sábado, 6=Domingo
    })
    
    dim_data_final.to_sql('dim_data', con=engine, schema='dw', if_exists='append', index=False)

    # =====================================================
    #  RECUPERAR SURROGATE KEYS GERADAS PARA A FATO
    # =====================================================
    # Como as PKs das dimensões no banco são Identity, precisamos ler o que foi gravado nelas para fazer o DE-PARA
    with engine.begin() as conn:
        db_dim_cliente = pd.read_sql("SELECT sk_cliente, id_cliente_origem FROM dw.dim_cliente", conn)
        db_dim_produto = pd.read_sql("SELECT sk_produto, id_produto_origem FROM dw.dim_produto", conn)
        db_dim_vendedor = pd.read_sql("SELECT sk_vendedor, id_vendedor_origem FROM dw.dim_vendedor", conn)
        db_dim_pagamento = pd.read_sql("SELECT sk_pagamento, tipo_pagamento, faixa_parcelas FROM dw.dim_pagamento", conn)
        db_dim_entrega = pd.read_sql("SELECT sk_entrega, tipo_entrega, faixa_prazo, entrega_atrasada FROM dw.dim_entrega", conn)

    # =====================================================
    #  FATO_VENDAS
    # =====================================================
    print('Carregando fato_vendas...')
    
    # Joins equivalentes aos INNER e LEFT JOINs da Origem
    fato = df_itens_pedido.merge(df_pedidos, on='id_pedido') \
                          .merge(df_produtos, on='id_produto') \
                          .merge(df_pagamentos, on='id_pedido') \
                          .merge(df_entregas, on='id_pedido') \
                          .merge(df_avaliacoes, on='id_pedido', how='left')

    # Cálculos das métricas locais antes de cruzar com as SKs das dimensões
    fato['data_pedido'] = pd.to_datetime(fato['data_pedido'])
    fato['sk_data'] = fato['data_pedido'].dt.strftime('%Y%m%d').astype(int)
    
    fato['valor_bruto'] = fato['quantidade'] * fato['preco_unitario']
    fato['valor_liquido'] = fato['valor_bruto'] - fato['desconto'] + fato['valor_frete']
    fato['custo_produto'] = fato['custo'] * fato['quantidade']
    fato['lucro'] = fato['valor_liquido'] - fato['custo_produto']
    
    # Diferença de dias para prazo
    fato['data_envio'] = pd.to_datetime(fato['data_envio'])
    fato['data_entrega_real'] = pd.to_datetime(fato['data_entrega_real'])
    fato['data_entrega_prevista'] = pd.to_datetime(fato['data_entrega_prevista'])
    fato['prazo_entrega_dias'] = (fato['data_entrega_real'] - fato['data_envio']).dt.days
    
    # Regras das faixas temporárias para bater com os Joins das dimensões de pagamento e entrega
    fato['tmp_faixa_parcelas'] = np.select(
        [fato['parcelas'] == 1, fato['parcelas'] <= 3, fato['parcelas'] <= 6],
        ['1x', '2-3x', '4-6x'], default='7+x'
    )
    fato['tmp_faixa_prazo'] = np.select(
        [fato['prazo_entrega_dias'] <= 3, fato['prazo_entrega_dias'] <= 7, fato['prazo_entrega_dias'] <= 15],
        ['Ate 3 dias', '4-7 dias', '8-15 dias'], default='15+ dias'
    )
    fato['tmp_entrega_atrasada'] = np.where(fato['data_entrega_real'] > fato['data_entrega_prevista'], 'Sim', 'Nao')

    # Mapeamento (Join) para as Surrogate Keys (SKs) das tabelas finais do DW
    fato = fato.merge(db_dim_cliente, left_on='id_cliente', right_on='id_cliente_origem')
    fato = fato.merge(db_dim_produto, left_on='id_produto', right_on='id_produto_origem')
    fato = fato.merge(db_dim_vendedor, left_on='id_vendedor', right_on='id_vendedor_origem')
    
    fato = fato.merge(db_dim_pagamento, left_on=['tipo_pagamento', 'tmp_faixa_parcelas'], right_on=['tipo_pagamento', 'faixa_parcelas'])
    fato = fato.merge(db_dim_entrega, left_on=['tipo_entrega', 'tmp_faixa_prazo', 'tmp_entrega_atrasada'], right_on=['tipo_entrega', 'faixa_prazo', 'entrega_atrasada'])

    # Seleção e renomeação final das colunas para a tabela fato_vendas
    fato_vendas_final = fato[[
        'sk_cliente', 'sk_produto', 'sk_vendedor', 'sk_pagamento', 'sk_entrega', 'sk_data',
        'id_pedido', 'quantidade', 'preco_unitario', 'valor_bruto', 'desconto', 'valor_frete',
        'valor_liquido', 'custo_produto', 'lucro', 'prazo_entrega_dias', 'nota'
    ]].rename(columns={'id_pedido': 'id_pedido_origem', 'quantidade': 'quantidade_itens', 'nota': 'avaliacao'})

    fato_vendas_final.to_sql('fato_vendas', con=engine, schema='dw', if_exists='append', index=False, chunksize=50000)

    print('=========================================')
    print('CARGA FINALIZADA COM SUCESSO')
    print('=========================================')

if __name__ == '__main__':
    executar_carga_dw()