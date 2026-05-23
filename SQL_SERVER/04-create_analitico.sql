USE FatecShop2;
GO

/* =========================================================
   SCHEMA ANALITICO
========================================================= */

CREATE SCHEMA dw;
GO

/* =========================================================
   DIM_CLIENTE
========================================================= */

CREATE TABLE dw.dim_cliente (

    sk_cliente                INT IDENTITY(1,1) PRIMARY KEY,

    id_cliente_origem         INT NOT NULL,

    nome_cliente              VARCHAR(150),
    sexo                      CHAR(1),
    data_nascimento           DATE,

    idade                     INT,
    faixa_etaria              VARCHAR(50),

    renda_mensal              DECIMAL(10,2),
    faixa_renda               VARCHAR(50),

    cidade                    VARCHAR(100),
    estado                    VARCHAR(2),
    regiao                    VARCHAR(50),

    data_cadastro             DATETIME
);
GO

/* =========================================================
   DIM_PRODUTO
========================================================= */

CREATE TABLE dw.dim_produto (

    sk_produto                INT IDENTITY(1,1) PRIMARY KEY,

    id_produto_origem         INT NOT NULL,

    nome_produto              VARCHAR(200),
    marca                     VARCHAR(100),

    categoria                 VARCHAR(100),
    subcategoria              VARCHAR(100),

    preco_base                DECIMAL(10,2),

    faixa_preco               VARCHAR(50),

    ativo                     BIT
);
GO

/* =========================================================
   DIM_VENDEDOR
========================================================= */

CREATE TABLE dw.dim_vendedor (

    sk_vendedor               INT IDENTITY(1,1) PRIMARY KEY,

    id_vendedor_origem        INT NOT NULL,

    nome_vendedor             VARCHAR(150),

    cidade                    VARCHAR(100),
    estado                    VARCHAR(2),
    regiao                    VARCHAR(50),

    data_entrada              DATE
);
GO

/* =========================================================
   DIM_PAGAMENTO
========================================================= */

CREATE TABLE dw.dim_pagamento (

    sk_pagamento              INT IDENTITY(1,1) PRIMARY KEY,

    tipo_pagamento            VARCHAR(50),

    faixa_parcelas            VARCHAR(50)
);
GO

/* =========================================================
   DIM_ENTREGA
========================================================= */

CREATE TABLE dw.dim_entrega (

    sk_entrega                INT IDENTITY(1,1) PRIMARY KEY,

    tipo_entrega              VARCHAR(50),

    faixa_prazo               VARCHAR(50),

    entrega_atrasada          VARCHAR(10)
);
GO

/* =========================================================
   DIM_DATA
========================================================= */

CREATE TABLE dw.dim_data (

    sk_data                   INT PRIMARY KEY,

    data_completa             DATE,

    dia                       INT,
    nome_dia_semana           VARCHAR(30),

    semana_ano                INT,

    mes                       INT,
    nome_mes                  VARCHAR(30),

    trimestre                 INT,
    semestre                  INT,
    ano                       INT,

    fim_semana                BIT
);
GO

/* =========================================================
   FATO_VENDAS
========================================================= */

CREATE TABLE dw.fato_vendas (

    sk_venda                  BIGINT IDENTITY(1,1) PRIMARY KEY,

    sk_cliente                INT NOT NULL,
    sk_produto                INT NOT NULL,
    sk_vendedor               INT NOT NULL,
    sk_pagamento              INT NOT NULL,
    sk_entrega                INT NOT NULL,
    sk_data                   INT NOT NULL,

    id_pedido_origem          INT NOT NULL,

    quantidade_itens          INT,

    preco_unitario            DECIMAL(10,2),
    valor_bruto               DECIMAL(10,2),
    desconto                  DECIMAL(10,2),
    valor_frete               DECIMAL(10,2),
    valor_liquido             DECIMAL(10,2),

    custo_produto             DECIMAL(10,2),
    lucro                     DECIMAL(10,2),

    prazo_entrega_dias        INT,

    avaliacao                 INT,

    CONSTRAINT fk_fato_cliente
        FOREIGN KEY (sk_cliente)
        REFERENCES dw.dim_cliente(sk_cliente),

    CONSTRAINT fk_fato_produto
        FOREIGN KEY (sk_produto)
        REFERENCES dw.dim_produto(sk_produto),

    CONSTRAINT fk_fato_vendedor
        FOREIGN KEY (sk_vendedor)
        REFERENCES dw.dim_vendedor(sk_vendedor),

    CONSTRAINT fk_fato_pagamento
        FOREIGN KEY (sk_pagamento)
        REFERENCES dw.dim_pagamento(sk_pagamento),

    CONSTRAINT fk_fato_entrega
        FOREIGN KEY (sk_entrega)
        REFERENCES dw.dim_entrega(sk_entrega),

    CONSTRAINT fk_fato_data
        FOREIGN KEY (sk_data)
        REFERENCES dw.dim_data(sk_data)
);
GO