def int_array_decompress(s: str):
    """ reverts compressIntArray from juntagrico.js
    E.g. '1-3_15_8' -> [1,2,3,15,18]
    """
    if not s:
        return []
    out = []
    last = ''
    for token in s.split('_'):
        if '-' not in token:
            token = last[:-len(token)] + token
            out.append(int(token))
            last = token
        else:
            start_str, end_str = token.split('-', 1)
            start_str = last[:-len(start_str)] + start_str
            last = start_str
            end_str = last[:-len(end_str)] + end_str
            last = end_str
            for i in range(int(start_str), int(end_str) + 1):
                out.append(i)
    return out
