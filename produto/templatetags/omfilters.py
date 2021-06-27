from django.template import Library
from utils import utils

register = Library()


@register.filter
def formata_preco(val):
    # return f'R$ {val:.2f}'.replace('.', ',')-> mudada pra ser reutilizada
    return utils.formata_preco(val)


@register.filter
def cart_total_qtd(carrinho):
    return utils.cart_total_qtd(carrinho)


@register.filter
def cart_totals(carrinho):
    return utils.cart_totals(carrinho)
