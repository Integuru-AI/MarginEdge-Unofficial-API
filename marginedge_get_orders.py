from curl_cffi import requests


def run(headers, user_input):
    """Retrieve all orders from MarginEdge with optional filters."""
    # Extract optional filters
    status = user_input.get("status", "ALL")
    vendor_id = user_input.get("vendor_id")
    start_date = user_input.get("start_date")
    end_date = user_input.get("end_date")

    # Build query parameters
    params = {
        "status": status,
        "inbound": "false"
    }

    if vendor_id:
        params["vendorId"] = vendor_id
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    try:
        data = _call_api(params, headers)
    except AuthError as e:
        return {'status_code': 401, 'body': {'error': str(e)}}
    except APIError as e:
        return {'status_code': e.status_code, 'body': {'error': str(e)}}
    except Exception as e:
        return {'status_code': 500, 'body': {'error': f'Failed to parse response: {str(e)}'}}

    # Transform orders to cleaner format
    orders = []
    for order in data:
        # Handle anyInvoiceDate which can be array [year, month, day] or null
        invoice_date = None
        if order.get("anyInvoiceDate"):
            date_parts = order["anyInvoiceDate"]
            if isinstance(date_parts, list) and len(date_parts) == 3:
                invoice_date = f"{date_parts[0]}-{date_parts[1]:02d}-{date_parts[2]:02d}"

        orders.append({
            "id": order.get("id"),
            "order_date": order.get("orderDate"),
            "vendor_name": order.get("vendorName"),
            "vendor_id": order.get("vendorId"),
            "invoice_number": order.get("anyInvoiceNum") or order.get("invoiceNum"),
            "invoice_date": invoice_date or order.get("invoiceDate"),
            "status": order.get("status"),
            "total": order.get("total") or order.get("initialReviewTotal"),
            "payment_account": order.get("paymentAccount"),
            "created_by": order.get("createdBy"),
            "origin": order.get("origin"),
            "payment_state": order.get("invoicePaymentState"),
            "accounting_sync_status": order.get("accountingSyncStatus")
        })

    return {
        'status_code': 200,
        'body': {
            'total_count': len(orders),
            'orders': orders
        }
    }


# === PRIVATE ===

class AuthError(Exception):
    """Authentication error."""
    pass


class APIError(Exception):
    """API error with status code."""
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


def _call_api(params, headers):
    """Make API request to fetch orders."""
    base_url = BASE_URL

    response = requests.get(
        f"{base_url}/api/orders",
        params=params,
        headers={
            **headers,
            "Accept": "application/json, text/plain, */*",
            "x-me-timezone": "America/Denver"
        },
        impersonate="chrome131",
        timeout=30
    )

    # Check for auth failure
    if response.status_code == 401:
        raise AuthError('Authentication failed')

    # Check for redirect to login page (session expired)
    if response.status_code in (301, 302, 303, 307, 308):
        raise AuthError('Session expired - redirected to login')

    # Check if response is HTML (login page)
    content_type = response.headers.get('content-type', '')
    if 'text/html' in content_type:
        raise AuthError('Session expired - received login page')

    if response.status_code != 200:
        raise APIError(f'API error: {response.text}', response.status_code)

    return response.json()
