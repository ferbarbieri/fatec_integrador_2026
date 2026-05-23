CREATE DATABASE FatecCare;
GO

USE FatecCare;
GO

-- =========================================
-- TABELA: CONVENIO
-- =========================================
CREATE TABLE Convenio (
    id_convenio INT IDENTITY(1,1) PRIMARY KEY,
    nome_convenio VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL
);
GO

-- =========================================
-- TABELA: ESPECIALIDADE
-- =========================================
CREATE TABLE Especialidade (
    id_especialidade INT IDENTITY(1,1) PRIMARY KEY,
    nome_especialidade VARCHAR(100) NOT NULL
);
GO

-- =========================================
-- TABELA: UNIDADE
-- =========================================
CREATE TABLE Unidade (
    id_unidade INT IDENTITY(1,1) PRIMARY KEY,
    nome_unidade VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    tipo_unidade VARCHAR(50) NOT NULL
);
GO

-- =========================================
-- TABELA: PROCEDIMENTO
-- =========================================
CREATE TABLE Procedimento (
    id_procedimento INT IDENTITY(1,1) PRIMARY KEY,
    nome_procedimento VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    valor_padrao DECIMAL(10,2) NOT NULL
);
GO

-- =========================================
-- TABELA: PACIENTE
-- =========================================
CREATE TABLE Paciente (
    id_paciente INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    sexo CHAR(1) NOT NULL,
    data_nascimento DATE NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    convenio_id INT NOT NULL,
    data_cadastro DATE NOT NULL,

    CONSTRAINT FK_Paciente_Convenio
        FOREIGN KEY (convenio_id)
        REFERENCES Convenio(id_convenio)
);
GO

-- =========================================
-- TABELA: MEDICO
-- =========================================
CREATE TABLE Medico (
    id_medico INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    especialidade_id INT NOT NULL,
    crm VARCHAR(20) NOT NULL,
    unidade_id INT NOT NULL,

    CONSTRAINT FK_Medico_Especialidade
        FOREIGN KEY (especialidade_id)
        REFERENCES Especialidade(id_especialidade),

    CONSTRAINT FK_Medico_Unidade
        FOREIGN KEY (unidade_id)
        REFERENCES Unidade(id_unidade)
);
GO

-- =========================================
-- TABELA: ATENDIMENTO
-- =========================================
CREATE TABLE Atendimento (
    id_atendimento INT IDENTITY(1,1) PRIMARY KEY,

    paciente_id INT NOT NULL,
    medico_id INT NOT NULL,
    unidade_id INT NOT NULL,
    procedimento_id INT NOT NULL,

    data_atendimento DATE NOT NULL,
    hora_atendimento TIME NOT NULL,

    tipo_atendimento VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL,

    valor_consulta DECIMAL(10,2) NOT NULL,

    tempo_espera_min INT,
    tempo_atendimento_min INT,

    satisfacao TINYINT,
    retorno BIT NOT NULL,
    urgencia VARCHAR(20) NOT NULL,

    CONSTRAINT FK_Atendimento_Paciente
        FOREIGN KEY (paciente_id)
        REFERENCES Paciente(id_paciente),

    CONSTRAINT FK_Atendimento_Medico
        FOREIGN KEY (medico_id)
        REFERENCES Medico(id_medico),

    CONSTRAINT FK_Atendimento_Unidade
        FOREIGN KEY (unidade_id)
        REFERENCES Unidade(id_unidade),

    CONSTRAINT FK_Atendimento_Procedimento
        FOREIGN KEY (procedimento_id)
        REFERENCES Procedimento(id_procedimento)
);
GO