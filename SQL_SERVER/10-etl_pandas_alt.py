#pip install pandas numpy pyodbc sqlalchemy faker jupyter

# ============================================================
# IMPORTS
# ============================================================

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime
import urllib

# ============================================================
# CONEXAO SQL SERVER
# ============================================================

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=FatecShop2;"
    "Trusted_Connection=yes;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    fast_executemany=True 
)

# ============================================================
# LEITURA TABELAS TRANSACIONAIS
# ============================================================

clientes = pd.read_sql(
    "SELECT * FROM clientes",
    engine
)

enderecos = pd.read_sql(
    "SELECT * FROM enderecos_clientes",
    engine
)

produtos = pd.read_sql(
    "SELECT * FROM produtos",
    engine
)

categorias = pd.read_sql(
    "SELECT * FROM categorias",
    engine
)

subcategorias = pd.read_sql(
    "SELECT * FROM subcategorias",
    engine
)

vendedores = pd.read_sql(
    "SELECT * FROM vendedores",
    engine
)

pedidos = pd.read_sql(
    "SELECT * FROM pedidos",
    engine
)

itens_pedido = pd.read_sql(
    "SELECT * FROM itens_pedido",
    engine
)

pagamentos = pd.read_sql(
    "SELECT * FROM pagamentos",
    engine
)

entregas = pd.read_sql(
    "SELECT * FROM entregas",
    engine
)

avaliacoes = pd.read_sql(
    "SELECT * FROM avaliacoes",
    engine
)

# ============================================================
# LIMPEZA DW
# ============================================================

with engine.begin() as conn:

    conn.exec_driver_sql(
        "TRUNCATE TABLE dw.fato_vendas"
    )

    conn.exec_driver_sql(
        "DELETE FROM dw.dim_cliente"
    )

    conn.exec_driver_sql(
        "DELETE FROM dw.dim_produto"
    )

    conn.exec_driver_sql(
        "DELETE FROM dw.dim_vendedor"
    )

    conn.exec_driver_sql(
        "DELETE FROM dw.dim_pagamento"
    )

    conn.exec_driver_sql(
        "DELETE FROM dw.dim_entrega"
    )

    conn.exec_driver_sql(
        "DELETE FROM dw.dim_data"
    )

    conn.exec_driver_sql(
        "DBCC CHECKIDENT ('dw.dim_cliente', RESEED, 0)"
    )

    conn.exec_driver_sql(
        "DBCC CHECKIDENT ('dw.dim_produto', RESEED, 0)"
    )

    conn.exec_driver_sql(
        "DBCC CHECKIDENT ('dw.dim_vendedor', RESEED, 0)"
    )

    conn.exec_driver_sql(
        "DBCC CHECKIDENT ('dw.dim_pagamento', RESEED, 0)"
    )

    conn.exec_driver_sql(
        "DBCC CHECKIDENT ('dw.dim_entrega', RESEED, 0)"
    )

print("LIMPEZA FINALIZADA")

# ============================================================
# DIM_CLIENTE
# ============================================================

print("Carregando dim_cliente...")

dim_cliente = clientes.merge(
    enderecos[
        enderecos['principal_entrega'] == 1
    ],
    on='id_cliente',
    how='left'
)

dim_cliente['idade'] = (
    datetime.now().year
    -
    pd.to_datetime(
        dim_cliente['data_nascimento']
    ).dt.year
)

dim_cliente['faixa_etaria'] = np.select(
    [
        dim_cliente['idade'] < 25,
        dim_cliente['idade'] < 35,
        dim_cliente['idade'] < 45,
        dim_cliente['idade'] < 60
    ],
    [
        '18-24',
        '25-34',
        '35-44',
        '45-59'
    ],
    default='60+'
)

dim_cliente['faixa_renda'] = np.select(
    [
        dim_cliente['renda_mensal'] < 3000,
        dim_cliente['renda_mensal'] < 8000,
        dim_cliente['renda_mensal'] < 15000
    ],
    [
        'Baixa',
        'Media',
        'Alta'
    ],
    default='Premium'
)

