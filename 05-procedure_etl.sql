USE FatecShop;
GO

/* =========================================================
   STORED PROCEDURE CARGA DIMENSIONAL
========================================================= */

CREATE OR ALTER PROCEDURE dw.sp_carga_full_dw
AS
BEGIN

    SET NOCOUNT ON;

    PRINT '=========================================';
    PRINT 'INICIANDO CARGA FULL DW';
    PRINT '=========================================';

    /* =====================================================
       LIMPEZA FATO
    ===================================================== */

    TRUNCATE TABLE dw.fato_vendas;

    /* =====================================================
       LIMPEZA DIMENSOES
    ===================================================== */

    DELETE FROM dw.dim_cliente;
    DELETE FROM dw.dim_produto;
    DELETE FROM dw.dim_vendedor;
    DELETE FROM dw.dim_pagamento;
    DELETE FROM dw.dim_entrega;
    DELETE FROM dw.dim_data;

    /* =====================================================
       RESET IDENTITY
    ===================================================== */

    DBCC CHECKIDENT ('dw.dim_cliente', RESEED, 0);
    DBCC CHECKIDENT ('dw.dim_produto', RESEED, 0);
    DBCC CHECKIDENT ('dw.dim_vendedor', RESEED, 0);
    DBCC CHECKIDENT ('dw.dim_pagamento', RESEED, 0);
    DBCC CHECKIDENT ('dw.dim_entrega', RESEED, 0);

    /* =====================================================
       DIM_CLIENTE
    ===================================================== */

    PRINT 'Carregando dim_cliente...';

    INSERT INTO dw.dim_cliente (
        id_cliente_origem,
        nome_cliente,
        sexo,
        data_nascimento,
        idade,
        faixa_etaria,
        renda_mensal,
        faixa_renda,
        cidade,
        estado,
        regiao,
        data_cadastro
    )

    SELECT
        c.id_cliente,
        c.nome_cliente,
        c.sexo,
        c.data_nascimento,

        DATEDIFF(YEAR, c.data_nascimento, GETDATE()) AS idade,

        CASE
            WHEN DATEDIFF(YEAR, c.data_nascimento, GETDATE()) < 25 THEN '18-24'
            WHEN DATEDIFF(YEAR, c.data_nascimento, GETDATE()) < 35 THEN '25-34'
            WHEN DATEDIFF(YEAR, c.data_nascimento, GETDATE()) < 45 THEN '35-44'
            WHEN DATEDIFF(YEAR, c.data_nascimento, GETDATE()) < 60 THEN '45-59'
            ELSE '60+'
        END AS faixa_etaria,

        c.renda_mensal,

        CASE
            WHEN c.renda_mensal < 3000 THEN 'Baixa'
            WHEN c.renda_mensal < 8000 THEN 'Media'
            WHEN c.renda_mensal < 15000 THEN 'Alta'
            ELSE 'Premium'
        END AS faixa_renda,

        e.cidade,
        e.estado,

        CASE
            WHEN e.estado IN ('SP','RJ','MG','ES') THEN 'Sudeste'
            WHEN e.estado IN ('RS','SC','PR') THEN 'Sul'
            WHEN e.estado IN ('BA','PE','CE') THEN 'Nordeste'
            WHEN e.estado IN ('GO','MT','MS','DF') THEN 'Centro-Oeste'
            ELSE 'Outros'
        END AS regiao,

        c.data_cadastro

    FROM clientes c

    LEFT JOIN enderecos_clientes e
        ON c.id_cliente = e.id_cliente
       AND e.principal_entrega = 1;

    /* =====================================================
       DIM_PRODUTO
    ===================================================== */

    PRINT 'Carregando dim_produto...';

    INSERT INTO dw.dim_produto (
        id_produto_origem,
        nome_produto,
        marca,
        categoria,
        subcategoria,
        preco_base,
        faixa_preco,
        ativo
    )

    SELECT
        p.id_produto,
        p.nome_produto,
        p.marca,
        c.nome_categoria,
        s.nome_subcategoria,
        p.preco,

        CASE
            WHEN p.preco < 100 THEN 'Ate 100'
            WHEN p.preco < 500 THEN '100-499'
            WHEN p.preco < 2000 THEN '500-1999'
            WHEN p.preco < 5000 THEN '2000-4999'
            ELSE '5000+'
        END AS faixa_preco,

        p.ativo

    FROM produtos p

    INNER JOIN subcategorias s
        ON p.id_subcategoria = s.id_subcategoria

    INNER JOIN categorias c
        ON s.id_categoria = c.id_categoria;

    /* =====================================================
       DIM_VENDEDOR
    ===================================================== */

    PRINT 'Carregando dim_vendedor...';

    INSERT INTO dw.dim_vendedor (
        id_vendedor_origem,
        nome_vendedor,
        cidade,
        estado,
        regiao,
        data_entrada
    )

    SELECT
        v.id_vendedor,
        v.nome_vendedor,
        v.cidade,
        v.estado,

        CASE
            WHEN v.estado IN ('SP','RJ','MG','ES') THEN 'Sudeste'
            WHEN v.estado IN ('RS','SC','PR') THEN 'Sul'
            WHEN v.estado IN ('BA','PE','CE') THEN 'Nordeste'
            WHEN v.estado IN ('GO','MT','MS','DF') THEN 'Centro-Oeste'
            ELSE 'Outros'
        END,

        v.data_entrada

    FROM vendedores v;

    /* =====================================================
       DIM_PAGAMENTO
    ===================================================== */

    PRINT 'Carregando dim_pagamento...';

    INSERT INTO dw.dim_pagamento (
        tipo_pagamento,
        faixa_parcelas
    )

    SELECT DISTINCT
        p.tipo_pagamento,

        CASE
            WHEN p.parcelas = 1 THEN '1x'
            WHEN p.parcelas <= 3 THEN '2-3x'
            WHEN p.parcelas <= 6 THEN '4-6x'
            ELSE '7+x'
        END AS faixa_parcelas

    FROM pagamentos p;

    /* =====================================================
       DIM_ENTREGA
    ===================================================== */

    PRINT 'Carregando dim_entrega...';

    INSERT INTO dw.dim_entrega (
        tipo_entrega,
        faixa_prazo,
        entrega_atrasada
    )

    SELECT DISTINCT

        e.tipo_entrega,

        CASE
            WHEN DATEDIFF(DAY, e.data_envio, e.data_entrega_real) <= 3 THEN 'Ate 3 dias'
            WHEN DATEDIFF(DAY, e.data_envio, e.data_entrega_real) <= 7 THEN '4-7 dias'
            WHEN DATEDIFF(DAY, e.data_envio, e.data_entrega_real) <= 15 THEN '8-15 dias'
            ELSE '15+ dias'
        END AS faixa_prazo,

        CASE
            WHEN e.data_entrega_real > e.data_entrega_prevista
                THEN 'Sim'
            ELSE 'Nao'
        END AS entrega_atrasada

    FROM entregas e;

    /* =====================================================
       DIM_DATA
    ===================================================== */

    PRINT 'Carregando dim_data...';

    ;WITH datas AS (

        SELECT CAST('2022-01-01' AS DATE) AS data_ref

        UNION ALL

        SELECT DATEADD(DAY, 1, data_ref)

        FROM datas

        WHERE data_ref < '2030-12-31'
    )

    INSERT INTO dw.dim_data (
        sk_data,
        data_completa,
        dia,
        nome_dia_semana,
        semana_ano,
        mes,
        nome_mes,
        trimestre,
        semestre,
        ano,
        fim_semana
    )

    SELECT

        CAST(FORMAT(data_ref, 'yyyyMMdd') AS INT),

        data_ref,

        DAY(data_ref),

        DATENAME(WEEKDAY, data_ref),

        DATEPART(WEEK, data_ref),

        MONTH(data_ref),

        DATENAME(MONTH, data_ref),

        DATEPART(QUARTER, data_ref),

        CASE
            WHEN MONTH(data_ref) <= 6 THEN 1
            ELSE 2
        END,

        YEAR(data_ref),

        CASE
            WHEN DATENAME(WEEKDAY, data_ref)
                 IN ('Saturday', 'Sunday')
                THEN 1
            ELSE 0
        END

    FROM datas

    OPTION (MAXRECURSION 0);

    /* =====================================================
       FATO_VENDAS
    ===================================================== */

    PRINT 'Carregando fato_vendas...';

    INSERT INTO dw.fato_vendas (

        sk_cliente,
        sk_produto,
        sk_vendedor,
        sk_pagamento,
        sk_entrega,
        sk_data,

        id_pedido_origem,

        quantidade_itens,

        preco_unitario,
        valor_bruto,
        desconto,
        valor_frete,
        valor_liquido,

        custo_produto,
        lucro,

        prazo_entrega_dias,

        avaliacao
    )

    SELECT

        dc.sk_cliente,
        dp.sk_produto,
        dv.sk_vendedor,
        dpg.sk_pagamento,
        de.sk_entrega,

        CAST(FORMAT(CAST(pe.data_pedido AS DATE), 'yyyyMMdd') AS INT),

        pe.id_pedido,

        ip.quantidade,

        ip.preco_unitario,

        (ip.quantidade * ip.preco_unitario),

        ip.desconto,

        en.valor_frete,

        ((ip.quantidade * ip.preco_unitario)
            - ip.desconto
            + en.valor_frete),

        (pr.custo * ip.quantidade),

        (
            ((ip.quantidade * ip.preco_unitario)
                - ip.desconto
                + en.valor_frete)

            - (pr.custo * ip.quantidade)
        ),

        DATEDIFF(
            DAY,
            en.data_envio,
            en.data_entrega_real
        ),

        av.nota

    FROM itens_pedido ip

    INNER JOIN pedidos pe
        ON ip.id_pedido = pe.id_pedido

    INNER JOIN produtos pr
        ON ip.id_produto = pr.id_produto

    INNER JOIN pagamentos pg
        ON pe.id_pedido = pg.id_pedido

    INNER JOIN entregas en
        ON pe.id_pedido = en.id_pedido

    LEFT JOIN avaliacoes av
        ON pe.id_pedido = av.id_pedido

    INNER JOIN dw.dim_cliente dc
        ON pe.id_cliente = dc.id_cliente_origem

    INNER JOIN dw.dim_produto dp
        ON ip.id_produto = dp.id_produto_origem

    INNER JOIN dw.dim_vendedor dv
        ON ip.id_vendedor = dv.id_vendedor_origem

    INNER JOIN dw.dim_pagamento dpg
        ON pg.tipo_pagamento = dpg.tipo_pagamento

       AND
       (
            CASE
                WHEN pg.parcelas = 1 THEN '1x'
                WHEN pg.parcelas <= 3 THEN '2-3x'
                WHEN pg.parcelas <= 6 THEN '4-6x'
                ELSE '7+x'
            END
       ) = dpg.faixa_parcelas

    INNER JOIN dw.dim_entrega de
        ON en.tipo_entrega = de.tipo_entrega

       AND
       (
            CASE
                WHEN DATEDIFF(DAY, en.data_envio, en.data_entrega_real) <= 3
                    THEN 'Ate 3 dias'

                WHEN DATEDIFF(DAY, en.data_envio, en.data_entrega_real) <= 7
                    THEN '4-7 dias'

                WHEN DATEDIFF(DAY, en.data_envio, en.data_entrega_real) <= 15
                    THEN '8-15 dias'

                ELSE '15+ dias'
            END
       ) = de.faixa_prazo

       AND
       (
            CASE
                WHEN en.data_entrega_real > en.data_entrega_prevista
                    THEN 'Sim'
                ELSE 'Nao'
            END
       ) = de.entrega_atrasada;

    PRINT '=========================================';
    PRINT 'CARGA FINALIZADA COM SUCESSO';
    PRINT '=========================================';

END;
GO