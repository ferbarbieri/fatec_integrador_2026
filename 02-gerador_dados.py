#pip install faker pandas pyodbc

import random
from datetime import datetime, timedelta

import pandas as pd
import pyodbc
from faker import Faker

fake = Faker('pt_BR')

# =========================================================
# CONEXAO SQL SERVER
# =========================================================

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\MSSQLLocalDB;'
    'DATABASE=FatecShop;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# =========================================================
# CONFIGURACOES
# =========================================================

QTD_CLIENTES = 5000
QTD_VENDEDORES = 200
QTD_PRODUTOS = 1000
QTD_PEDIDOS = 100000

# =========================================================
# DOMINIOS
# =========================================================

categorias = {
    'Eletronicos': ['Smartphones', 'Notebooks', 'TVs'],
    'Casa': ['Moveis', 'Decoracao', 'Cozinha'],
    'Moda': ['Masculino', 'Feminino', 'Calcados'],
    'Esportes': ['Academia', 'Ciclismo', 'Corrida'],
    'Games': ['Consoles', 'Jogos', 'Acessorios'],
    'Beleza': ['Perfumaria', 'Skincare', 'Maquiagem'],
    'Livros': ['Tecnologia', 'Ficcao', 'Negocios'],
    'Pet': ['Racoes', 'Brinquedos', 'Higiene'],
    'Automotivo': ['Pecas', 'Som', 'Acessorios'],
    'Bebidas': ['Vinhos', 'Cervejas', 'Destilados']
}

marcas = [
    'TechPro', 'UltraMax', 'PrimeTech', 'HomePlus',
    'FastWare', 'PowerFit', 'VisionX', 'NovaEra',
    'EliteStore', 'MegaLine'
]

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

estados = [
    'SP', 'RJ', 'MG', 'RS', 'SC',
    'PR', 'BA', 'GO', 'PE', 'CE'
]

# =========================================================
# CATEGORIAS E SUBCATEGORIAS
# =========================================================

print('Inserindo categorias...')

subcategoria_ids = []

for categoria, subs in categorias.items():

    cursor.execute(
        """
        INSERT INTO categorias (nome_categoria)
        OUTPUT INSERTED.id_categoria
        VALUES (?)
        """,
        categoria
    )

    id_categoria = cursor.fetchone()[0]

    for sub in subs:

        cursor.execute(
            """
            INSERT INTO subcategorias (
                id_categoria,
                nome_subcategoria
            )
            OUTPUT INSERTED.id_subcategoria
            VALUES (?, ?)
            """,
            id_categoria,
            sub
        )

        subcategoria_ids.append(cursor.fetchone()[0])

conn.commit()

# =========================================================
# CLIENTES
# =========================================================

print('Inserindo clientes...')

