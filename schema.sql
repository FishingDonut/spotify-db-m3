CREATE DATABASE IF NOT EXISTS spotify;
USE spotify;

SET FOREIGN_KEY_CHECKS = 0;

-- artista
DROP TABLE IF EXISTS Artista;
CREATE TABLE Artista (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(45) NOT NULL,
    descricao TEXT,
    seguidores INT DEFAULT 0,
    ouvintes_mensais INT DEFAULT 0
);

-- album 
DROP TABLE IF EXISTS Album;
CREATE TABLE Album (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(45) NOT NULL,
    ano INT NOT NULL,
    id_artista BIGINT NOT NULL,
    genero VARCHAR(45),
    capa_url VARCHAR(255),
    
    CONSTRAINT fk_album_artista
    FOREIGN KEY (id_artista) REFERENCES Artista(id)
);

-- musica
DROP TABLE IF EXISTS Musica;
CREATE TABLE Musica (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    duracao INT NOT NULL, -- em segundos
    reproducoes INT DEFAULT 0,
    letra TEXT,
    genero VARCHAR(45),
    ano INT NOT NULL,
    id_album BIGINT,
    id_artista BIGINT NOT NULL,
    
    CONSTRAINT fk_musica_album
    FOREIGN KEY (id_album) REFERENCES Album(id),
    
    CONSTRAINT fk_musica_artista
    FOREIGN KEY (id_artista) REFERENCES Artista(id)
);

-- plano
DROP TABLE IF EXISTS Plano;
CREATE TABLE Plano (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(15) NOT NULL, -- Free, Premium, Family, Student
    modalidade VARCHAR(15) NOT NULL, -- Mensal, Anual, Trimestral
    valor DECIMAL(10,2) NOT NULL,
    descricao VARCHAR(255)
);

-- pagamento
DROP TABLE IF EXISTS Pagamento;
CREATE TABLE Pagamento (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_plano BIGINT NOT NULL,
    data_assinatura DATE NOT NULL,
    vencimento DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Ativo', -- Ativo, Cancelado, Pendente
    
    CONSTRAINT fk_pagamento_plano
    FOREIGN KEY (id_plano) REFERENCES Plano(id)
);

-- usuario
DROP TABLE IF EXISTS Usuario;
CREATE TABLE Usuario (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(45) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    data_nascimento DATE,
    pais VARCHAR(45),
    id_pagamento BIGINT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_usuario_pagamento
    FOREIGN KEY (id_pagamento) REFERENCES Pagamento(id)
);

-- playlist
DROP TABLE IF EXISTS Playlist;
CREATE TABLE Playlist (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    salvamentos INT DEFAULT 0,
    id_usuario_autor BIGINT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    publica BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT fk_playlist_usuario
    FOREIGN KEY (id_usuario_autor) REFERENCES Usuario(id)
);

-- relacionamento n:n entre musica e playlist
DROP TABLE IF EXISTS Playlist_Musica;
CREATE TABLE Playlist_Musica (
    id_playlist BIGINT NOT NULL,
    id_musica BIGINT NOT NULL,
    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ordem INT,
    
    PRIMARY KEY (id_playlist, id_musica),
    CONSTRAINT fk_playlist_musica_playlist
    FOREIGN KEY (id_playlist) REFERENCES Playlist(id) ON DELETE CASCADE,
    CONSTRAINT fk_playlist_musica_musica
    FOREIGN KEY (id_musica) REFERENCES Musica(id) ON DELETE CASCADE
);

-- artista convidado colab/feat
DROP TABLE IF EXISTS Artista_Convidado;
CREATE TABLE Artista_Convidado (
    id_musica BIGINT NOT NULL,
    id_artista BIGINT NOT NULL,
    
    PRIMARY KEY (id_musica, id_artista),
    CONSTRAINT fk_artista_convidado_musica
    FOREIGN KEY (id_musica) REFERENCES Musica(id) ON DELETE CASCADE,
    CONSTRAINT fk_artista_convidado_artista
    FOREIGN KEY (id_artista) REFERENCES Artista(id) ON DELETE CASCADE
);

-- histórico de reprodução
DROP TABLE IF EXISTS Historico_Reproducao;
CREATE TABLE Historico_Reproducao (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    id_musica BIGINT NOT NULL,
    data_reproducao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_historico_usuario
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    CONSTRAINT fk_historico_musica
    FOREIGN KEY (id_musica) REFERENCES Musica(id) ON DELETE CASCADE
);

