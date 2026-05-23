import random
from datetime import timedelta

import pandas as pd
import pyodbc
from faker import Faker

fake = Faker('pt_BR')

# =========================================================
# CONEXAO
# =========================================================

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\MSSQLLocalDB;'
    'DATABASE=FatecShop2;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# =========================================================
# CONFIG
# =========================================================

QTD_PEDIDOS = 100000

# =========================================================
# DOMINIOS
# =========================================================

status_pedido = [
    'Entregue',
    'Cancelado',
    'Em Transporte',
    'Processando'
]

formas_pagamento = [
    'Cartao Credito',
    'PIX',
    'Boleto',
    'Cartao Debito'
]

# =========================================================
# CARREGAR IDS
# =========================================================

clientes_ids = pd.read_sql(
    'SELECT id_cliente FROM clientes',
    conn
)['id_cliente'].tolist()

vendedores_ids = pd.read_sql(
    'SELECT id_vendedor FROM vendedores',
    conn
)['id_vendedor'].tolist()

produtos_df = pd.read_sql(
    '''
    SELECT
        id_produto,
        preco,
        custo
    FROM produtos
    ''',
    conn
)

# =========================================================
# PEDIDOS
# =========================================================

print('Gerando pedidos...')

for i in range(QTD_PEDIDOS):

    id_cliente = random.choice(clientes_ids)

    data_pedido = fake.date_time_between(
        start_date='-2y',
        end_date='now'
    )

    status = random.choices(
        status_pedido,
        weights=[75, 5, 10, 10]
    )[0]

    # =====================================================
    # PEDIDO
    # =====================================================

    cursor.execute(
        """
        INSERT INTO pedidos (
            id_cliente,
            data_pedido,
            status_pedido
        )
        OUTPUT INSERTED.id_pedido
        VALUES (?, ?, ?)
        """,
        id_cliente,
        data_pedido,
        status
    )

    id_pedido = cursor.fetchone()[0]

    # =====================================================
    # ITENS
    # =====================================================

    qtd_itens = random.randint(1, 5)

    total_pedido = 0

    for _ in range(qtd_itens):

        produto = produtos_df.sample(1).iloc[0]

        quantidade = random.randint(1, 3)

        desconto = round(
            random.uniform(0, 80),
            2
        )

        preco_unitario = float(produto['preco'])

        total_item = (
            preco_unitario * quantidade
        ) - desconto

        total_pedido += total_item

        cursor.execute(
            """
            INSERT INTO itens_pedido (
                id_pedido,
                id_produto,
                id_vendedor,
                quantidade,
                preco_unitario,
                desconto
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            id_pedido,
            int(produto['id_produto']),
            random.choice(vendedores_ids),
            quantidade,
            preco_unitario,
            desconto
        )

    # =====================================================
    # PAGAMENTO
    # =====================================================

    forma_pagamento = random.choices(
        formas_pagamento,
        weights=[45, 30, 15, 10]
    )[0]

    parcelas = (
        random.randint(1, 12)
        if forma_pagamento == 'Cartao Credito'
        else 1
    )

    cursor.execute(
        """
        INSERT INTO pagamentos (
            id_pedido,
            tipo_pagamento,
            valor_pagamento,
            parcelas,
            data_pagamento
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        id_pedido,
        forma_pagamento,
        total_pedido,
        parcelas,
        data_pedido
    )

    # =====================================================
    # ENTREGA
    # =====================================================

    prazo = random.randint(2, 15)

    data_prevista = (
        data_pedido + timedelta(days=prazo)
    )

    atraso = random.choices(
        [0, 1],
        weights=[85, 15]
    )[0]

    dias_atraso = (
        random.randint(1, 10)
        if atraso
        else 0
    )

    data_real = (
        data_prevista +
        timedelta(days=dias_atraso)
    )

    cursor.execute(
        """
        INSERT INTO entregas (
            id_pedido,
            tipo_entrega,
            data_envio,
            data_entrega_prevista,
            data_entrega_real,
            valor_frete
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        id_pedido,
        random.choice([
            'Normal',
            'Expressa'
        ]),
        data_pedido + timedelta(days=1),
        data_prevista,
        data_real,
        round(random.uniform(10, 80), 2)
    )

    # =====================================================
    # AVALIACAO
    # =====================================================

    if status == 'Entregue':

        nota = random.choices(
            [1,2,3,4,5],
            weights=[5,5,10,30,50]
        )[0]

        cursor.execute(
            """
            INSERT INTO avaliacoes (
                id_pedido,
                nota,
                comentario,
                data_avaliacao
            )
            VALUES (?, ?, ?, ?)
            """,
            id_pedido,
            nota,
            fake.sentence(),
            data_real + timedelta(days=3)
        )

    # =====================================================
    # COMMIT
    # =====================================================

    if i % 1000 == 0:

        conn.commit()

        print(f'Pedidos inseridos: {i}')

conn.commit()

print('Carga finalizada!')