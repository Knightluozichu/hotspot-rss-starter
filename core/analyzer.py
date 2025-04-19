def filter_by_keywords(items, keywords):
    result = []
    for item in items:
        if any(k.lower() in item['title'].lower() for k in keywords):
            result.append(item)
    return result
