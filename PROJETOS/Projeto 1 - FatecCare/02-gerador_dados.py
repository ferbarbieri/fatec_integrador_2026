from faker import Faker
import random
from datetime import datetime, timedelta
import pyodbc

fake = Faker("pt_BR")

# =========================================
# CONFIGURAÇÃO SQL SERVER
# =========================================

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\MSSQLLocalDB;'
    'DATABASE=FatecCare;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# =========================================
# DADOS FIXOS
# =========================================

convenios = [
    ("Unimed", "Premium"),
    ("Amil", "Intermediário"),
    ("Bradesco Saúde", "Premium"),
    ("SulAmérica", "Premium"),
    ("NotreDame Intermédica", "Básico"),
    ("Hapvida", "Básico"),
    ("Porto Seguro Saúde", "Intermediário"),
    ("Particular", "Particular")
]

especialidades = [
    "Clínico Geral",
    "Cardiologia",
    "Dermatologia",
    "Ortopedia",
    "Pediatria",
    "Neurologia",
    "Ginecologia",
    "Psiquiatria",
    "Oftalmologia",
    "Endocrinologia"
]

unidades = [
    ("Hospital Central", "São Paulo", "SP", "Hospital"),
    ("Clínica Vida", "Campinas", "SP", "Clínica"),
    ("Hospital Santa Luzia", "Rio de Janeiro", "RJ", "Hospital"),
    ("Centro Médico Saúde+", "Belo Horizonte", "MG", "Clínica"),
    ("Hospital Esperança", "Curitiba", "PR", "Hospital")
]

procedimentos = [
    ("Consulta Clínica", "Consulta", 150),
    ("Eletrocardiograma", "Exame", 220),
    ("Raio-X", "Exame", 180),
    ("Ultrassonografia", "Exame", 300),
    ("Consulta Cardiológica", "Consulta", 250),
    ("Exame de Sangue", "Laboratório", 90),
    ("Ressonância Magnética", "Imagem", 1200),
    ("Tomografia", "Imagem", 950),
    ("Consulta Pediátrica", "Consulta", 180),
    ("Consulta Dermatológica", "Consulta", 220)
]

tipos_atendimento = [
    "Consulta",
    "Retorno",
    "Emergência",
    "Check-up"
]

status_list = [
    "Finalizado",
    "Cancelado",
    "Em andamento"
]

urgencias = [
    "Baixa",
    "Média",
    "Alta"
]

# =========================================
# INSERT CONVENIO
# =========================================

print("Inserindo convênios...")

for convenio in convenios:
    cursor.execute("""
        INSERT INTO Convenio (nome_convenio, categoria)
        VALUES (?, ?)
    """, convenio)

conn.commit()

# =========================================
# INSERT ESPECIALIDADE
# =========================================

print("Inserindo especialidades...")

for esp in especialidades:
    cursor.execute("""
        INSERT INTO Especialidade (nome_especialidade)
        VALUES (?)
    """, esp)

conn.commit()

# =========================================
# INSERT UNIDADE
# =========================================

print("Inserindo unidades...")

for unidade in unidades:
    cursor.execute("""
        INSERT INTO Unidade (nome_unidade, cidade, estado, tipo_unidade)
        VALUES (?, ?, ?, ?)
    """, unidade)

conn.commit()

# =========================================
# INSERT PROCEDIMENTO
# =========================================

print("Inserindo procedimentos...")

for proc in procedimentos:
    cursor.execute("""
        INSERT INTO Procedimento (nome_procedimento, categoria, valor_padrao)
        VALUES (?, ?, ?)
    """, proc)

conn.commit()

# =========================================
# INSERT PACIENTES
# =========================================

print("Inserindo pacientes...")

NUM_PACIENTES = 200

for _ in range(NUM_PACIENTES):

    sexo = random.choice(["M", "F"])

    nascimento = fake.date_between(
        start_date="-90y",
        end_date="-1y"
    )

    cadastro = fake.date_between(
        start_date="-5y",
        end_date="today"
    )

    cursor.execute("""
        INSERT INTO Paciente (
            nome,
            sexo,
            data_nascimento,
            cidade,
            estado,
            convenio_id,
            data_cadastro
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        fake.name_male() if sexo == "M" else fake.name_female(),
        sexo,
        nascimento,
        fake.city(),
        fake.estado_sigla(),
        random.randint(1, len(convenios)),
        cadastro
    ))

conn.commit()

# =========================================
# INSERT MÉDICOS
# =========================================

print("Inserindo médicos...")

NUM_MEDICOS = 30

for _ in range(NUM_MEDICOS):

    cursor.execute("""
        INSERT INTO Medico (
            nome,
            especialidade_id,
            crm,
            unidade_id
        )
        VALUES (?, ?, ?, ?)
    """,
    (
        f"Dr(a). {fake.name()}",
        random.randint(1, len(especialidades)),
        f"CRM-{random.randint(10000,99999)}",
        random.randint(1, len(unidades))
    ))

conn.commit()

# =========================================
# INSERT ATENDIMENTOS
# =========================================

print("Inserindo atendimentos...")

NUM_ATENDIMENTOS = 2000

for i in range(NUM_ATENDIMENTOS):

    data_atendimento = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    hora = fake.time_object()

    procedimento_id = random.randint(1, len(procedimentos))

    valor_base = procedimentos[procedimento_id - 1][2]

    valor = round(
        valor_base * random.uniform(0.8, 1.3),
        2
    )

    cursor.execute("""
        INSERT INTO Atendimento (
            paciente_id,
            medico_id,
            unidade_id,
            procedimento_id,
            data_atendimento,
            hora_atendimento,
            tipo_atendimento,
            status,
            valor_consulta,
            tempo_espera_min,
            tempo_atendimento_min,
            satisfacao,
            retorno,
            urgencia
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        random.randint(1, NUM_PACIENTES),
        random.randint(1, NUM_MEDICOS),
        random.randint(1, len(unidades)),
        procedimento_id,
        data_atendimento,
        hora,
        random.choice(tipos_atendimento),
        random.choices(
            status_list,
            weights=[85, 10, 5]
        )[0],
        valor,
        random.randint(5, 180),
        random.randint(10, 120),
        random.randint(1, 5),
        random.choice([0, 1]),
        random.choice(urgencias)
    ))

    if i % 1000 == 0 and i > 0:
        print(f"{i} atendimentos inseridos...")
        conn.commit()

conn.commit()

# =========================================
# FINALIZAÇÃO
# =========================================

cursor.close()
conn.close()

print("\nBase populada com sucesso!")
print(f"Pacientes: {NUM_PACIENTES}")
print(f"Médicos: {NUM_MEDICOS}")
print(f"Atendimentos: {NUM_ATENDIMENTOS}")