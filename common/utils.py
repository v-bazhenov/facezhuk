import re


def to_snake(value):
    value = re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()
    return value


def prepare_object_for_postgresql(message: dict) -> dict:
    res = {}
    for k, v in message.items():
        k = to_snake(k)
        res.update({k: v})
    res['mongo_id'] = str(res['_id'])
    res.pop('_id')
    res.pop('is_backup_created')
    return res