for i in range(QTD_CLIENTES):

    sexo = random.choice(['M', 'F'])

    nascimento = fake.date_between(
        start_date='-70y',
        end_date='-18y'
    )

    renda = round(random.uniform(1500, 25000), 2)

    cursor.execute(
        """
        INSERT INTO clientes (
            nome_cliente,
            email,
            telefone,
            sexo,
            data_nascimento,
            renda_mensal,
            data_cadastro
        )
        OUTPUT INSERTED.id_cliente
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        fake.name(),
        fake.unique.email(),
        fake.phone_number(),
        sexo,
        nascimento,
        renda,
        fake.date_time_between(
            start_date='-3y',
            end_date='now'
        )
    )

    id_cliente = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO enderecos_clientes (
            id_cliente,
            tipo_endereco,
            endereco,
            numero,
            complemento,
            bairro,
            cidade,
            estado,
            cep,
            principal_entrega
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        id_cliente,
        'Entrega',
        fake.street_name(),
        str(random.randint(1, 9999)),
        '',
        fake.bairro(),
        fake.city(),
        random.choice(estados),
        fake.postcode(),
        1
    )

    if i % 500 == 0:
        conn.commit()
        print(f'Clientes inseridos: {i}')

conn.commit()

# =========================================================
# VENDEDORES
# =========================================================

print('Inserindo vendedores...')

for _ in range(QTD_VENDEDORES):

    cursor.execute(
        """
        INSERT INTO vendedores (
            nome_vendedor,
            email,
            telefone,
            cidade,
            estado,
            data_entrada
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        fake.company(),
        fake.company_email(),
        fake.phone_number(),
        fake.city(),
        random.choice(estados),
        fake.date_between(start_date='-5y', end_date='today')
    )

conn.commit()

# =========================================================
# PRODUTOS
# =========================================================

print('Inserindo produtos...')

produtos_por_categoria = {
    'Smartphones': [
        'iPhone 15', 'Galaxy S24', 'Moto Edge 50',
        'Xiaomi Redmi Note 13', 'Galaxy A55'
    ],
    'Notebooks': [
        'Notebook Dell Inspiron', 'MacBook Air M3',
        'Lenovo IdeaPad', 'Acer Nitro 5', 'ASUS Vivobook'
    ],
    'TVs': [
        'Smart TV Samsung 55', 'LG OLED 65',
        'TCL 50 Polegadas', 'Philips Ambilight', 'Smart TV 4K Sony'
    ],
    'Moveis': [
        'Sofa Retratil', 'Mesa de Jantar',
        'Guarda Roupa Casal', 'Cadeira Gamer', 'Escrivaninha Office'
    ],
    'Decoracao': [
        'Luminaria LED', 'Quadro Decorativo',
        'Tapete Sala', 'Espelho Redondo', 'Cortina Blackout'
    ],
    'Cozinha': [
        'Air Fryer', 'Liquidificador Turbo',
        'Jogo de Panelas', 'Cafeteira Expresso', 'Microondas 30L'
    ],
    'Masculino': [
        'Camiseta Basica', 'Jaqueta Jeans',
        'Calca Slim', 'Camisa Social', 'Bermuda Moletom'
    ],
    'Feminino': [
        'Vestido Floral', 'Blusa Feminina',
        'Calca Wide Leg', 'Jaqueta Feminina', 'Saia Midi'
    ],
    'Calcados': [
        'Tenis Casual', 'Tenis Running',
        'Bota Couro', 'Sandalia Feminina', 'Sapato Social'
    ],
    'Academia': [
        'Kit Halteres', 'Esteira Eletrica',
        'Bicicleta Ergometrica', 'Corda Crossfit', 'Banco Supino'
    ],
    'Ciclismo': [
        'Bike MTB Aro 29', 'Capacete Bike',
        'Luva Ciclismo', 'Sinalizador LED Bike', 'Bomba de Ar Bike'
    ],
    'Corrida': [
        'Tenis Performance', 'Relogio Esportivo',
        'Camiseta Dry Fit', 'Mochila Hidratacao', 'Fone Bluetooth Sport'
    ],
    'Consoles': [
        'PlayStation 5', 'Xbox Series X',
        'Nintendo Switch', 'Controle DualSense', 'Headset Gamer'
    ],
    'Jogos': [
        'EA FC 26', 'Call of Duty',
        'Minecraft', 'GTA V', 'Forza Horizon'
    ],
    'Acessorios': [
        'Mouse Gamer', 'Teclado Mecanico',
        'Monitor Gamer', 'Webcam Full HD', 'SSD NVMe 1TB'
    ],
    'Perfumaria': [
        'Perfume Importado', 'Body Splash',
        'Kit Masculino', 'Kit Feminino', 'Perfume Amadeirado'
    ],
    'Skincare': [
        'Serum Facial', 'Hidratante Facial',
        'Protetor Solar', 'Sabonete Facial', 'Creme Antiidade'
    ],
    'Maquiagem': [
        'Base Liquida', 'Paleta Sombras',
        'Mascara Cilios', 'Batom Matte', 'Pincel Maquiagem'
    ],
    'Tecnologia': [
        'Livro Python', 'Livro SQL',
        'Livro Data Science', 'Livro Power BI', 'Livro Machine Learning'
    ],
    'Ficcao': [
        'Romance Bestseller', 'Livro Fantasia',
        'Livro Suspense', 'Livro Distopia', 'Livro Sci-Fi'
    ],
    'Negocios': [
        'Livro Lideranca', 'Livro Marketing',
        'Livro Financas', 'Livro Startups', 'Livro Produtividade'
    ]
}

subcategorias_df = pd.read_sql(
    """
    SELECT id_subcategoria, nome_subcategoria
    FROM subcategorias
    """,
    conn
)

for _, row in subcategorias_df.iterrows():

    id_subcategoria = row['id_subcategoria']
    nome_subcategoria = row['nome_subcategoria']

    produtos_lista = produtos_por_categoria.get(
        nome_subcategoria,
        ['Produto Generico']
    )

    qtd_produtos_categoria = random.randint(20, 60)

    for _ in range(qtd_produtos_categoria):

        produto_base = random.choice(produtos_lista)

        preco = round(random.uniform(20, 15000), 2)
        custo = round(preco * random.uniform(0.4, 0.8), 2)

        nome_produto = f'{produto_base} {random.randint(100,999)}'

        cursor.execute(
            """
            INSERT INTO produtos (
                id_subcategoria,
                nome_produto,
                marca,
                preco,
                custo,
                ativo
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            int(id_subcategoria),
            nome_produto,
            random.choice(marcas),
            preco,
            custo,
            1
        )

conn.commit()

print('Carga parcial concluida com sucesso!')
