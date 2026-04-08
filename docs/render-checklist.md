# Checklist de Deploy no Render (modo gratuito, sem Redis)

Este guia é para subir o projeto em modo gratuito, **sem Redis**, para validação inicial.

## O que o blueprint cria

- `seuservico-api` (web)
- `seuservico-db` (PostgreSQL)

> Neste modo, **worker/cron e Redis ficam de fora** para simplificar custo e operação.

## Passo a passo

1. No Render, clique em **New +**.
2. Clique em **Blueprint**.
3. Selecione o repositório.
4. Confirme o `render.yaml`.
5. Clique em **Apply**.

## Variáveis obrigatórias

No serviço `seuservico-api`, configure:

- `SECRET_KEY` (obrigatória)
- `DATABASE_URL` (já vinculada automaticamente pelo blueprint)
- `REDIS_URL` fica vazia (`""`) neste modo gratuito

## Ordem recomendada

1. Aguarde o banco `seuservico-db` ficar **Available**.
2. Faça deploy do `seuservico-api`.
3. Rode migração no shell da API:

```bash
alembic upgrade head
```

## Validação

- Abra: `https://<seu-servico-api>.onrender.com/docs`
- Teste cadastro/login básicos e endpoints principais.

## Impacto de remover Redis (esperado)

Com Redis desativado:

- ✅ API principal e banco continuam funcionando.
- ⚠️ Blacklist de token (logout/refresh com invalidação forte) vira modo degradado.
- ⚠️ Cache fica desativado.
- ⚠️ Celery worker/cron não rodam neste blueprint gratuito.

Quando decidir evoluir, adicionamos Redis + worker + cron sem quebrar a base.
