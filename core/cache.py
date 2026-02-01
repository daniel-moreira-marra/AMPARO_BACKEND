from django.core.cache import cache
from django.conf import settings
import hashlib
import json

FEED_VERSION_CACHE_KEY = "feed_global_version"

def get_feed_version():
    """
    Retorna a versão atual do feed. Se não existir, cria uma inicial.
    Utilizado para invalidação de cache atômica.
    """
    version = cache.get(FEED_VERSION_CACHE_KEY)
    if version is None:
        version = 1
        cache.set(FEED_VERSION_CACHE_KEY, version, timeout=None)
    return version

def bump_feed_version():
    """
    Incrementa a versão do feed, invalidando efetivamente todos os caches de feed.
    """
    try:
        return cache.incr(FEED_VERSION_CACHE_KEY)
    except ValueError:
        # Se a chave não existir (ex: expirou ou cache limpo)
        cache.set(FEED_VERSION_CACHE_KEY, 1, timeout=None)
        return 1

def generate_feed_cache_key(user, cursor=None, extra_params=None):
    """
    Gera uma chave de cache determinística para o feed.
    Inclui: user_id (ou anon), versão do feed, cursor e parâmetros extras.
    """
    user_id = user.id if user and user.is_authenticated else "anon"
    version = get_feed_version()
    
    # Normalizar parâmetros extras para garantir determinismo
    params_str = ""
    if extra_params:
        params_str = json.dumps(extra_params, sort_keys=True)
    
    # Criar uma string base para o hash
    raw_key = f"feed:u{user_id}:v{version}:c{cursor or 'initial'}:{params_str}"
    
    # Usar hash para evitar chaves muito longas ou caracteres inválidos no backend de cache
    key_hash = hashlib.md5(raw_key.encode()).hexdigest()
    
    # Prefixo para facilitar debug e limpeza manual se necessário
    return f"feed_cache:{key_hash}"
