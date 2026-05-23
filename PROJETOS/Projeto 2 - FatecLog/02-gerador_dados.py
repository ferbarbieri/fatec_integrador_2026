from faker import Faker
import random
from datetime import timedelta
import pyodbc

fake = Faker("pt_BR")

# =========================================
# CONFIG SQL SERVER
# =========================================

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\MSSQLLocalDB;'
    'DATABASE=FatecLog;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# =========================================
# DADOS FIXOS
# =========================================

segmentos = [
    "Varejo",
    "Farmacêutico",
    "Alimentício",
    "Automotivo",
    "Tecnologia"
]

centros = [
    ("CD São Paulo", "São Paulo", "SP", 10000),
    ("CD Campinas", "Campinas", "SP", 7000),
    ("CD Curitiba", "Curitiba", "PR", 5000),
    ("CD Belo Horizonte", "Belo Horizonte", "MG", 6000),
    ("CD Rio de Janeiro", "Rio de Janeiro", "RJ", 8000)
]

veiculos = [
    ("ABC1A11", "Volkswagen Delivery", "Caminhão", 8000, 2020, "Ativo"),
    ("DEF2B22", "Mercedes Atego", "Caminhão", 12000, 2021, "Ativo"),
    ("GHI3C33", "Fiat Fiorino", "Van", 1000, 2022, "Ativo"),
    ("JKL4D44", "Volvo FH", "Carreta", 30000, 2019, "Ativo"),
    ("MNO5E55", "Hyundai HR", "Utilitário", 1800, 2023, "Manutenção")
]

rotas = [
    ("São Paulo", "SP", "Campinas", "SP", 100),
    ("São Paulo", "SP", "Rio de Janeiro", "RJ", 430),
    ("Curitiba", "PR", "Florianópolis", "SC", 300),
    ("Belo Horizonte", "MG", "Vitória", "ES", 520),
    ("Campinas", "SP", "Ribeirão Preto", "SP", 220),
    ("Rio de Janeiro", "RJ", "Belo Horizonte", "MG", 440)
]

tipos_carga = [
    ("Medicamentos", "Farmacêutico"),
    ("Alimentos Refrigerados", "Perecível"),
    ("Eletrônicos", "Tecnologia"),
    ("Autopeças", "Automotivo"),
    ("Produtos de Limpeza", "Químico")
]

status_entrega = [
    "Entregue",
    "Atrasada",
    "Em trânsito",
    "Cancelada"
]

# =========================================
# INSERT CLIENTES
# =========================================

print("Inserindo clientes...")

NUM_CLIENTES = 200

for _ in range(NUM_CLIENTES):

    cursor.execute("""
        INSERT INTO Cliente (
            nome_cliente,
            segmento,
            cidade,
            estado,
            data_cadastro
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        fake.company(),
        random.choice(segmentos),
        fake.city(),
        fake.estado_sigla(),
        fake.date_between(start_date="-5y", end_date="today")
    ))

conn.commit()

# =========================================
# INSERT CENTROS
# =========================================

print("Inserindo centros...")

for centro in centros:

    cursor.execute("""
        INSERT INTO CentroDistribuicao (
            nome_centro,
            cidade,
            estado,
            capacidade_operacional
        )
        VALUES (?, ?, ?, ?)
    """, centro)

conn.commit()

# =========================================
# INSERT VEICULOS
# =========================================

print("Inserindo veículos...")

for veiculo in veiculos:

    cursor.execute("""
        INSERT INTO Veiculo (
            placa,
            modelo,
            tipo_veiculo,
            capacidade_kg,
            ano_fabricacao,
            status_veiculo
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, veiculo)

conn.commit()

# =========================================
# INSERT MOTORISTAS
# =========================================

print("Inserindo motoristas...")

NUM_MOTORISTAS = 60

for _ in range(NUM_MOTORISTAS):

    cursor.execute("""
        INSERT INTO Motorista (
            nome_motorista,
            cidade,
            estado,
            data_admissao,
            categoria_cnh
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        fake.name(),
        fake.city(),
        fake.estado_sigla(),
        fake.date_between(start_date="-10y", end_date="today"),
        random.choice(["B", "C", "D", "E"])
    ))

conn.commit()

# =========================================
# INSERT ROTAS
# =========================================

print("Inserindo rotas...")

for rota in rotas:

    cursor.execute("""
        INSERT INTO Rota (
            cidade_origem,
            estado_origem,
            cidade_destino,
            estado_destino,
            distancia_km
        )
        VALUES (?, ?, ?, ?, ?)
    """, rota)

conn.commit()

# =========================================
# INSERT TIPO CARGA
# =========================================

print("Inserindo tipos de carga...")

for carga in tipos_carga:

    cursor.execute("""
        INSERT INTO TipoCarga (
            descricao_tipo_carga,
            categoria
        )
        VALUES (?, ?)
    """, carga)

conn.commit()

# =========================================
# INSERT ENTREGAS
# =========================================

print("Inserindo entregas...")

NUM_ENTREGAS = 15000

for i in range(NUM_ENTREGAS):

    data_saida = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    tempo_estimado = random.randint(4, 72)

    atraso = random.choice([
        random.randint(0, 12),
        0,
        0,
        0
    ])

    tempo_real = tempo_estimado + atraso

    data_entrega = data_saida + timedelta(
        hours=tempo_real
    )

    entregue_prazo = 1 if tempo_real <= tempo_estimado else 0

    status = random.choices(
        status_entrega,
        weights=[75, 10, 10, 5]
    )[0]

    valor_frete = round(
        random.uniform(200, 5000),
        2
    )

    custo_combustivel = round(
        valor_frete * random.uniform(0.15, 0.35),
        2
    )

    cursor.execute("""
        INSERT INTO Entrega (
            cliente_id,
            centro_id,
            veiculo_id,
            motorista_id,
            rota_id,
            tipo_carga_id,
            data_saida,
            data_entrega,
            status_entrega,
            peso_carga_kg,
            valor_frete,
            custo_combustivel,
            tempo_estimado_horas,
            tempo_real_horas,
            quantidade_volumes,
            avaria,
            entrega_no_prazo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        random.randint(1, NUM_CLIENTES),
        random.randint(1, len(centros)),
        random.randint(1, len(veiculos)),
        random.randint(1, NUM_MOTORISTAS),
        random.randint(1, len(rotas)),
        random.randint(1, len(tipos_carga)),
        data_saida,
        data_entrega,
        status,
        round(random.uniform(50, 25000), 2),
        valor_frete,
        custo_combustivel,
        tempo_estimado,
        tempo_real,
        random.randint(1, 150),
        random.choice([0, 0, 0, 1]),
        entregue_prazo
    ))

    if i % 1000 == 0 and i > 0:
        print(f"{i} entregas inseridas...")
        conn.commit()

conn.commit()

cursor.close()
conn.close()

print("\nBase FatecLog populada com sucesso!")