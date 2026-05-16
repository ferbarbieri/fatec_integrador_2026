CREATE DATABASE FatecShop;
GO

USE FatecShop;
GO

/* =========================================================
   CLIENTES
========================================================= */

CREATE TABLE clientes (
    id_cliente            INT IDENTITY(1,1) PRIMARY KEY,
    nome_cliente          VARCHAR(150) NOT NULL,
    email                 VARCHAR(150) NOT NULL,
    telefone              VARCHAR(20),
    sexo                  CHAR(1),
    data_nascimento       DATE,
    renda_mensal          DECIMAL(10,2),
    data_cadastro         DATETIME DEFAULT GETDATE()
);
GO

/* =========================================================
   ENDERECOS CLIENTES
========================================================= */

CREATE TABLE enderecos_clientes (
    id_endereco           INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente            INT NOT NULL,
    tipo_endereco         VARCHAR(30), -- Residencial, Entrega etc
    endereco              VARCHAR(200),
    numero                VARCHAR(20),
    complemento           VARCHAR(100),
    bairro                VARCHAR(100),
    cidade                VARCHAR(100),
    estado                VARCHAR(2),
    cep                   VARCHAR(10),
    principal_entrega     BIT DEFAULT 0,

    CONSTRAINT fk_endereco_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
);
GO

/* =========================================================
   VENDEDORES
========================================================= */

CREATE TABLE vendedores (
    id_vendedor           INT IDENTITY(1,1) PRIMARY KEY,
    nome_vendedor         VARCHAR(150) NOT NULL,
    email                 VARCHAR(150),
    telefone              VARCHAR(20),
    cidade                VARCHAR(100),
    estado                VARCHAR(2),
    data_entrada          DATE
);
GO

/* =========================================================
   CATEGORIAS
========================================================= */

CREATE TABLE categorias (
    id_categoria          INT IDENTITY(1,1) PRIMARY KEY,
    nome_categoria        VARCHAR(100) NOT NULL
);
GO

/* =========================================================
   SUBCATEGORIAS
========================================================= */

CREATE TABLE subcategorias (
    id_subcategoria       INT IDENTITY(1,1) PRIMARY KEY,
    id_categoria          INT NOT NULL,
    nome_subcategoria     VARCHAR(100) NOT NULL,

    CONSTRAINT fk_subcategoria_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
);
GO

/* =========================================================
   PRODUTOS
========================================================= */

CREATE TABLE produtos (
    id_produto            INT IDENTITY(1,1) PRIMARY KEY,
    id_subcategoria       INT NOT NULL,
    nome_produto          VARCHAR(200) NOT NULL,
    marca                 VARCHAR(100),
    preco                 DECIMAL(10,2) NOT NULL,
    custo                 DECIMAL(10,2) NOT NULL,
    ativo                 BIT DEFAULT 1,
    data_cadastro         DATETIME DEFAULT GETDATE(),

    CONSTRAINT fk_produto_subcategoria
        FOREIGN KEY (id_subcategoria)
        REFERENCES subcategorias(id_subcategoria)
);
GO

/* =========================================================
   PROMOCOES
========================================================= */

CREATE TABLE promocoes (
    id_promocao           INT IDENTITY(1,1) PRIMARY KEY,
    nome_promocao         VARCHAR(150),
    percentual_desconto   DECIMAL(5,2),
    data_inicio           DATE,
    data_fim              DATE
);
GO

/* =========================================================
   PRODUTOS_PROMOCOES
========================================================= */

CREATE TABLE produtos_promocoes (
    id_produto_promocao   INT IDENTITY(1,1) PRIMARY KEY,
    id_produto            INT NOT NULL,
    id_promocao           INT NOT NULL,

    CONSTRAINT fk_produto_promocao_produto
        FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto),

    CONSTRAINT fk_produto_promocao_promocao
        FOREIGN KEY (id_promocao)
        REFERENCES promocoes(id_promocao)
);
GO

/* =========================================================
   PEDIDOS
========================================================= */

CREATE TABLE pedidos (
    id_pedido             INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente            INT NOT NULL,
    data_pedido           DATETIME DEFAULT GETDATE(),
    status_pedido         VARCHAR(50),

    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
);
GO

/* =========================================================
   ITENS PEDIDO
========================================================= */

CREATE TABLE itens_pedido (
    id_item_pedido        INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido             INT NOT NULL,
    id_produto            INT NOT NULL,
    id_vendedor           INT NOT NULL,
    quantidade            INT NOT NULL,
    preco_unitario        DECIMAL(10,2) NOT NULL,
    desconto              DECIMAL(10,2) DEFAULT 0,

    CONSTRAINT fk_item_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido),

    CONSTRAINT fk_item_produto
        FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto),

    CONSTRAINT fk_item_vendedor
        FOREIGN KEY (id_vendedor)
        REFERENCES vendedores(id_vendedor)
);
GO

/* =========================================================
   PAGAMENTOS
========================================================= */

CREATE TABLE pagamentos (
    id_pagamento          INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido             INT NOT NULL,
    tipo_pagamento        VARCHAR(50), -- Cartao, Pix, Boleto
    valor_pagamento       DECIMAL(10,2),
    parcelas              INT,
    data_pagamento        DATETIME,

    CONSTRAINT fk_pagamento_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido)
);
GO

/* =========================================================
   ENTREGAS
========================================================= */

CREATE TABLE entregas (
    id_entrega            INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido             INT NOT NULL,
    tipo_entrega          VARCHAR(50), -- Normal, Expressa
    data_envio            DATETIME,
    data_entrega_prevista DATETIME,
    data_entrega_real     DATETIME,
    valor_frete           DECIMAL(10,2),

    CONSTRAINT fk_entrega_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido)
);
GO

/* =========================================================
   AVALIACOES
========================================================= */

CREATE TABLE avaliacoes (
    id_avaliacao          INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido             INT NOT NULL,
    nota                  INT,
    comentario            VARCHAR(500),
    data_avaliacao        DATETIME DEFAULT GETDATE(),

    CONSTRAINT fk_avaliacao_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido)
);
GO