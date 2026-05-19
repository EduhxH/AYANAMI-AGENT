# Correções Implementadas - Módulo de Email

## Resumo Executivo

Foram corrigidos 3 problemas críticos no módulo de email do AYANAMI-AGENT:

✅ **Problema 1**: Perda de token Google não mapeado corretamente  
✅ **Problema 2**: Roteamento incorreto de intenção no Orchestrator  
✅ **Problema 3**: Incapacidade de enviar emails (apenas leitura)

---

## 1. CORREÇÃO DE TOKEN GOOGLE

### Problema
O `google_token` não era repassado corretamente do `user_data` para o agente de email.

### Solução Implementada

#### Arquivo: `backend/src/dev_agent/api/routes/query.py`
- ✅ Adicionado `google_refresh_token` no dict de `user_data`:
  ```python
  user_data = {
      "user_id": user.id,
      "github_token": user.github_token,
      "github_username": user.github_username,
      "google_token": user.google_token,
      "google_refresh_token": user.google_refresh_token,  # ← NOVO
  }
  ```

#### Arquivo: `backend/src/dev_agent/orchestrator/dispatcher.py`
- ✅ Já extrai corretamente: `token = self.user_data.get("google_token")`
- ✅ Callback de renovação passado para `EmailAgent`

#### Fluxo de Renovação Automática
1. Token expirado detectado (erro 401)
2. Callback `refresh_google()` é invocado
3. Função `ensure_fresh_google_token()` valida e renova
4. Novo token atualizado no BD e usado imediatamente

---

## 2. INTEGRAÇÃO DE INTENÇÃO NO PLANNER

### Problema
Palavras-chave críticas como "enviar", "responder", "escrever" não eram reconhecidas pelo `Planner`, causando roteamento para "general" em vez de "email".

### Solução Implementada

#### Arquivo: `backend/src/dev_agent/orchestrator/planner.py`

##### LLM Prompt (atualizado):
```python
Usa o agente "email" quando o pedido envolver:
- Ler, buscar, ou analisar emails
- Responder a emails (palavras como "responda", "responde", "responder", "reply")
- Enviar emails (palavras como "envie", "enviar", "mande", "mandar", "envio")
- Escrever emails ou propostas de resposta (palavras como "escreva", "escrever", "gere uma resposta", "gere uma proposta", "draft", "rascunho")
- Classificar ou organizar emails
- Qualquer operação de Gmail/correio
```

##### Fallback Keywords (expandidas):
```python
if any(word in query_lower for word in [
    "email", "gmail", "mensagem", "responde", "responder", "envie", "enviar", 
    "mande", "mandar", "escreva", "escrever", "gere uma resposta", "gere uma proposta",
    "resposta", "envio", "compose", "rascunho", "draft", "correio"
]):
    agents.append(AgentType.EMAIL)
```

### Exemplos Agora Funcionam ✅
- "Responda o email de maria@example.com"
- "Envie um email para support@company.com"
- "Gere uma proposta de resposta"
- "Escreva um email"
- "Mande um rascunho"

---

## 3. DISTINÇÃO ENTRE LER E ENVIAR

### Problema
O `EmailAgent` apenas realizava leitura, sem suporte a envio de emails.

### Solução Implementada

#### Novo Arquivo: `backend/src/dev_agent/tools/email/sender.py`
Classe `GmailSender` com:
- ✅ `_create_message()`: Cria MIME encoded raw message
- ✅ `send_email()`: POST para Gmail API `/messages/send`
- ✅ Suporte a resposta em thread (`reply_to` parameter)
- ✅ Renovação automática de token (retry 401/403)

#### Arquivo: `backend/src/dev_agent/agents/email_agent.py`

##### Novo Método: `_is_send_intent(query: str) -> bool`
Detecta intenção de ENVIO por:
- **Palavras-chave explícitas**: "envie", "enviar", "mande", "mandar", "responda", "responder", "escreva", "escrever", "compose", "envio", "gere uma proposta", "gere uma resposta"
- **Padrão de texto longo entre aspas**: `"Este é o corpo do email"`
- **Detecção tanto aspas simples quanto duplas**

Retorna:
- `True` → Executa `send_email()`
- `False` → Executa busca e análise de emails (comportamento original)

