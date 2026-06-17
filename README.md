# MarginEdge Unofficial API

Unofficial Python integrations for MarginEdge.

## Integrations

- `marginedge_get_purchase_report.py` - `get_purchase_report`.
- `marginedge_get_orders.py` - `get_orders`.
- `marginedge_get_order_detail.py` - `get_order_detail`.
- `marginedge_get_vendors.py` - `get_vendors`.

## Usage

Each file exposes a `run(input, context)` entrypoint. The runtime is expected to provide:

- `input`: integration-specific request fields.
- `context["headers"]`: authenticated request headers when required.
- `context["base_url"]`: the platform base URL when overriding the default.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Info

This unofficial API is built by [Integuru.ai](https://integuru.ai/).

For custom requests or hosted authentication, contact richard@taiki.online.

See the [complete list of APIs by Integuru](https://github.com/Integuru-AI/APIs-by-Integuru).
