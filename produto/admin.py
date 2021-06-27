from django.contrib import admin
from django.db import close_old_connections
from . import models
# Register your models here.


class VariacaoInline(admin.TabularInline):
    model = models.Variacao
    extra = 1


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'get_preco_formatado',
                    'get_preco_promocional_formatado']
    inlines = [
        VariacaoInline
    ]


admin.site.register(models.Produto, ProdutoAdmin)
admin.site.register(models.Variacao)
