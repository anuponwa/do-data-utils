import re


def search_regexp(pattern, string, group=0):
    search = re.search(pattern, string)
    if search:
        return search.group(group)

    return None
