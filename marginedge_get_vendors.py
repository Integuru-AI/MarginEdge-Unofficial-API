from curl_cffi import requests


def run(headers, user_input):
    """List vendors for the current restaurant unit."""

    try:
        response = _call_api(headers)
    except Exception as e:
        return {'status_code': 500, 'body': {'error': str(e)}}

    # Check for auth failure
    if response.status_code == 401:
        return {'status_code': 401, 'body': {'error': 'Authentication expired'}}

    if response.status_code == 403:
        return {'status_code': 401, 'body': {'error': 'Session expired or access denied'}}

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

    # Extract relevant fields for each vendor
    vendors = []
    for vendor in data:
        vendors.append({
            'id': vendor.get('id'),
            'name': vendor.get('name'),
            'account_number': vendor.get('accountNumber'),
            'preferred_order_method': vendor.get('preferredOrderMethod'),
            'preferred_order_address': vendor.get('preferredOrderAddress'),
            'phone': vendor.get('vendorPhone', {}).get('phone') if vendor.get('vendorPhone') else None,
            'online_ordering': vendor.get('onlineOrdering'),
            'exclude_from_accounting': vendor.get('excludeFromAccounting'),
            'payment_transmission_type': vendor.get('paymentTransmissionType'),
            'vendor_credit_mode': vendor.get('vendorCreditMode'),
            'bill_pay_configured': vendor.get('billPayConfigured'),
            'invoices_this_period': vendor.get('invoicesThisPeriod'),
            'purchases_this_period': vendor.get('purchasesThisPeriod'),
            'retired_date': vendor.get('retiredDate'),
        })

    return {
        'status_code': 200,
        'body': {
            'vendors': vendors,
            'count': len(vendors)
        }
    }


# === PRIVATE ===

def _call_api(headers):
    """Fetch vendors from the API."""
    base_url = BASE_URL

    response = requests.get(
        f"{base_url}/api/vendors",
        headers={
            **headers,
            "Accept": "application/json",
        },
        impersonate="chrome131",
        timeout=30,
    )
    return response
