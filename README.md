# Spotify DB Manager - Trabalho Univali M3 (Banco de Dados)

Este é um projeto desenvolvido em **Python** utilizando **Flask**, **Flask-SQLAlchemy** e **MySQL** para gerenciar um clone simplificado do banco de dados do Spotify. O objetivo do projeto é demonstrar a modelagem relacional funcional (MER), contendo tabelas com chaves primárias/estrangeiras, operações de **CRUD**, **Gatilhos (Triggers)**, **Visões (Views)** e dados de teste.

---

## 🛠️ Tecnologias e Dependências

A estrutura do projeto já vem pré-configurada com as seguintes dependências instaladas no ambiente virtual (`.venv`):
- **Flask**: Servidor web da aplicação e API REST.
- **Flask-SQLAlchemy**: ORM para gerenciar o mapeamento objeto-relacional e executar consultas.
- **PyMySQL**: Conector Python para comunicação com o MySQL.
- **HTML/CSS/JS (Vanilla)**: Interface web do painel.

---

## 🚀 Como Rodar o Projeto

### 1. Pré-requisitos
- Certifique-se de que o **MySQL Server** esteja ativo em sua máquina.
- Por padrão, o projeto está configurado para conectar ao MySQL no endereço `localhost` com o usuário `root` e senha `root`. 
  * Se o seu usuário ou senha forem diferentes, ajuste a linha `10` do arquivo `main.py`:
    ```python
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://seu_usuario:sua_senha@localhost/spotify'
    ```

### 2. Ativar o Ambiente Virtual e Iniciar o Servidor
Abra o terminal na pasta raiz do projeto e execute os seguintes comandos:

**No Windows (PowerShell):**
```powershell
.venv\Scripts\activate
python main.py
```

**No Linux/macOS:**
```bash
source .venv/bin/activate
python main.py
```

---

## 💾 Inicialização Automática do Banco de Dados

Ao iniciar o servidor (`python main.py`), a aplicação executará automaticamente o script [schema.sql](schema.sql). Esse script realiza as seguintes operações no MySQL:
1. Cria a base de dados `spotify` (caso não exista).
2. Suspende temporariamente as validações de chaves estrangeiras para fazer o `DROP` seguro de tabelas preexistentes.
3. Cria todas as tabelas principais e de relacionamento.
4. Cria o Gatilho **`atualiza_reproducoes`** (Trigger) para incrementar a contagem de execuções de músicas automaticamente.
5. Cria a Visão **`TopMusicas`** (View) para listar as 10 músicas mais ouvidas.
6. Insere os dados de exemplo (semeamento) para todas as tabelas.

Se tudo correr bem, você verá a mensagem no console:
> *Tabelas, triggers, visões e dados de sementes inicializados com sucesso!*

---

## 🌐 Como Usar a Interface Web

Após iniciar a aplicação, abra o seu navegador e acesse:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

Na interface web, você poderá navegar e gerenciar as **4 entidades principais**:

1.  **Navegação Lateral**: Alterne facilmente entre as seções de **Artistas**, **Álbuns**, **Músicas**, **Usuários** e **Top 10**.
2.  **Operações de CRUD**:
    *   **Inserir (Create)**: Clique no botão verde superior (ex: *"Novo Artista"*) para preencher o formulário. O formulário de músicas e usuários carrega automaticamente seletores dinâmicos baseados no banco de dados.
    *   **Visualizar (Read)**: Dados das tabelas são mostrados dinamicamente. A barra de busca no topo permite buscar registros pelo nome.
    *   **Atualizar (Update)**: Clique no botão de lápis (verde) na linha de um registro para editar suas informações no modal.
    *   **Remover (Delete)**: Clique no botão de lixeira (vermelho) para remover o registro do banco de dados (respeitando as regras de chaves estrangeiras).
3.  **Simulação do Gatilho (Trigger)**:
    *   Na página de **Músicas**, clique no ícone verde de **Play** à esquerda do ID de qualquer música.
    *   Isso enviará uma requisição inserindo um histórico de reprodução. O gatilho `atualiza_reproducoes` no MySQL atualizará automaticamente a contagem de reproduções em tempo real na tela.
4.  **Consulta de Visão (View)**:
    *   Na seção **Top 10 (View)**, a tabela lista em tempo real o ranking das músicas consumindo diretamente a View `TopMusicas` do banco de dados.
5.  **Console de Desenvolvedor (F12)**:
    *   Se você abrir a ferramenta de desenvolvedor do navegador (F12) e acessar a aba **Console**, poderá ver o log em tempo real de cada comando SQL executado no banco a cada clique de ação na interface!

---

## 🔌 Como Usar a API via Insomnia / Postman

Se desejar testar os endpoints da API por um cliente externo:

- **Endereço Base**: `http://127.0.0.1:5000`
- **Cabeçalho obrigatório para POST e PUT**: `Content-Type: application/json`

### Endpoints Disponíveis:

| Recurso | Método | Rota | Descrição |
| :--- | :--- | :--- | :--- |
| **Artistas** | `GET` | `/api/artistas` | Lista todos os artistas (Aceita query `?search=nome`) |
| | `POST` | `/api/artistas` | Adiciona um artista no banco |
| | `PUT` | `/api/artistas/<id>` | Atualiza os dados de um artista específico |
| | `DELETE`| `/api/artistas/<id>` | Remove um artista |
| **Álbuns** | `GET` | `/api/albuns` | Lista álbuns relacionando nomes de artistas |
| | `POST` | `/api/albuns` | Adiciona um álbum vinculado a um artista |
| | `PUT` | `/api/albuns/<id>` | Atualiza dados do álbum |
| | `DELETE`| `/api/albuns/<id>` | Remove um álbum |
| **Músicas** | `GET` | `/api/musicas` | Lista músicas relacionando álbuns e artistas |
| | `POST` | `/api/musicas` | Adiciona uma música |
| | `PUT` | `/api/musicas/<id>` | Atualiza dados da música |
| | `DELETE`| `/api/musicas/<id>` | Remove uma música |
| | `POST` | `/api/musicas/<id>/reproduzir` | Insere no histórico de reprodução (Ativa Trigger) |
| **Usuários**| `GET` | `/api/usuarios` | Lista usuários com plano e status de assinatura |
| | `POST` | `/api/usuarios` | Adiciona um novo usuário |
| | `PUT` | `/api/usuarios/<id>` | Atualiza dados do usuário |
| | `DELETE`| `/api/usuarios/<id>` | Remove um usuário |
| **Visão** | `GET` | `/api/top-musicas` | Consulta a View `TopMusicas` no MySQL |

#### Exemplo de Payload para Criar Artista (`POST /api/artistas`):
```json
{
  "nome": "Anitta",
  "descricao": "Cantora e compositora brasileira.",
  "seguidores": 65000000,
  "ouvintes_mensais": 28000000
}
```

---

## 📝 Comentários do Comando SQL Abstraído (Requisito da M3)
Como exigido nas instruções do trabalho, todas as rotas e interações com o banco dentro do arquivo `main.py` contêm comentários estruturados detalhando a sintaxe SQL real que está sendo executada através das consultas SQLAlchemy.

*Exemplo de comentário encontrado no código:*
```python
# COMENTÁRIO SQL ABSTRAÍDO:
# UPDATE Artista SET nome = :nome, descricao = :descricao, seguidores = :seguidores, ouvintes_mensais = :ouvintes_mensais WHERE id = :id;
```
