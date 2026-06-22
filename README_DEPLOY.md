# 🚀 Deploy no Easypanel (VPS)

## Pré-requisitos
- VPS com Easypanel instalado
- Repositório no GitHub com o código do projeto

---

## 1. Crie os serviços no Easypanel

### 1.1 — Banco de dados PostgreSQL
1. No Easypanel, crie um novo serviço do tipo **PostgreSQL**
2. Anote o nome do serviço (ex: `presidente-db`)
3. Defina uma senha forte

### 1.2 — Aplicação
1. Crie um novo serviço do tipo **App**
2. Conecte ao repositório GitHub
3. Selecione o branch `main`
4. Build type: **Dockerfile**

---

## 2. Configure as variáveis de ambiente

No painel do serviço App, adicione as seguintes variáveis:

| Variável | Descrição | Exemplo |
|---|---|---|
| `DATABASE_URL` | URL de conexão ao Postgres | `postgresql://wpcrm_user:SENHA@presidente-db:5432/presidente` |
| `JWT_SECRET` | Chave secreta JWT (gerada aleatoriamente) | `abc123xyz...` |
| `WAHA_API_URL` | URL da sua instância WAHA | `https://waha.meusite.com/` |
| `WAHA_API_KEY` | Chave de API da WAHA | `abc123...` |
| `PORT` | Porta da aplicação | `9010` |
| `ADMIN_EMAIL` | Email do admin padrão | `admin@empresa.com` |
| `ADMIN_PASSWORD` | Senha do admin padrão | `SenhaForte123!` |

> ⚠️ **IMPORTANTE**: O host do `DATABASE_URL` é o **nome do serviço** do banco no Easypanel, não `localhost`.

---

## 3. Configure o domínio e porta

- Porta interna: **9010**
- Configure o domínio no Easypanel apontando para a porta 9010

---

## 4. Volume persistente

Configure um volume no serviço da aplicação:
- **Container path**: `/app/data`
- Este diretório armazena mídias (imagens, áudios, etc.) enviadas pelo WhatsApp

---

## 5. Configure o webhook no WAHA

Após o deploy, configure o webhook no WAHA para apontar para:
```
https://SEU_DOMINIO/api/webhooks/waha
```

---

## Desenvolvimento local

Para testar localmente (com SQLite, sem precisar de Postgres):

```bash
.\testar_localmente.bat
```

O servidor sobe em: `http://localhost:3008`
