# Automação WhatsApp + Hotmart

Protótipo inspirado no fluxo descrito para integrar Hotmart e WhatsApp Business Cloud API.
Ele registra compras, dispara mensagens diárias por 35 dias e mantém logs para o painel administrativo.

## Funcionalidades cobertas

- Webhook de compra/reembolso (Hotmart).
- Catálogo de mensagens diárias com 35 dias.
- Disparo diário manual via endpoint (`/messages/dispatch`).
- Painel administrativo simples (`/admin`).
- Logs de envio e eventos.

## Executando localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse: `http://localhost:8000/admin`

## Exemplos de uso

### Registrar compra

```bash
curl -X POST http://localhost:8000/webhooks/hotmart \
  -H 'Content-Type: application/json' \
  -d '{"event":"purchase","customer":{"name":"Ana","phone":"551199999999"},"purchase_date":"2024-01-27"}'
```

### Registrar reembolso

```bash
curl -X POST http://localhost:8000/webhooks/hotmart \
  -H 'Content-Type: application/json' \
  -d '{"event":"refund","customer_id":1}'
```

### Disparar mensagens do dia

```bash
curl -X POST http://localhost:8000/messages/dispatch
```
