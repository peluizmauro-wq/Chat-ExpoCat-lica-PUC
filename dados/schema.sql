-- Modelo relacional usado no protótipo
CREATE TABLE expositores (
  expositor_id VARCHAR PRIMARY KEY,
  nome_fantasia VARCHAR,
  segmento VARCHAR,
  cidade VARCHAR,
  uf VARCHAR,
  status_contrato VARCHAR,
  email_demo VARCHAR
);

CREATE TABLE estandes (
  estande_id VARCHAR PRIMARY KEY,
  expositor_id VARCHAR REFERENCES expositores(expositor_id),
  codigo_estande VARCHAR,
  setor VARCHAR,
  metragem_m2 INTEGER,
  tipo_montagem VARCHAR
);

CREATE TABLE pendencias (
  pendencia_id VARCHAR PRIMARY KEY,
  expositor_id VARCHAR REFERENCES expositores(expositor_id),
  descricao VARCHAR,
  status VARCHAR,
  prazo DATE,
  prioridade VARCHAR
);
