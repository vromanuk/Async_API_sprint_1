from functools import wraps

import orjson

from src.db.redis import get_redis


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


def cached(decoder, many: bool = False):
    def decorator(func):
        @wraps(func)
        async def decorated_function(*args, **kwargs):
            cache = get_redis()
            if many:
                cache_key = (
                    f"{kwargs['search_query']}:{kwargs['sort_order'].lower()}:{kwargs['sort'].lower()}:"
                    f"{kwargs['page']}:{kwargs['limit']}"
                )
            else:
                _, entity = kwargs.items()
                entity_title, _ = entity[0].split("_")
                cache_key = f"{entity_title}:{entity[1]}"
            rv = await cache.get_from_cache(cache_key)

            if rv is not None:
                if many:
                    entities = orjson.loads(rv)
                    if not entities:
                        return []
                    return entities
                return decoder.parse_raw(rv)

            rv = await func(*args, **kwargs)
            if many:
                await cache.cache(cache_key, orjson.dumps([entity.dict() for entity in rv]))
            else:
                await cache.cache(cache_key, rv.json())

            return rv

        return decorated_function

    return decorator