dim_cliente['regiao'] = np.select(
    [
        dim_cliente['estado'].isin(['SP','RJ','MG','ES']),
        dim_cliente['estado'].isin(['RS','SC','PR']),
        dim_cliente['estado'].isin(['BA','PE','CE']),
        dim_cliente['estado'].isin(['GO','MT','MS','DF'])
    ],
    [
        'Sudeste',
        'Sul',
        'Nordeste',
        'Centro-Oeste'
    ],
    default='Outros'
)

dim_cliente = dim_cliente[[
    'id_cliente',
    'nome_cliente',
    'sexo',
    'data_nascimento',
    'idade',
    'faixa_etaria',
    'renda_mensal',
    'faixa_renda',
    'cidade',
    'estado',
    'regiao',
    'data_cadastro'
]]

dim_cliente = dim_cliente.rename(columns={
    'id_cliente':'id_cliente_origem'
})

dim_cliente.to_sql(
    'dim_cliente',
    con=engine,
    schema='dw',
    if_exists='append',
    index=False,
    chunksize=1000
)

print(f"dim_cliente: {len(dim_cliente)} linhas")

# ============================================================
# DIM_PRODUTO
# ============================================================

print("Carregando dim_produto...")

dim_produto = (
    produtos
    .merge(
        subcategorias,
        on='id_subcategoria'
    )
    .merge(
        categorias,
        on='id_categoria'
    )
)

dim_produto['faixa_preco'] = np.select(
    [
        dim_produto['preco'] < 100,
        dim_produto['preco'] < 500,
        dim_produto['preco'] < 2000,
        dim_produto['preco'] < 5000
    ],
    [
        'Ate 100',
        '100-499',
        '500-1999',
        '2000-4999'
    ],
    default='5000+'
)

dim_produto = dim_produto[[
    'id_produto',
    'nome_produto',
    'marca',
    'nome_categoria',
    'nome_subcategoria',
    'preco',
    'faixa_preco',
    'ativo'
]]

dim_produto = dim_produto.rename(columns={
    'id_produto':'id_produto_origem',
    'nome_categoria':'categoria',
    'nome_subcategoria':'subcategoria',
    'preco':'preco_base'
})

dim_produto.to_sql(
    'dim_produto',
    con=engine,
    schema='dw',
    if_exists='append',
    index=False,
    chunksize=1000
)

print(f"dim_produto: {len(dim_produto)} linhas")

# ============================================================
# DIM_VENDEDOR
# ============================================================

print("Carregando dim_vendedor...")

dim_vendedor = vendedores.copy()

dim_vendedor['regiao'] = np.select(
    [
        dim_vendedor['estado'].isin(['SP','RJ','MG','ES']),
        dim_vendedor['estado'].isin(['RS','SC','PR']),
        dim_vendedor['estado'].isin(['BA','PE','CE']),
        dim_vendedor['estado'].isin(['GO','MT','MS','DF'])
    ],
    [
        'Sudeste',
        'Sul',
        'Nordeste',
        'Centro-Oeste'
    ],
    default='Outros'
)

dim_vendedor = dim_vendedor[[
    'id_vendedor',
    'nome_vendedor',
    'cidade',
    'estado',
    'regiao',
    'data_entrada'
]]

dim_vendedor = dim_vendedor.rename(columns={
    'id_vendedor':'id_vendedor_origem'
})

dim_vendedor.to_sql(
    'dim_vendedor',
    con=engine,
    schema='dw',
    if_exists='append',
    index=False,
    chunksize=1000
)

print(f"dim_vendedor: {len(dim_vendedor)} linhas")

# ============================================================
# DIM_PAGAMENTO
# ============================================================

print("Carregando dim_pagamento...")

dim_pagamento = pagamentos.copy()

dim_pagamento['faixa_parcelas'] = np.select(
    [
        dim_pagamento['parcelas'] == 1,
        dim_pagamento['parcelas'] <= 3,
        dim_pagamento['parcelas'] <= 6
    ],
    [
        '1x',
        '2-3x',
        '4-6x'
    ],
    default='7+x'
)

dim_pagamento = dim_pagamento[[
    'tipo_pagamento',
    'faixa_parcelas'
]].drop_duplicates()

dim_pagamento.to_sql(
    'dim_pagamento',
    con=engine,
    schema='dw',
    if_exists='append',
    index=False
)

