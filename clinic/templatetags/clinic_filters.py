from django import template

register = template.Library()


@register.filter
def star_range(value):
    try:
        return range(int(value))
    except (TypeError, ValueError):
        return range(0)


@register.filter
def empty_star_range(value):
    try:
        return range(10 - int(value))
    except (TypeError, ValueError):
        return range(10)


@register.filter
def sub(value, arg):
    try:
        return int(value) - int(arg)
    except (TypeError, ValueError):
        return value


@register.filter
def format_som(value):
    """
    Format an integer as so'm currency with space separators.
    Example: 5000000 -> "5 000 000"
             200000  -> "200 000"
    """
    try:
        num = int(value)
    except (TypeError, ValueError):
        return value
    if num < 0:
        return '-' + format_som(-num)
    result = '{:,}'.format(num).replace(',', ' ')
    return result


@register.filter
def get_item(dictionary, key):
    """Get item from dict by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def visit_service_names(visit):
    """Return comma-separated service names for a visit (from VisitService M2M)."""
    try:
        names = [vs.service.name for vs in visit.visit_services.all() if vs.service]
        if names:
            return ', '.join(names)
    except Exception:
        pass
    # Fallback to old single service FK
    if hasattr(visit, 'service') and visit.service:
        return visit.service.name
    return '—'
