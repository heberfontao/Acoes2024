-- Tabelas
CREATE TABLE IF NOT EXISTS `usuarios` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `senha` VARCHAR(255) NOT NULL,
    `foto_perfil` VARCHAR(255),
    `cursos` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `email_UNIQUE` (`email`)
);

CREATE TABLE IF NOT EXISTS `taxas` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(255) NOT NULL,
    `aliquota` INT NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `acoes` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(255) NOT NULL,
    `ticker` VARCHAR(10) NOT NULL,
	`preco_atual` decimal(20,14) NOT NULL,
    `preco_minimo` decimal(20,14) NOT NULL,
    `preco_maximo` decimal(20,14) NOT NULL,
    `preco_medio_alvo` decimal(20,14) NOT NULL,
    `preco_medio_desejado` decimal(20,14) NOT NULL,
  	`preco_data` date NOT NULL,
    `setor` VARCHAR(255) NOT NULL,
    `sub_setor` VARCHAR(255) NOT NULL,
    `recomendacao` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `movimentacoes` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `id_acao` INT NOT NULL,
    `id_usuario` INT NOT NULL,
    `data` DATE NOT NULL,
    `cd_tipo` INT NOT NULL,
    `quantidade` INT NOT NULL,
    `valor_unitario` DECIMAL(10,2) NOT NULL,
    `total_taxas` DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`),
    FOREIGN KEY (`id_acao`) REFERENCES `acoes` (`id`)
);

-- Views
CREATE OR REPLACE VIEW carteira AS
SELECT
	m.id_usuario,
    m.id_acao,
	a.ticker,
	a.nome,
	a.preco_atual,
	SUM(CASE WHEN cd_tipo = 2 THEN m.quantidade * (-1) ELSE m.quantidade END) as quantidade,
	SUM(CASE WHEN cd_tipo = 2 THEN m.quantidade * (-1) ELSE m.quantidade END) * a.preco_atual as valor,
    CASE 
        WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
            SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
            / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)
        ELSE 0
    END AS valor_medio,
	(a.preco_atual 
	- (CASE 
        WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
            SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
            / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)
        ELSE 0
    END))
	/ (CASE 
        WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
            SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
            / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)
        ELSE 0
    END) * 100 AS rentabilidade_percentual,
	a.preco_atual 
	- (CASE 
        WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
            SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
            / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)
        ELSE 0
    END)  AS rentabilidade_valor
FROM
    movimentacoes m
	inner join acoes a on m.id_acao = a.id
GROUP BY
    m.id_usuario,
    m.id_acao,
	a.ticker,
	a.nome,
	a.preco_atual;
	
CREATE OR REPLACE VIEW carteira_por_usuario AS
SELECT 
	id_usuario, 
    count(distinct id_acao) as quantidade,
    sum(valor) as valor,
	sum(valor - (valor_medio * quantidade)) as rentabilidade_valor,
	sum((valor - (valor_medio * quantidade)) / (valor_medio * quantidade)) as rentabilidade_percentual
FROM 
	carteira
GROUP BY
	id_usuario;
	
CREATE OR REPLACE VIEW resultado as 	
SELECT
	m.id_usuario,
	date_format(m.data,'%m/%Y') as periodo,
    m.id_acao,
	a.ticker,
	a.nome,
	a.preco_atual,
    SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) AS total_compras,
    SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) AS total_quantidade_comprada,
    SUM(CASE WHEN m.cd_tipo = 2 THEN (m.valor_unitario * m.quantidade) - m.total_taxas ELSE 0 END) AS total_vendas,
    SUM(CASE WHEN m.cd_tipo = 2 THEN m.quantidade ELSE 0 END) AS total_quantidade_vendida,
	SUM(m.total_taxas) AS total_taxas,
    CASE 
        WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
            SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
            / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)
        ELSE 0
    END AS custo_medio,
    SUM(CASE WHEN m.cd_tipo = 2 THEN (m.valor_unitario * m.quantidade) - m.total_taxas ELSE 0 END) - 
    (CASE 
        WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
            (SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
            / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)) 
            * SUM(CASE WHEN m.cd_tipo = 2 THEN m.quantidade ELSE 0 END)
        ELSE 0
    END) AS lucro_prejuizo,
    CASE 
        WHEN SUM(CASE WHEN m.cd_tipo = 2 THEN m.quantidade ELSE 0 END) > 0 THEN
            ((SUM(CASE WHEN m.cd_tipo = 2 THEN (m.valor_unitario * m.quantidade) - m.total_taxas ELSE 0 END) - 
            (CASE 
                WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
                    (SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
                    / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)) 
                    * SUM(CASE WHEN m.cd_tipo = 2 THEN m.quantidade ELSE 0 END)
                ELSE 0
            END)) / 
            (CASE 
                WHEN SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END) > 0 THEN
                    (SUM(CASE WHEN m.cd_tipo = 1 THEN (m.valor_unitario * m.quantidade) + m.total_taxas ELSE 0 END) 
                    / SUM(CASE WHEN m.cd_tipo = 1 THEN m.quantidade ELSE 0 END)) 
                    * SUM(CASE WHEN m.cd_tipo = 2 THEN m.quantidade ELSE 0 END)
                ELSE 0
            END)) * 100
        ELSE 0
    END AS rentabilidade_percentual
FROM
    movimentacoes m
	inner join acoes a on m.id_acao = a.id
GROUP BY
    m.id_usuario,
	date_format(m.data,'%m/%Y'),
    m.id_acao,
	a.ticker,
	a.nome,
	a.preco_atual
ORDER BY
	m.data;
	
CREATE OR REPLACE VIEW resultado_por_ticker as
SELECT 
	r.id_usuario,
	r.periodo,
	r.id_acao,
	r.ticker, 
	r.nome,
	r.preco_atual,
	sum(r.total_compras) as total_compras,
    sum(r.total_quantidade_comprada) as total_quantidade_comprada,
    sum(r.total_vendas) as total_vendas,
    sum(r.total_quantidade_vendida) as total_quantidade_vendida,
	sum(r.total_taxas) as total_taxas,
    sum(r.custo_medio) as custo_medio,
    sum(r.lucro_prejuizo) as lucro_prejuizo,
    sum(r.rentabilidade_percentual) as rentabilidade_percentual
FROM 
	resultado r
GROUP BY
	r.id_usuario,
	r.periodo,
	r.id_acao,
	r.ticker, 
	r.nome,
	r.preco_atual;
	
CREATE OR REPLACE VIEW resultado_por_periodo as
SELECT 
	r.id_usuario,
	r.periodo,
	sum(r.total_compras) as total_compras,
    sum(r.total_quantidade_comprada) as total_quantidade_comprada,
    sum(r.total_vendas) as total_vendas,
    sum(r.total_quantidade_vendida) as total_quantidade_vendida,
	sum(r.total_taxas) as total_taxas,
    sum(r.custo_medio) as custo_medio,
    sum(r.lucro_prejuizo) as lucro_prejuizo,
    sum(r.rentabilidade_percentual) as rentabilidade_percentual
FROM 
	resultado r
GROUP BY
	r.id_usuario,
	r.periodo;

