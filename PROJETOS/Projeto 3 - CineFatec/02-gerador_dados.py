from faker import Faker
import random
import pyodbc
from datetime import timedelta

fake = Faker("pt_BR")

# =========================================
# CONEXÃO
# =========================================
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\MSSQLLocalDB;'
    'DATABASE=CineFatec;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# =========================================
# LIMPEZA
# =========================================
print("Limpando dados...")

cursor.execute("DELETE FROM Ingresso")
cursor.execute("DELETE FROM Sessao")
cursor.execute("DELETE FROM Sala")
cursor.execute("DELETE FROM Filme")
cursor.execute("DELETE FROM GeneroFilme")
cursor.execute("DELETE FROM Cinema")
cursor.execute("DELETE FROM Cliente")

conn.commit()

# =========================================
# DADOS FIXOS
# =========================================

generos = [
    "Ação", "Comédia", "Drama", "Terror",
    "Ficção Científica", "Romance", "Animação", "Suspense"
]

filmes = [
    "Operação Final", "Risos do Amanhã", "Além da Escuridão",
    "Galáxia Perdida", "Amor em Paris", "Detetive Sombrio",
    "Mundo Animado", "Código Mortal", "Última Chance", "Planeta Vermelho"
]

cinemas = [
    ("CineFatec Paulista", "São Paulo", "SP", "Shopping"),
    ("CineFatec Campinas", "Campinas", "SP", "Shopping"),
    ("CineFatec Curitiba", "Curitiba", "PR", "Rua"),
    ("CineFatec Rio", "Rio de Janeiro", "RJ", "Shopping"),
    ("CineFatec BH", "Belo Horizonte", "MG", "Shopping")
]

tipos_sala = ["Convencional", "3D", "IMAX", "VIP"]

formatos = ["2D", "3D", "IMAX"]

canais_venda = ["Bilheteria", "Aplicativo", "Website", "Totem"]

# =========================================
# GENERO
# =========================================
print("Inserindo gêneros...")

for g in generos:
    cursor.execute("INSERT INTO GeneroFilme (nome_genero) VALUES (?)", g)

conn.commit()

genero_ids = [r[0] for r in cursor.execute("SELECT id_genero FROM GeneroFilme").fetchall()]

# =========================================
# FILMES
# =========================================
print("Inserindo filmes...")

for f in filmes:
    cursor.execute("""
        INSERT INTO Filme (
            titulo, genero_id, classificacao_indicativa,
            duracao_min, idioma_original, distribuidora
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        f,
        random.choice(genero_ids),
        random.choice(["Livre", "10", "12", "14", "16", "18"]),
        random.randint(80, 180),
        random.choice(["Português", "Inglês"]),
        random.choice(["Warner", "Disney", "Universal", "Sony"])
    ))

conn.commit()

filme_ids = [r[0] for r in cursor.execute("SELECT id_filme FROM Filme").fetchall()]

# =========================================
# CINEMAS
# =========================================
print("Inserindo cinemas...")

for c in cinemas:
    cursor.execute("""
        INSERT INTO Cinema (nome_cinema, cidade, estado, tipo_unidade)
        VALUES (?, ?, ?, ?)
    """, c)

conn.commit()

cinema_ids = [r[0] for r in cursor.execute("SELECT id_cinema FROM Cinema").fetchall()]

# =========================================
# SALAS
# =========================================
print("Inserindo salas...")

for cinema_id in cinema_ids:
    qtd = random.randint(4, 8)

    for i in range(qtd):
        cursor.execute("""
            INSERT INTO Sala (cinema_id, nome_sala, capacidade, tipo_sala)
            VALUES (?, ?, ?, ?)
        """,
        (
            cinema_id,
            f"Sala {i+1}",
            random.randint(80, 300),
            random.choice(tipos_sala)
        ))

conn.commit()

sala_ids = [r[0] for r in cursor.execute("SELECT id_sala FROM Sala").fetchall()]

# =========================================
# CLIENTES
# =========================================
print("Inserindo clientes...")

NUM_CLIENTES = 5000

for _ in range(NUM_CLIENTES):
    sexo = random.choice(["M", "F"])

    cursor.execute("""
        INSERT INTO Cliente (
            nome, sexo, data_nascimento, cidade, estado, data_cadastro
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        fake.name_male() if sexo == "M" else fake.name_female(),
        sexo,
        fake.date_between("-70y", "-10y"),
        fake.city(),
        fake.estado_sigla(),
        fake.date_between("-5y", "today")
    ))

conn.commit()

cliente_ids = [r[0] for r in cursor.execute("SELECT id_cliente FROM Cliente").fetchall()]

# =========================================
# SESSOES
# =========================================
print("Inserindo sessões...")

NUM_SESSOES = 2000

for i in range(NUM_SESSOES):

    cursor.execute("""
        INSERT INTO Sessao (
            filme_id, sala_id, data_sessao, hora_sessao, idioma, formato
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        random.choice(filme_ids),
        random.choice(sala_ids),
        fake.date_between("-1y", "+30d"),
        random.choice(["13:00", "15:30", "18:00", "20:30", "23:00"]),
        random.choice(["Dublado", "Legendado"]),
        random.choice(formatos)
    ))

    if i % 500 == 0:
        conn.commit()

conn.commit()

sessao_ids = [r[0] for r in cursor.execute("SELECT id_sessao FROM Sessao").fetchall()]

# =========================================
# INGRESSOS (FATO FUTURO)
# =========================================
print("Inserindo ingressos...")

NUM_INGRESSOS = 20000

for i in range(NUM_INGRESSOS):

    meia = random.choice([0, 1])

    tipo = "Meia" if meia else random.choice(["Inteira", "VIP"])

    valor = random.uniform(20, 80)

    if tipo == "VIP":
        valor *= 1.8
    if meia:
        valor *= 0.5

    cursor.execute("""
        INSERT INTO Ingresso (
            sessao_id, cliente_id, data_compra,
            canal_venda, tipo_ingresso, valor_ingresso,
            assento, meia_entrada, snack_combo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        random.choice(sessao_ids),
        random.choice(cliente_ids),
        fake.date_time_between("-1y", "now"),
        random.choice(canais_venda),
        tipo,
        round(valor, 2),
        f"{random.choice('ABCDEFGH')}{random.randint(1,20)}",
        meia,
        random.choice([0, 1])
    ))

    if i % 5000 == 0:
        conn.commit()

conn.commit()

cursor.close()
conn.close()

print("\nCineFatec carregado com sucesso (versão corrigida)! 🚀")