# SeuServiço — Backend API

Backend completo em Python/FastAPI para o app **SeuServiço**, que conecta clientes a prestadores de serviços locais.

---

## Stack

| Tecnologia | Função |
|---|---|
| FastAPI | Framework web / REST API |
| SQLAlchemy 2.0 | ORM |
| PostgreSQL | Banco de dados principal |
| Alembic | Migrações de banco |
| Pydantic v2 | Validação de dados |
| python-jose | JWT (autenticação) |
| passlib + bcrypt | Hash de senhas |
| Socket.IO | Chat em tempo real |
| Redis | Cache + blacklist de tokens |
| Celery | Tarefas assíncronas (e-mail, push, cleanup) |

---

## Estrutura

```
seuservico/
├── app/
│   ├── api/v1/endpoints/   # auth, users, professionals, services, chat, admin
│   ├── core/               # config, security, deps
│   ├── db/                 # session, base, redis
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Lógica de negócio
│   ├── tasks/              # Celery tasks
│   ├── socketio_server.py  # Chat em tempo real
│   └── main.py             # Entrypoint FastAPI + Socket.IO
├── alembic/                # Migrações
├── tests/                  # Testes automatizados
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Início Rápido

### 1. Pré-requisitos
- Docker & Docker Compose **ou** Python 3.11+, PostgreSQL, Redis

### 2. Com Docker (recomendado)

```bash
cp .env.example .env
# Edite .env com suas configurações
docker-compose up --build
```

API disponível em: `http://localhost:8000`  
Docs interativos: `http://localhost:8000/docs`

### 3. Sem Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Edite com suas credenciais

# Criar banco e rodar migrações
alembic upgrade head

# Iniciar API
uvicorn app.main:socket_app --reload --port 8000

# Iniciar worker Celery (outro terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Iniciar Celery Beat (outro terminal)
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## Endpoints Principais

### Auth `/api/v1/auth`
| Método | Rota | Descrição |
|---|---|---|
| POST | `/register` | Cadastro de usuário |
| POST | `/login` | Login → JWT |
| POST | `/refresh` | Renovar token |
| POST | `/logout` | Logout |
| POST | `/forgot-password` | Solicitar reset |
| POST | `/reset-password` | Resetar senha |

### Usuários `/api/v1/users`
| Método | Rota | Descrição |
|---|---|---|
| GET | `/me` | Perfil do usuário logado |
| PUT | `/me` | Atualizar perfil |
| PUT | `/me/password` | Alterar senha |
| POST | `/me/avatar` | Upload de avatar |
| GET | `/me/services` | Histórico de serviços |

### Profissionais `/api/v1/professionals`
| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Listar com filtros (category, service, city, rating) |
| GET | `/{id}` | Detalhes do profissional |
| POST | `/register` | Criar perfil profissional |
| PUT | `/me` | Atualizar perfil |
| POST | `/me/portfolio` | Adicionar imagem |
| DELETE | `/me/portfolio/{image_id}` | Remover imagem |
| GET | `/me/stats` | Estatísticas |
| GET/PUT | `/me/availability` | Disponibilidade |

### Serviços `/api/v1/services`
| Método | Rota | Descrição |
|---|---|---|
| POST | `/requests` | Criar solicitação |
| GET | `/requests/client` | Serviços do cliente |
| GET | `/requests/professional` | Serviços do profissional |
| PUT | `/requests/{id}/accept` | Aceitar |
| PUT | `/requests/{id}/reject` | Recusar |
| PUT | `/requests/{id}/start` | Iniciar |
| PUT | `/requests/{id}/complete` | Concluir |
| PUT | `/requests/{id}/cancel` | Cancelar |
| POST | `/requests/{id}/rate` | Avaliar (1-5 estrelas) |

### Chat `/api/v1/chat`
| Método | Rota | Descrição |
|---|---|---|
| GET | `/conversations` | Listar conversas |
| GET | `/conversations/{id}/messages` | Mensagens |
| POST | `/conversations/{id}/messages` | Enviar mensagem |
| PUT | `/messages/{id}/read` | Marcar como lida |

### Admin `/api/v1/admin`
| Método | Rota | Descrição |
|---|---|---|
| GET | `/dashboard/stats` | Métricas gerais |
| GET | `/professionals/pending` | Aguardando aprovação |
| PUT | `/professionals/{id}/verify` | Aprovar profissional |
| PUT | `/professionals/{id}/feature` | Destacar (premium) |
| GET | `/users` | Listar usuários |
| PUT | `/users/{id}/block` | Bloquear usuário |
| GET | `/reports/metrics` | Relatórios |
| GET | `/reviews/reported` | Avaliações reportadas |
| PUT | `/reviews/{id}/moderate` | Moderar avaliação |

---

## Socket.IO — Chat em Tempo Real

Conecte-se ao servidor com um token JWT:

```javascript
const socket = io("http://localhost:8000", {
  auth: { token: "seu_access_token" }
});

// Entrar em uma conversa
socket.emit("join_chat", { chat_id: "uuid-do-chat" });

// Enviar mensagem
socket.emit("send_message", { chat_id: "uuid", content: "Olá!" });

// Receber mensagens
socket.on("new_message", (msg) => console.log(msg));

// Indicador de digitação
socket.emit("typing", { chat_id: "uuid" });
socket.on("user_typing", ({ user_id }) => console.log(user_id, "está digitando..."));
```

---

## Testes

```bash
pytest tests/ -v
```

---

## Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL do PostgreSQL |
| `REDIS_URL` | URL do Redis |
| `SECRET_KEY` | Chave JWT (use algo longo e aleatório) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (padrão: 30) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (padrão: 7) |
| `UPLOAD_DIR` | Diretório de uploads (padrão: `uploads`) |
| `SMTP_*` | Configurações de e-mail (opcional) |
