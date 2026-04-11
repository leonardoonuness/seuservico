# 🚀 Deploy no Render - Guia de Atualização

## Instruções para Deploy

### 1. Fazer Push do Código
```bash
git add .
git commit -m "fix: corrigir erro 500 na rota de registro - remover Enum, adicionar validação"
git push
```

### 2. Render fará rebuild automaticamente
- A aplicação será reiniciada
- `Base.metadata.create_all()` será executado
- Tabelas serão criadas/atualizadas

### 3. Verificar Logs no Render
```
Dashboard → Services → seuserviço-api → Logs

Procurar por:
✅ "Creating all tables"
✅ "Application startup complete"
```

---

## ✅ Teste de Produção

### Após deploy, testar:

```bash
# 1. Teste simples de registro
curl -X POST https://seu-app.render.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste Render",
    "email": "teste'$(date +%s)'@render.com",
    "password": "TestPassword123",
    "type": "client",
    "phone": "11987654321",
    "city": "São Paulo"
  }'

# Esperado: 201 Created com tokens
```

### 2. Teste de erro (email duplicado)
```bash
# Usar o mesmo email do teste anterior
curl -X POST https://seu-app.render.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Duplo",
    "email": "teste@render.com",
    "password": "TestPassword123",
    "type": "client",
    "phone": "11987654321",
    "city": "São Paulo"
  }'

# Esperado: 409 Conflict (não 500)
```

### 3. Teste de validação (type inválido)
```bash
curl -X POST https://seu-app.render.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Inválido",
    "email": "invalido@render.com",
    "password": "TestPassword123",
    "type": "invalid_type",
    "phone": "11987654321",
    "city": "São Paulo"
  }'

# Esperado: 400 Bad Request
```

---

## 🔍 Monitorar em Produção

### Logs para acompanhar:
```
✅ "Registering new user: email@example.com"
✅ "User registered successfully: user_id"
⚠️ "Email already registered: email@example.com"
❌ "Database integrity error"
```

### Alertas (se ocorrerem):
- Muitos 409 → Validação funcionando ✓
- Muitos 400 → Type inválido (comunicar com Flutter dev)
- Muitos 500 → Problema grave (revisar)

---

## 📝 Checklist Final

- [ ] Código feito push
- [ ] Render fez rebuild (5-10 min)
- [ ] Logs mostram "Application startup complete"
- [ ] Teste de registro passou (201 Created)
- [ ] Teste de email duplicado passou (409)
- [ ] Teste de type inválido passou (400)
- [ ] Nenhum erro 500 nos últimos 10 registros

---

## ❌ Se Algo Não Funcionar

### 1. Erro de Import
```
ModuleNotFoundError: No module named 'app.models.user'
```
→ Verificar se todos os arquivos foram commitados

### 2. Erro de Banco
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```
→ Banco não foi inicializado
→ Verificar se `Base.metadata.create_all()` está em main.py

### 3. Erro 500 em /auth/register
→ Ver logs com detalhe:
```
Render → Services → Logs → Last 100 lines
```

### 4. Resetar Banco (ÚLTIMO RECURSO)
```
Render Dashboard:
1. Data → PostgreSQL
2. Delete database
3. Redeploy app
```

---

## 📞 Suporte

Se tiver problemas:
1. Verificar logs do Render
2. Testar localmente: `uvicorn app.main:app --reload`
3. Verificar arquivo `CHANGES_SUMMARY.md` neste repo
