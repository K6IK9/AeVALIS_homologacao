from django import template
from rolepermissions.checkers import has_role as check_role

register = template.Library()


@register.filter
def has_role(user, role):
    """
    Template filter para verificar se o usuário tem uma role específica
    """
    return check_role(user, role)
