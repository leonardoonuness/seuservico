# Checklist de Deploy no Render (passo a passo)

Este guia foi feito para o blueprint `render.yaml` deste repositório.

## 1) Pré-requisitos

- Repositório no GitHub com o arquivo `render.yaml` na raiz.
- Conta no Render conectada ao GitHub.
- Uma `SECRET_KEY` forte para JWT (deve ser **igual** em API, worker e cron).

## 2) Criar stack via Blueprint

1. No Render, clique em **New +**.
2. Clique em **Blueprint**.
3. Selecione o repositório.
4. Confirme que o arquivo detectado é `render.yaml`.
5. Clique em **Apply** para criar os serviços.

Serviços criados pelo blueprint:
- `seuservico-api` (web)
- `seuservico-worker` (worker)
- `seuservico-cron-cleanup` (cron)
- `seuservico-db` (PostgreSQL)

> Observação: nesta versão do blueprint, o Redis **não é provisionado automaticamente** (evita erro de schema no campo `keyvalue`).
- `seuservico-redis` (Redis)

## 3) Configurar variáveis obrigatórias

Após os serviços existirem, abra cada um dos 3 processos de aplicação (`api`, `worker`, `cron`) e configure:

- `SECRET_KEY` com **exatamente o mesmo valor** nos três serviços.
- Ajuste opcional de:
  - `ACCESS_TOKEN_EXPIRE_MINUTES` (padrão no blueprint: `30`)
  - `REFRESH_TOKEN_EXPIRE_DAYS` (padrão no blueprint: `7`)
  - `UPLOAD_DIR` (padrão no blueprint: `uploads`)

> `DATABASE_URL` é vinculado automaticamente pelo blueprint.
> `REDIS_URL` deve ser preenchido manualmente com a URL do Redis que você criar no Render (ou externo).

## 4) Ordem de deploy recomendada

1. Aguarde `seuservico-db` ficar **Available**.
2. Crie um Redis no Render (ou use externo) e copie a URL.
3. Preencha `REDIS_URL` (igual) em `seuservico-api`, `seuservico-worker` e `seuservico-cron-cleanup`.
4. Faça deploy do `seuservico-api`.
5. Faça deploy do `seuservico-worker`.
6. Faça deploy do `seuservico-cron-cleanup`.
> `DATABASE_URL` e `REDIS_URL` já são vinculados automaticamente pelo blueprint.

## 4) Ordem de deploy recomendada

1. Aguarde primeiro `seuservico-db` e `seuservico-redis` ficarem **Available**.
2. Faça deploy do `seuservico-api`.
3. Faça deploy do `seuservico-worker`.
4. Faça deploy do `seuservico-cron-cleanup`.

## 5) Rodar migrações Alembic (primeiro deploy)

No shell do serviço `seuservico-api`, execute:

```bash
alembic upgrade head
```

## 6) Validação pós-deploy

- API no ar: abra `https://<seu-servico-api>.onrender.com/docs`
- Worker conectado ao broker: verifique logs do `seuservico-worker`.
- Cron executando: confira logs do `seuservico-cron-cleanup` no horário agendado.

## 7) Troubleshooting rápido

- **401/erros de JWT entre API e worker/cron**: normalmente `SECRET_KEY` diferente.
- **Erro de conexão no banco**: aguarde DB ficar `Available` antes do deploy da API.
- **Tasks não processam**: confirme `REDIS_URL` igual nos 3 serviços e logs de conexão ao Redis.
- **Tasks não processam**: confirme `REDIS_URL` em worker/cron e logs de conexão.

## 8) O que foi possível executar automaticamente neste ambiente

- Validação de sintaxe YAML do `render.yaml`.

Não foi possível executar deploy real no Render por depender de:
- autenticação da sua conta Render,
- conexão do seu GitHub no painel,
- aprovação/aplicação do blueprint no seu workspace.

## 9) Se ocorrer conflito de merge no Git

Se você estiver na branch destino (ex.: `main`) e quiser manter a versão deste PR para os arquivos de deploy:

```bash
git merge <branch-do-pr>
git checkout --theirs render.yaml docs/render-checklist.md
git add render.yaml docs/render-checklist.md
git commit -m "Resolve conflicts keeping Render deploy files"
```

> Dica: em merges, `--theirs` normalmente representa a branch que está sendo mesclada.
