from curl_cffi import requests


def run(headers, user_input):
    """Get the purchase report for the current restaurant unit within a date range."""

    start_date = user_input.get("start_date")
    end_date = user_input.get("end_date")

    if not start_date:
        return {'status_code': 400, 'body': {'error': 'start_date is required (YYYY-MM-DD)'}}
    if not end_date:
        return {'status_code': 400, 'body': {'error': 'end_date is required (YYYY-MM-DD)'}}

    try:
        response = _call_api(headers, start_date, end_date)
    except Exception as e:
        return {'status_code': 500, 'body': {'error': str(e)}}

    # Check for auth failure
    if response.status_code == 401:
        return {'status_code': 401, 'body': {'error': 'Authentication expired'}}

    if response.status_code == 403:
        return {'status_code': 401, 'body': {'error': 'Session expired or access denied'}}

    if response.status_code == 400:
        return {'status_code': 400, 'body': {'error': 'Invalid date range. Use YYYY-MM-DD format.'}}

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

    # Extract purchase report rows
    rows = []
    for row in data.get('purchaseReportRows', []):
        product_unit = row.get('productUnit', {}) or {}
        rows.append({
            'product_id': row.get('productId'),
            'name': row.get('name'),
            'category': row.get('category'),
            'category_type': row.get('categoryType'),
            'purchased_units': row.get('purchasedUnits'),
            'purchased_value': row.get('purchasedValue'),
            'unit': product_unit.get('unit'),
            'count_by': row.get('countBy'),
        })

    # Extract category info
    category_info = {}
    for key, val in data.get('companyConceptProductCategoryInfoMap', {}).items():
        category_info[key] = {
            'category': val.get('category'),
            'custom_category_type_name': val.get('customCategoryTypeName'),
            'custom_category_type_code': val.get('customCategoryTypeCodeName'),
        }

    return {
        'status_code': 200,
        'body': {
            'rows': rows,
            'count': len(rows),
            'category_info': category_info,
        }
    }


# === PRIVATE ===

def _call_api(headers, start_date, end_date):
    """Fetch purchase report from the API."""
    base_url = BASE_URL

    response = requests.get(
        f"{base_url}/api/orders/purchaseReport",
        params={
            "startDate": start_date,
            "endDate": end_date,
        },
        headers={
            **headers,
            "Accept": "application/json",
        },
        impersonate="chrome131",
        timeout=30,
    )
    return response
