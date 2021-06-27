from django.http.response import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView  # para diminuiçao de codigo
from django.views import View
# Create your views here.
from . import models
from django.contrib import messages
from pprint import pprint
from perfil.models import Perfil


class ListaProdutos(ListView):
    # procura por padrão /produto_list -> quando herdado de listview
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'  # o objeto no template chamará produtos
    paginate_by = 3


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'  # o objeto no template chamará produtos
    slug_url_kwarg = 'slug'


class AdicionarAoCarrinho(View):
    # hendando de view tem que fazer os metodos de get(não tem method) e post- não renderiza nada so redirect
    def get(self, *args, **kwargs):
        # TODO:REMOVER IF ABAIXO
        # if self.request.session.get('carrinho'):
        #     del self.request.session['carrinho']
        #     # apagar se tiver algum carrinho salvo
        #     self.request.session.save()

        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        # checando vid da url
        variacao_id = self.request.GET.get('vid')
        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            # para não tentar adicionar um produto em pagina que não existe
            return redirect(http_referer)
        # return redirect(self.request.META['HTTP_REFERER'])#forma da pagina saber qual a url anterior, OPCAO PARA NÃO USAR AJAX/JAVASCRIPT
        # levanta erro caso o ojeto não exista
        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome
        # variacao_id = variacao.id- ja setado acima
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        if variacao.estoque < 1:
            messages.error(
                self.request,
                'Estoque insuficiente'
            )
            return redirect(http_referer)

        # sessoes  like cockies são unicas para cada user
        if not self.request.session.get('carrinho'):
            # se a chave não existir será criada
            self.request.session['carrinho'] = {}  # DICIONARIO
            self.request.session.save()

        carrinho = self.request.session['carrinho']
        if variacao_id in carrinho:
            # VARIAÇÃO EXISTE NO CARRINHO
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1
            if variacao_estoque < quantidade_carrinho:
                # se quantidade adicionada no carrinho > que produtos em estoque
                messages.warning(
                    self.request,
                    f'Estoque insuficiente de {produto_nome} para esta quantidade'
                )
                quantidade_carrinho = variacao_estoque

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * \
                quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * \
                quantidade_carrinho
        else:
            # VARIACAO NÃO EXISTE NO CARRINHO
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': 1,
                'slug': slug,
                'imagem': imagem,

            }

        self.request.session.save()  # salva a sessão
        # pprint(carrinho)-verificando carrinho atual
        # return HttpResponse(f'{variacao.produto}')
        messages.success(
            self.request,
            'Produtos adicionados ao carrinho'
        )
        return redirect(http_referer)


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        # checando vid da url
        variacao_id = self.request.GET.get('vid')
        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        if variacao_id not in self.request.session['carrinho']:
            return redirect(http_referer)

        carrinho = self.request.session['carrinho'][variacao_id]
        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} removido do carrinho'
        )

        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        return redirect(http_referer)


class Carrinho(View):
    def get(self, *args, **kwargs):
        contexto = {
            'carrinho': self.request.session.get('carrinho', {})
        }
        return render(self.request, 'produto/carrinho.html', contexto)


class ResumoDaCompra(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        perfil=Perfil.objects.filter(usuario=self.request.user).exists()
        if not perfil:
            messages.error(
                self.request,
                'Usuário sem perfil.'
            )
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('produto:lista')
        
        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }
        return render(self.request, 'produto/resumodacompra.html', contexto)