print(f"dim_pagamento: {len(dim_pagamento)} linhas")

# ============================================================
# DIM_ENTREGA
# ============================================================

print("Carregando dim_entrega...")

dim_entrega = entregas.copy()

dim_entrega['prazo_entrega'] = (
    pd.to_datetime(
        dim_entrega['data_entrega_real']
    )
    -
    pd.to_datetime(
        dim_entrega['data_envio']
    )
).dt.days

dim_entrega['faixa_prazo'] = np.select(
    [
        dim_entrega['prazo_entrega'] <= 3,
        dim_entrega['prazo_entrega'] <= 7,
        dim_entrega['prazo_entrega'] <= 15
    ],
    [
        'Ate 3 dias',
        '4-7 dias',
        '8-15 dias'
    ],
    default='15+ dias'
)

dim_entrega['entrega_atrasada'] = np.where(
    pd.to_datetime(
        dim_entrega['data_entrega_real']
    )
    >
    pd.to_datetime(
        dim_entrega['data_entrega_prevista']
    ),
    'Sim',
    'Nao'
)

dim_entrega = dim_entrega[[
    'tipo_entrega',
    'faixa_prazo',
    'entrega_atrasada'
]].drop_duplicates()

dim_entrega.to_sql(
    'dim_entrega',
    con=engine,
    schema='dw',
    if_exists='append',
    index=False
)

print(f"dim_entrega: {len(dim_entrega)} linhas")

# ============================================================
# DIM_DATA
# ============================================================

print("Carregando dim_data...")

datas = pd.date_range(
    start='2022-01-01',
    end='2030-12-31'
)

dim_data = pd.DataFrame()

dim_data['data_completa'] = datas

dim_data['sk_data'] = (
    dim_data['data_completa']
    .dt.strftime('%Y%m%d')
    .astype(int)
)

dim_data['dia'] = (
    dim_data['data_completa']
    .dt.day
)

dim_data['nome_dia_semana'] = (
    dim_data['data_completa']
    .dt.day_name()
)

dim_data['semana_ano'] = (
    dim_data['data_completa']
    .dt.isocalendar().week
)

dim_data['mes'] = (
    dim_data['data_completa']
    .dt.month
)

dim_data['nome_mes'] = (
    dim_data['data_completa']
    .dt.month_name()
)

dim_data['trimestre'] = (
    dim_data['data_completa']
    .dt.quarter
)

dim_data['semestre'] = np.where(
    dim_data['mes'] <= 6,
    1,
    2
)

dim_data['ano'] = (
    dim_data['data_completa']
    .dt.year
)

dim_data['fim_semana'] = np.where(
    dim_data['nome_dia_semana'].isin([
        'Saturday',
        'Sunday'
    ]),
    1,
    0
)

dim_data = dim_data[[
    'sk_data',
    'data_completa',
    'dia',
    'nome_dia_semana',
    'semana_ano',
    'mes',
    'nome_mes',
    'trimestre',
    'semestre',
    'ano',
    'fim_semana'
]]

dim_data.to_sql(
    'dim_data',
    con=engine,
    schema='dw',
    if_exists='append',
    index=False,
    chunksize=1000
)

print(f"dim_data: {len(dim_data)} linhas")

# ============================================================
# RELEITURA DIMENSOES
# ============================================================

dim_cliente_dw = pd.read_sql(
    "SELECT sk_cliente, id_cliente_origem FROM dw.dim_cliente",
    engine
)

dim_produto_dw = pd.read_sql(
    "SELECT sk_produto, id_produto_origem FROM dw.dim_produto",
    engine
)

dim_vendedor_dw = pd.read_sql(
    "SELECT sk_vendedor, id_vendedor_origem FROM dw.dim_vendedor",
    engine
)

dim_pagamento_dw = pd.read_sql(
    "SELECT * FROM dw.dim_pagamento",
    engine
)

dim_entrega_dw = pd.read_sql(
    "SELECT * FROM dw.dim_entrega",
    engine
)

# ============================================================
# FATO_VENDAS
# ============================================================

print("Montando fato_vendas...")

