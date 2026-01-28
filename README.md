# Sistema de automação Hotmart + WhatsApp (modelo)

Este projeto fornece um esqueleto funcional para automatizar mensagens diárias via WhatsApp (Cloud API) com base na data de compra recebida pela Hotmart. O foco é disponibilizar endpoints, banco local e um agendador diário para enviar mensagens em até 35 dias.

## O que este projeto entrega

- Webhooks para compra e reembolso da Hotmart.
- Registro de clientes ativos/refundados.
- Templates de mensagens por dia (D0 a D34).
- Agendador diário (09:00 UTC) que envia mensagens automaticamente.
- Logs de envio para auditoria.
- Endpoints administrativos simples para atualizar templates e disparo manual.

## Tecnologias

- FastAPI
- APScheduler
- SQLite

## Como rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints principais

- `POST /webhooks/hotmart/purchase`
- `POST /webhooks/hotmart/refund`
- `POST /admin/templates`
- `POST /admin/messages/manual`
- `GET /health`

## Próximos passos sugeridos

- Integrar WhatsApp Cloud API (autenticação + envio real).
- Implementar opt-out automático e tratamento de falhas.
- Adicionar painel administrativo com autenticação.
- Enviar mensagens em horários configuráveis por cliente.
- Exportar relatórios e logs para CSV.