-- curtidas do usuário
DROP TABLE IF EXISTS Curtida;
CREATE TABLE Curtida (
    id_usuario BIGINT NOT NULL,
    id_musica BIGINT NOT NULL,
    data_curtida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id_usuario, id_musica),
    CONSTRAINT fk_curtida_usuario
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE,
    CONSTRAINT fk_curtida_musica
    FOREIGN KEY (id_musica) REFERENCES Musica(id) ON DELETE CASCADE
);

-- triggers e views
DELIMITER //
CREATE TRIGGER atualiza_reproducoes
AFTER INSERT ON Historico_Reproducao
FOR EACH ROW
BEGIN
    UPDATE Musica 
    SET reproducoes = reproducoes + 1 
    WHERE id = NEW.id_musica;
END//
DELIMITER ;

DROP VIEW IF EXISTS TopMusicas;
CREATE VIEW TopMusicas AS
SELECT m.titulo, a.nome as artista, m.reproducoes
FROM Musica m
JOIN Artista a ON m.id_artista = a.id
ORDER BY m.reproducoes DESC
LIMIT 10;


-- inserts
-- 1. Artistas
INSERT INTO Artista (id, nome, descricao, seguidores, ouvintes_mensais) VALUES 
(1, 'Jennie Kim', 'Cantora, rapper e compositora sul-coreana. Membro do BLACKPINK e artista solo.', 85000000, 12000000),
(2, 'Anavitória', 'Dupla brasileira de música popular formada por Ana Caetano e Vitória Falcão.', 5000000, 3500000);

-- 2. Planos
INSERT INTO Plano (id, tipo, modalidade, valor, descricao) VALUES 
(1, 'Free', 'Mensal', 0.00, 'Plano gratuito com anúncios'),
(2, 'Premium', 'Mensal', 19.90, 'Plano premium individual'),
(3, 'Premium', 'Anual', 199.00, 'Plano premium anual com desconto'),
(4, 'Premium', 'Familiar', 34.90, 'Plano para até 6 pessoas'),
(5, 'Premium', 'Universitário', 9.90, 'Plano para estudantes');

-- 3. Pagamentos
INSERT INTO Pagamento (id, id_plano, data_assinatura, vencimento, status) VALUES 
(1, 2, '2025-01-15', '2025-02-15', 'Ativo'),
(2, 3, '2025-01-01', '2026-01-01', 'Ativo'),
(3, 4, '2025-02-01', '2025-03-01', 'Ativo'),
(4, 2, '2024-12-10', '2025-01-10', 'Cancelado'),
(5, 5, '2025-01-20', '2025-02-20', 'Ativo');

-- 4. Usuários
INSERT INTO Usuario (id, nome, email, data_nascimento, pais, id_pagamento) VALUES 
(1, 'Mariana Silva', 'mariana.silva@email.com', '1998-03-15', 'Brasil', 1),
(2, 'João Pereira', 'joao.pereira@email.com', '1995-07-22', 'Brasil', 2),
(3, 'Carla Souza', 'carla.souza@email.com', '2000-11-05', 'Portugal', 3),
(4, 'Rafael Lima', 'rafael.lima@email.com', '1992-09-10', 'Brasil', 4),
(5, 'Ana Clara', 'ana.clara@email.com', '2001-05-18', 'Brasil', 5);

-- 5. Álbuns - Jennie
INSERT INTO Album (id, titulo, ano, id_artista, genero, capa_url) VALUES 
(1, 'Solo', 2018, 1, 'K-Pop', 'jennie_solo_album.jpg'),
(2, 'You & Me', 2023, 1, 'K-Pop', 'jennie_you_and_me.jpg'),
(3, 'Mantra', 2024, 1, 'Pop', 'jennie_mantra.jpg'),
(4, 'Anavitória', 2016, 2, 'MPB', 'anavitoria_2016.jpg'),
(5, 'O Tempo É Agora', 2018, 2, 'MPB', 'o_tempo_e_agora.jpg'),
(6, 'Cor', 2021, 2, 'MPB', 'cor_album.jpg'),
(7, 'Esquinas', 2023, 2, 'MPB', 'esquinas.jpg');