fato = (
    itens_pedido

    .merge(
        pedidos,
        on='id_pedido',
        how='inner'
    )

    .merge(
        produtos[['id_produto','custo']],
        on='id_produto',
        how='inner'
    )

    .merge(
        pagamentos,
        on='id_pedido',
        how='inner'
    )

    .merge(
        entregas,
        on='id_pedido',
        how='inner'
    )

    .merge(
        avaliacoes,
        on='id_pedido',
        how='left'
    )
)

print(f"Fato base: {len(fato)} linhas")

# ============================================================
# CALCULOS
# ============================================================

fato['valor_bruto'] = (
    fato['quantidade']
    * fato['preco_unitario']
)

fato['valor_liquido'] = (
    fato['valor_bruto']
    - fato['desconto']
    + fato['valor_frete']
)

fato['custo_produto'] = (
    fato['custo']
    * fato['quantidade']
)

fato['lucro'] = (
    fato['valor_liquido']
    - fato['custo_produto']
)

fato['prazo_entrega_dias'] = (
    pd.to_datetime(
        fato['data_entrega_real']
    )
    -
    pd.to_datetime(
        fato['data_envio']
    )
).dt.days

fato['faixa_parcelas'] = np.select(
    [
        fato['parcelas'] == 1,
        fato['parcelas'] <= 3,
        fato['parcelas'] <= 6
    ],
    [
        '1x',
        '2-3x',
        '4-6x'
    ],
    default='7+x'
)

fato['faixa_prazo'] = np.select(
    [
        fato['prazo_entrega_dias'] <= 3,
        fato['prazo_entrega_dias'] <= 7,
        fato['prazo_entrega_dias'] <= 15
    ],
    [
        'Ate 3 dias',
        '4-7 dias',
        '8-15 dias'
    ],
    default='15+ dias'
)

fato['entrega_atrasada'] = np.where(
    pd.to_datetime(
        fato['data_entrega_real']
    )
    >
    pd.to_datetime(
        fato['data_entrega_prevista']
    ),
    'Sim',
    'Nao'
)

fato['sk_data'] = (
    pd.to_datetime(
        fato['data_pedido']
    )
    .dt.strftime('%Y%m%d')
    .astype(int)
)

# ============================================================
# LOOKUPS
# ============================================================

fato = fato.merge(
    dim_cliente_dw,
    left_on='id_cliente',
    right_on='id_cliente_origem',
    how='inner'
)

fato = fato.merge(
    dim_produto_dw,
    left_on='id_produto',
    right_on='id_produto_origem',
    how='inner'
)

fato = fato.merge(
    dim_vendedor_dw,
    left_on='id_vendedor',
    right_on='id_vendedor_origem',
    how='inner'
)

fato = fato.merge(
    dim_pagamento_dw,
    on=[
        'tipo_pagamento',
        'faixa_parcelas'
    ],
    how='inner'
)

fato = fato.merge(
    dim_entrega_dw,
    on=[
        'tipo_entrega',
        'faixa_prazo',
        'entrega_atrasada'
    ],
    how='inner'
)

print(f"Fato final: {len(fato)} linhas")

# ============================================================
# DATAFRAME FINAL
# ============================================================

fato_vendas = fato[[
    'sk_cliente',
    'sk_produto',
    'sk_vendedor',
    'sk_pagamento',
    'sk_entrega',
    'sk_data',
    'id_pedido',
    'quantidade',
    'preco_unitario',
    'valor_bruto',
    'desconto',
    'valor_frete',
    'valor_liquido',
    'custo_produto',
    'lucro',
    'prazo_entrega_dias',
    'nota'
]]

fato_vendas = fato_vendas.rename(columns={
    'id_pedido':'id_pedido_origem',
    'quantidade':'quantidade_itens',
    'nota':'avaliacao'
})

# ============================================================
# CARGA FATO
# ============================================================

print("Gravando fato_vendas...")

fato_vendas.to_sql(
    'fato_vendas',
    con=engine,
    schema='dw',
    if_exists='append',
    index=False,
    chunksize=50000
)

print(f"fato_vendas: {len(fato_vendas)} linhas")

print("=========================================")
print("CARGA DW FINALIZADA COM SUCESSO")
print("=========================================")