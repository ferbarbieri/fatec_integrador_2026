USE FatecShop2;
GO

/* =========================================================
   REMOVER CONSTRAINTS TEMPORARIAMENTE
========================================================= */

ALTER TABLE avaliacoes DROP CONSTRAINT fk_avaliacao_pedido;

ALTER TABLE entregas DROP CONSTRAINT fk_entrega_pedido;

ALTER TABLE pagamentos DROP CONSTRAINT fk_pagamento_pedido;

ALTER TABLE itens_pedido DROP CONSTRAINT fk_item_pedido;
ALTER TABLE itens_pedido DROP CONSTRAINT fk_item_produto;
ALTER TABLE itens_pedido DROP CONSTRAINT fk_item_vendedor;

ALTER TABLE pedidos DROP CONSTRAINT fk_pedido_cliente;

ALTER TABLE produtos_promocoes DROP CONSTRAINT fk_produto_promocao_produto;
ALTER TABLE produtos_promocoes DROP CONSTRAINT fk_produto_promocao_promocao;

ALTER TABLE produtos DROP CONSTRAINT fk_produto_subcategoria;

ALTER TABLE subcategorias DROP CONSTRAINT fk_subcategoria_categoria;

ALTER TABLE enderecos_clientes DROP CONSTRAINT fk_endereco_cliente;

GO

/* =========================================================
   TRUNCATE
========================================================= */

TRUNCATE TABLE avaliacoes;
TRUNCATE TABLE entregas;
TRUNCATE TABLE pagamentos;
TRUNCATE TABLE itens_pedido;
TRUNCATE TABLE pedidos;
TRUNCATE TABLE produtos_promocoes;
TRUNCATE TABLE promocoes;
TRUNCATE TABLE produtos;
TRUNCATE TABLE subcategorias;
TRUNCATE TABLE categorias;
TRUNCATE TABLE vendedores;
TRUNCATE TABLE enderecos_clientes;
TRUNCATE TABLE clientes;

GO

/* =========================================================
   RECRIAR CONSTRAINTS
========================================================= */

ALTER TABLE enderecos_clientes
ADD CONSTRAINT fk_endereco_cliente
FOREIGN KEY (id_cliente)
REFERENCES clientes(id_cliente);

ALTER TABLE subcategorias
ADD CONSTRAINT fk_subcategoria_categoria
FOREIGN KEY (id_categoria)
REFERENCES categorias(id_categoria);

ALTER TABLE produtos
ADD CONSTRAINT fk_produto_subcategoria
FOREIGN KEY (id_subcategoria)
REFERENCES subcategorias(id_subcategoria);

ALTER TABLE produtos_promocoes
ADD CONSTRAINT fk_produto_promocao_produto
FOREIGN KEY (id_produto)
REFERENCES produtos(id_produto);

ALTER TABLE produtos_promocoes
ADD CONSTRAINT fk_produto_promocao_promocao
FOREIGN KEY (id_promocao)
REFERENCES promocoes(id_promocao);

ALTER TABLE pedidos
ADD CONSTRAINT fk_pedido_cliente
FOREIGN KEY (id_cliente)
REFERENCES clientes(id_cliente);

ALTER TABLE itens_pedido
ADD CONSTRAINT fk_item_pedido
FOREIGN KEY (id_pedido)
REFERENCES pedidos(id_pedido);

ALTER TABLE itens_pedido
ADD CONSTRAINT fk_item_produto
FOREIGN KEY (id_produto)
REFERENCES produtos(id_produto);

ALTER TABLE itens_pedido
ADD CONSTRAINT fk_item_vendedor
FOREIGN KEY (id_vendedor)
REFERENCES vendedores(id_vendedor);

ALTER TABLE pagamentos
ADD CONSTRAINT fk_pagamento_pedido
FOREIGN KEY (id_pedido)
REFERENCES pedidos(id_pedido);

ALTER TABLE entregas
ADD CONSTRAINT fk_entrega_pedido
FOREIGN KEY (id_pedido)
REFERENCES pedidos(id_pedido);

ALTER TABLE avaliacoes
ADD CONSTRAINT fk_avaliacao_pedido
FOREIGN KEY (id_pedido)
REFERENCES pedidos(id_pedido);

GO

/* =========================================================
   RESET IDENTITIES
========================================================= */

DBCC CHECKIDENT ('clientes', RESEED, 0);
DBCC CHECKIDENT ('enderecos_clientes', RESEED, 0);
DBCC CHECKIDENT ('vendedores', RESEED, 0);
DBCC CHECKIDENT ('categorias', RESEED, 0);
DBCC CHECKIDENT ('subcategorias', RESEED, 0);
DBCC CHECKIDENT ('produtos', RESEED, 0);
DBCC CHECKIDENT ('promocoes', RESEED, 0);
DBCC CHECKIDENT ('produtos_promocoes', RESEED, 0);
DBCC CHECKIDENT ('pedidos', RESEED, 0);
DBCC CHECKIDENT ('itens_pedido', RESEED, 0);
DBCC CHECKIDENT ('pagamentos', RESEED, 0);
DBCC CHECKIDENT ('entregas', RESEED, 0);
DBCC CHECKIDENT ('avaliacoes', RESEED, 0);

GO