-- 7. Inserindo Músicas
INSERT INTO Musica (id, titulo, duracao, reproducoes, letra, genero, ano, id_album, id_artista) VALUES 
(1, 'Solo', 178, 350000000, 'I\'m going solo lo lo lo lo lo...', 'K-Pop', 2018, 1, 1),
(2, 'You & Me', 187, 150000000, 'Baby you and me...', 'K-Pop', 2023, 2, 1),
(3, 'Mantra', 156, 100000000, 'I\'m on my way...', 'Pop', 2024, 3, 1),
(4, 'Trevo (Tu)', 186, 300000000, 'Tu és o trevo que eu procurei...', 'MPB', 2016, 4, 2),
(5, 'Adelaide', 198, 280000000, 'Adelaide, Adelaide...', 'MPB', 2016, 4, 2),
(6, 'A Culpa É do Meu Coração', 210, 250000000, 'Eu não sei explicar...', 'MPB', 2018, 5, 2),
(7, 'Meu Eu em Você', 204, 180000000, 'Meu eu em você...', 'MPB', 2021, 6, 2),
(8, 'Amor de Marte', 192, 120000000, 'Amor de marte...', 'MPB', 2021, 6, 2),
(9, 'Esquinas', 215, 95000000, 'Nas esquinas...', 'MPB', 2023, 7, 2),
(10, 'Rua de Solidão', 188, 75000000, 'Na rua da solidão...', 'MPB', 2023, 7, 2);

-- 9. Inserindo Playlists
INSERT INTO Playlist (id, nome, descricao, salvamentos, id_usuario_autor, publica) VALUES 
(1, 'K-Pop Hits', 'As melhores músicas do K-Pop', 150000, 1, TRUE),
(2, 'MPB Relax', 'Música brasileira para relaxar', 80000, 2, TRUE),
(3, 'Jennie Solo', 'Todas as músicas da Jennie', 45000, 3, TRUE),
(4, 'Anavitória Completo', 'Discografia completa da dupla', 32000, 4, TRUE),
(5, 'Minhas Favoritas', 'Minha playlist pessoal', 5000, 5, FALSE);

-- 10.Playlist_Musica
-- Playlist K-Pop Hits (id 1)
INSERT INTO Playlist_Musica (id_playlist, id_musica, ordem) VALUES 
(1, 1, 1), -- Solo
(1, 2, 2), -- You & Me
(1, 3, 3); -- Mantra

-- Playlist MPB (id 2)
INSERT INTO Playlist_Musica (id_playlist, id_musica, ordem) VALUES 
(2, 4, 1), -- Trevo
(2, 5, 2), -- Adelaide
(2, 7, 3), -- Meu Eu em Você
(2, 9, 4), -- Esquinas
(2, 10, 5); -- Rua de Solidão

-- Playlist Jennie Solo (id 3)
INSERT INTO Playlist_Musica (id_playlist, id_musica, ordem) VALUES 
(3, 1, 1),
(3, 2, 2),
(3, 3, 3);

-- Playlist Anavitória Completo (id 4)
INSERT INTO Playlist_Musica (id_playlist, id_musica, ordem) VALUES 
(4, 4, 1),
(4, 5, 2),
(4, 6, 3),
(4, 7, 4),
(4, 8, 5),
(4, 9, 6),
(4, 10, 7);

-- 11. Histórico de Reprodução (últimas 24h)
INSERT INTO Historico_Reproducao (id_usuario, id_musica, data_reproducao) VALUES 
(1, 1, NOW() - INTERVAL 2 HOUR),
(1, 2, NOW() - INTERVAL 5 HOUR),
(2, 4, NOW() - INTERVAL 3 HOUR),
(2, 5, NOW() - INTERVAL 4 HOUR),
(3, 1, NOW() - INTERVAL 1 HOUR),
(3, 3, NOW() - INTERVAL 6 HOUR),
(4, 4, NOW() - INTERVAL 7 HOUR),
(4, 8, NOW() - INTERVAL 8 HOUR),
(5, 6, NOW() - INTERVAL 9 HOUR),
(5, 9, NOW() - INTERVAL 10 HOUR),
(1, 3, NOW() - INTERVAL 11 HOUR),
(2, 7, NOW() - INTERVAL 12 HOUR);

-- 12. Curtidas
INSERT INTO Curtida (id_usuario, id_musica, data_curtida) VALUES 
(1, 1, NOW() - INTERVAL 1 DAY),
(1, 2, NOW() - INTERVAL 2 DAY),
(2, 4, NOW() - INTERVAL 3 DAY),
(2, 5, NOW() - INTERVAL 4 DAY),
(3, 1, NOW() - INTERVAL 5 DAY),
(3, 3, NOW() - INTERVAL 6 DAY),
(4, 4, NOW() - INTERVAL 7 DAY),
(4, 9, NOW() - INTERVAL 8 DAY),
(5, 6, NOW() - INTERVAL 9 DAY),
(5, 10, NOW() - INTERVAL 10 DAY);

-- 13. colabs
INSERT INTO Artista_Convidado (id_musica, id_artista) VALUES 
(1, 2), 
(2, 2);

SET FOREIGN_KEY_CHECKS = 1;
