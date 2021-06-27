import pedido
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View

from django.http import HttpResponse, request, response
# Create your views here.
from django.contrib import messages
from produto.models import Variacao
from utils import utils
from .models import Pedido, ItemPedido


class DispatchLoginRequired(View):  # para descobrir para onde a pagina deve ir
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(*args, **kwargs)


class Pagar(DispatchLoginRequired, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        # para inpedir que o usuario acesse pedido que não é o dele
        qs = qs.filter(usuario=self.request.user)
        return qs


class SalvarPedido(View):
    template_name = 'pedido/pagar.html'

    def get(self, *args, **kwargs):
        # metodo somente pra testar os endpoints
        # return HttpResponse('Pagar')
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Faça o login'
            )
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('produto:lista')

        # verificando o id das variações de produto
        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_id = [v for v in carrinho]
        bd_variacoes = list(Variacao.objects.select_related(
            'produto').filter(id__in=carrinho_variacao_id))

        # print(bd_variacoes)
        for variacao in bd_variacoes:
            vid = str(variacao.id)

            estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']

            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                # corrigindo os preços
                carrinho[vid]['preco_quantitativo'] = estoque*preco_unt
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * \
                    preco_unt_promo

                error_msg_estoque = 'Estoque insulficiente pra alguns produtos,quantidade reduzida'

            if error_msg_estoque:
                messages.error(
                    self.request,
                    error_msg_estoque
                )
                self.request.session.save()
                return redirect('produto:carrinho')

        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_totals(carrinho)

        pedido = Pedido(usuario=self.request.user,
                        total=valor_total_carrinho,
                        qtd_total=qtd_total_carrinho,
                        status='C'
                        )
        pedido.save()

        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    image=v['imagem'],
                ) for v in carrinho.values()]
        )
        del self.request.session['carrinho']
        # contexto = {
        #     'qtd_total_carrinho': qtd_total_carrinho,
        #     'valor_total_carrinho':valor_total_carrinho,
        # }
        # return render(self.request, self.template_name)
        return redirect(
            reverse(
                'pedido:pagar',
                kwargs={
                    'pk': pedido.pk
                }
            )
        )
    # =======


class Detalhe(View):
    def get(self, *args, **kwargs):
        # metodo somente pra testar os endpoints
        return HttpResponse('Detalhes do pedido')


class Lista(View):
    def get(self, *args, **kwargs):
        # metodo somente pra testar os endpoints
        return HttpResponse('Lista do pedido')
