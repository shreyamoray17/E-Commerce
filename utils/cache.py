from django.core.cache import cache


def get_product_list_cache_key(page=1):
    return f'product_list_page_{page}'


def get_product_detail_cache_key(product_id):
    return f'product_detail_{product_id}'


def clear_product_cache(product_id=None):
    # Clear product detail cache
    if product_id:
        cache_key = get_product_detail_cache_key(product_id)
        cache.delete(cache_key)
    
    # Clear all product list caches (pages 1-10)
    for page in range(1, 11):
        cache_key = get_product_list_cache_key(page)
        cache.delete(cache_key)


def cache_product_list(page, data, timeout=900):
    cache_key = get_product_list_cache_key(page)
    cache.set(cache_key, data, timeout)


def cache_product_detail(product_id, data, timeout=1800):
    cache_key = get_product_detail_cache_key(product_id)
    cache.set(cache_key, data, timeout)
