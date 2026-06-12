from datetime import datetime


def search_patterns(search: str) -> list[str]:
    term = search.strip()
    if not term:
        return []

    variants = {term}

    for date_format in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            parsed = datetime.strptime(term, date_format).date()
        except ValueError:
            continue
        variants.add(parsed.isoformat())
        variants.add(parsed.strftime("%d/%m/%Y"))
        variants.add(parsed.strftime("%d-%m-%Y"))

    if "/" in term:
        variants.add(term.replace("/", "-"))
    if "-" in term:
        variants.add(term.replace("-", "/"))
    if term.endswith("%"):
        variants.add(term[:-1].strip())

    return [f"%{variant}%" for variant in variants if variant]