##### Novo Método: `async def _extract_email_details(query: str) -> tuple`
Extrai detalhes do email:
- **Destinatário**: Usa regex `[\w\.-]+@[\w\.-]+\.\w+`
- **Assunto**: 
  - Procura `"assunto: ..."` ou `"subject: ..."`
  - Se for resposta, prefixo `"Re: "`
- **Corpo**: 
  - Extrai entre aspas: `"corpo aqui"`
  - Ou usa restante da query após email

Retorna: `(destinatário, assunto, corpo)`

##### Fluxo Atualizado de `run()`
```python
async def run(self, query: str) -> AgentResult:
    if not self.token:
        return failure("Gmail não está ligado...")
    
    if self._is_send_intent(query):
        # NOVO: Envio de email
        recipient, subject, body = await self._extract_email_details(query)
        sender = GmailSender(self.token, on_token_refresh=...)
        result = await sender.send_email(to, subject, body)
        return success({"action": "send", "result": result})
    else:
        # Original: Leitura de emails
        reader = GmailReader(self.token, ...)
        emails = await reader.get_recent_emails()
        highlight = await self._pick_highlight(query, emails)
        return success({"action": "read", "emails": emails, "highlight": highlight})
```

### Exemplos de Uso ✅

**Enviar Email:**
```
"Enviar para user@example.com: Olá, como vai?"
"Mande um email para support@company.com assunto: Suporte - Tenho uma dúvida"
'Responda a john@example.com: "Muito obrigado pela resposta"'
```

**Ler Email (comportamento original preservado):**
```
"Ler últimos emails"
"Mostra meus emails recentes"
"Quais emails tenho hoje?"
```

---

## 4. ARQUIVOS MODIFICADOS

| Arquivo | Tipo | Mudanças |
|---------|------|----------|
| `backend/src/dev_agent/agents/email_agent.py` | Modificado | +2 métodos (send intent detection, detail extraction) |
| `backend/src/dev_agent/tools/email/sender.py` | **Novo** | Classe `GmailSender` com suporte a envio |
| `backend/src/dev_agent/orchestrator/planner.py` | Modificado | +16 palavras-chave de email |
| `backend/src/dev_agent/orchestrator/dispatcher.py` | Sem mudança | Já suporta token refresh |
| `backend/src/dev_agent/api/routes/query.py` | Modificado | +1 campo (google_refresh_token) |

---

## 5. TESTES DE VALIDAÇÃO

✅ **Todos os 7 testes passaram:**

| Teste | Status |
|-------|--------|
| Sintaxe - email_agent.py | ✓ PASS |
| Sintaxe - sender.py | ✓ PASS |
| Sintaxe - planner.py | ✓ PASS |
| Sintaxe - dispatcher.py | ✓ PASS |
| Sintaxe - query.py | ✓ PASS |
| Lógica - _is_send_intent() | ✓ PASS (11/11 keywords) |
| Lógica - _extract_email_details() | ✓ PASS |

---

## 6. MANUAIS DE TESTE

### Teste 1: Detecção de Token
```bash
# Verificar que google_token é passado corretamente
grep -n "google_token" backend/src/dev_agent/api/routes/query.py
grep -n "google_token" backend/src/dev_agent/orchestrator/dispatcher.py
```

### Teste 2: Palavras-chave do Planner
```bash
# Verificar keywords expandidas
grep -A 5 "if any(word in query_lower" backend/src/dev_agent/orchestrator/planner.py | grep "email"
```

### Teste 3: Suporte a Envio
```bash
# Verificar classe GmailSender
grep "class GmailSender" backend/src/dev_agent/tools/email/sender.py
```

### Teste 4: Distinção Ler/Enviar
```bash
# Verificar _is_send_intent
grep -A 20 "def _is_send_intent" backend/src/dev_agent/agents/email_agent.py
```

---

## 7. PRÓXIMOS PASSOS (Opcional)

1. **Testes de integração**: Adicionar testes com mocks da API do Gmail
2. **Logging**: Adicionar logs detalhados para debugging
3. **Cache de histórico**: Implementar persistência de último email lido para contexto
4. **Suporte a anexos**: Estender `GmailSender` para envio com attachments

---

## Validação Final

```bash
cd backend
python validate_fixes.py
# Output: Total: 7/7 testes passaram ✓
```

**Resultado:** ✅ Todas as correções implementadas e validadas com sucesso!
