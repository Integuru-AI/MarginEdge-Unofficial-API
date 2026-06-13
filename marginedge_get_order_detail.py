from curl_cffi import requests


def run(headers, user_input):
    """Get full details for a specific order by ID."""

    order_id = user_input.get("order_id")
    if not order_id:
        return {'status_code': 400, 'body': {'error': 'order_id is required'}}

    try:
        response = _call_api(headers, order_id)
    except Exception as e:
        return {'status_code': 500, 'body': {'error': str(e)}}

    # Check for auth failure
    if response.status_code == 401:
        return {'status_code': 401, 'body': {'error': 'Authentication expired'}}

    if response.status_code == 403:
        return {'status_code': 401, 'body': {'error': 'Session expired or access denied'}}

    if response.status_code == 404:
        return {'status_code': 404, 'body': {'error': f'Order {order_id} not found'}}

    if response.status_code != 200:
        return {
            'status_code': response.status_code,
            'body': {'error': f'API returned status {response.status_code}'}
        }

    # Check for login page redirect (session expired)
    content_type = response.headers.get('content-type', '')
    if 'text/html' in content_type:
        return {'status_code': 401, 'body': {'error': 'Session expired - redirected to login'}}

    data = response.json()

    # Build line items
    line_items = []
    for item in data.get('lineItems', []):
        vp = item.get('vendorProduct', {}) or {}
        line_items.append({
            'id': item.get('id'),
            'quantity': item.get('quantity'),
            'unit_price': item.get('unitPrice'),
            'line_price': item.get('linePrice'),
            'product_name': vp.get('name'),
            'vendor_product_id': vp.get('id'),
        })

    # Build result
    vendor = data.get('vendor', {}) or {}
    result = {
        'id': data.get('id'),
        'order_date': data.get('orderDate'),
        'invoice_date': data.get('invoiceDate'),
        'invoice_number': data.get('invoiceNum'),
        'status': data.get('status'),
        'origin': data.get('origin'),
        'total': data.get('total'),
        'vendor': {
            'id': vendor.get('id'),
            'name': vendor.get('name'),
        },
        'line_items': line_items,
        'taxes': data.get('taxes'),
        'tax_credits': data.get('taxCredits'),
        'delivery': data.get('delivery'),
        'other': data.get('other'),
        'credit': data.get('credit'),
        'payment_due_date': data.get('paymentDueDate'),
        'closed_date': data.get('closedDate'),
        'sent_date': data.get('sentDate'),
        'attachments_count': len(data.get('attachments', []) or []),
    }

    return {
        'status_code': 200,
        'body': result
    }


# === PRIVATE ===

def _call_api(headers, order_id):
    """Fetch order detail from the API."""
    base_url = BASE_URL

    response = requests.get(
        f"{base_url}/api/orders/{order_id}",
        headers={
            **headers,
            "Accept": "application/json",
        },
        impersonate="chrome131",
        timeout=30,
    )
    return response
