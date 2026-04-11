# 📚 Exemplo de Uso do /auth/register

## Respostas de Exemplo

### ✅ Sucesso (201 Created)

**Request:**
```json
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "João Silva Santos",
  "email": "joao.silva@email.com",
  "password": "MinhaSenha123!",
  "type": "client",
  "phone": "11999887766",
  "city": "São Paulo"
}
```

**Response:**
```json
HTTP/1.1 201 Created
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZDYwNWVhYy03ZDk0LTQ4MTItYjBjNC1lODM4YTkwNDlkZjYiLCJleHAiOjE2NDY1OTUyMzksInR5cGUiOiJhY2Nlc3MifQ.7jN8sY9kZ0pX1aQ2bR3cS4dT5eU6fV7wX8yZ9aB0cD1",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZDYwNWVhYy03ZDk0LTQ4MTItYjBjNC1lODM4YTkwNDlkZjYiLCJleHAiOjE2NDkxODcyMzksInR5cGUiOiJyZWZyZXNoIn0.abc123xyz789",
  "token_type": "bearer",
  "user": {
    "id": "5d605eac-7d94-4812-b0c4-e838a9049df6",
    "name": "João Silva Santos",
    "email": "joao.silva@email.com",
    "phone": "11999887766",
    "type": "client",
    "city": "São Paulo",
    "profile_image": null,
    "is_verified": false,
    "is_blocked": false,
    "created_at": "2026-04-11T14:30:39.123456+00:00"
  }
}
```

---

### ❌ Email Já Cadastrado (409 Conflict)

**Request:**
```json
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "Outro Nome",
  "email": "joao.silva@email.com",
  "password": "OutraSenha123!",
  "type": "client",
  "phone": "11988776655",
  "city": "Rio de Janeiro"
}
```

**Response:**
```json
HTTP/1.1 409 Conflict
Content-Type: application/json

{
  "detail": "E-mail já cadastrado"
}
```

**Backend Log:**
```
2026-04-11 14:32:15 WARNING - Email already registered: joao.silva@email.com
```

---

### ❌ Tipo Usuário Inválido (400 Bad Request)

**Request:**
```json
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "Maria Silva",
  "email": "maria@email.com",
  "password": "SenhaForte123!",
  "type": "superuser",
  "phone": "11988776655",
  "city": "Brasília"
}
```

**Response:**
```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "detail": "Tipo de usuário inválido. Use: client, professional, admin"
}
```

**Backend Log:**
```
2026-04-11 14:33:22 WARNING - Invalid user type: superuser
```

---

### ❌ Senha Muito Curta (422 Unprocessable Entity)

**Request:**
```json
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "Carlos",
  "email": "carlos@email.com",
  "password": "123",
  "type": "client",
  "phone": "11988776655",
  "city": "Salvador"
}
```

**Response:**
```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Value error, Senha deve ter no mínimo 8 caracteres"
    }
  ]
}
```

---

### ❌ Campo Obrigatório Missing (422 Unprocessable Entity)

**Request:**
```json
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "Pedro",
  "email": "pedro@email.com",
  "password": "SenhaForte123!"
}
```

**Response:**
```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "type"],
      "msg": "Field required"
    },
    {
      "type": "missing",
      "loc": ["body", "phone"],
      "msg": "Field required"
    },
    {
      "type": "missing",
      "loc": ["body", "city"],
      "msg": "Field required"
    }
  ]
}
```

---

### ❌ Email Inválido (422 Unprocessable Entity)

**Request:**
```json
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "Ana",
  "email": "email-invalido",
  "password": "SenhaForte123!",
  "type": "client",
  "phone": "11988776655",
  "city": "Porto Alegre"
}
```

**Response:**
```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address: email-invalido (missing @ or more than one @)"
    }
  ]
}
```

---

### ❌ Nome Vazio (422 Unprocessable Entity)

**Request:**
```json
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "",
  "email": "teste@email.com",
  "password": "SenhaForte123!",
  "type": "client",
  "phone": "11988776655",
  "city": "Curitiba"
}
```

**Response:**
```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "name"],
      "msg": "Value error, Nome não pode estar vazio"
    }
  ]
}
```

---

## 🔐 Usando os Tokens

### Access Token (na Authorization Header)

```bash
curl -X GET https://seu-app.render.com/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZDYwNWVhYy03ZDk0LTQ4MTItYjBjNC1lODM4YTkwNDlkZjYiLCJleHAiOjE2NDY1OTUyMzksInR5cGUiOiJhY2Nlc3MifQ.7jN8sY9kZ0pX1aQ2bR3cS4dT5eU6fV7wX8yZ9aB0cD1"
```

### Refresh Token (para renovar tokens expirados)

```bash
curl -X POST https://seu-app.render.com/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZDYwNWVhYy03ZDk0LTQ4MTItYjBjNC1lODM4YTkwNDlkZjYiLCJleHAiOjE2NDkxODcyMzksInR5cGUiOiJyZWZyZXNoIn0.abc123xyz789"
  }'
```

---

## 📱 Exemplo em Flutter

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> registerUser() async {
  final response = await http.post(
    Uri.parse('https://seu-app.render.com/auth/register'),
    headers: {
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'name': 'João Silva',
      'email': 'joao@example.com',
      'password': 'SenhaForte123!',
      'type': 'client',
      'phone': '11999887766',
      'city': 'São Paulo',
    }),
  );

  if (response.statusCode == 201) {
    final data = jsonDecode(response.body);
    final accessToken = data['access_token'];
    final user = data['user'];
    
    print('✅ Usuário registrado: ${user['name']}');
    print('🎫 Access Token: $accessToken');
  } else if (response.statusCode == 409) {
    print('❌ E-mail já cadastrado');
  } else if (response.statusCode == 400) {
    print('❌ Tipo inválido');
  } else {
    print('❌ Erro: ${response.statusCode}');
  }
}
```

---

## 🎯 Summary

| Cenário | Status | Código |
|---------|--------|--------|
| Registro sucesso | ✅ | 201 |
| Email duplicado | ❌ | 409 |
| Type inválido | ❌ | 400 |
| Senha curta | ❌ | 422 |
| Campo missing | ❌ | 422 |
| Email inválido | ❌ | 422 |

**Nenhum 500!** ✅
