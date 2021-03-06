from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
# Create your views here.
from django.http import HttpResponse
from . import models
from . import forms
import perfil
from django.contrib.auth.models import User
import copy
from django.contrib.auth import authenticate, login, logout  # para autenticar e logar
from django.contrib import messages


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.perfil = None
        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user
            ).first()  # pegar um perfil determinado

            self.contexto = {
                'userform': forms.UserForm(data=self.request.POST or None, usuario=self.request.user, instance=self.request.user),
                'perfilform': forms.PerfilForm(data=self.request.POST or None, instance=self.perfil)
            }
        else:
            self.contexto = {
                'userform': forms.UserForm(data=self.request.POST or None),
                'perfilform': forms.PerfilForm(data=self.request.POST or None)
            }

        self.userform = self.contexto['userform']
        self.perfilform = self.contexto['perfilform']

        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(
            self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    # criado o criar.html agora para realizar o POST
    # necessario verificar se forms sao validos
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            # print('invalido')
            messages.error(
                self.request,
                'Formulario abaixo com erros, verifique os campo '
            )
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
        # print('valido!!!!')
        # se usuario logado
        if self.request.user.is_authenticated:
            usuario = get_object_or_404(
                User, username=self.request.user.username)  # self.request.user
            usuario.name = username
            if password:
                usuario.set_password(password)  # para manter a criptografia

            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            # cria um perfil
            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()
            else:
                perfil = self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()

        else:
            # se usuario n??o logado
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        if password:
            autentica = authenticate(
                self.request, username=usuario, password=password)
            # para relogar mesmo apos trocar dados da conta de usuario
            if autentica:
                login(self.request, user=usuario)

        # salva session apo alterar conta
        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()

        messages.success(
            self.request,
            'Cadastro criado/atualizado com sucesso.'
        )
        messages.success(
            self.request,
            'Login realizado no sistema.'
        )
        # para n??o reenviar o formulario
        return redirect('produto:carrinho')
        return self.renderizar  # porque 2 returns seguidos ???


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def post(self, *args, **kwargs):
        # return HttpResponse('Login')
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        if not username or not password:
            messages.error(
                self.request,
                'Usu??rio ou senha inv??lidos.'
            )
            return redirect('perfil:criar')
        usuario = authenticate(
            self.request, username=username, password=password)
        if not usuario:
            messages.error(
                self.request,
                'Usu??rio ou senha inv??lidos.'
            )
            return redirect('perfil:criar')

        login(self.request, user=usuario)
        messages.success(
            self.request,
            'Usu??rio logado no sistema.'
        )
        return redirect('produto:carrinho')


class Logout(View):
    def get(self, *args, **kwargs):
        carrinho = copy.deepcopy(self.request.session.get('carrinho'))
        logout(self.request)
        # para salva o carrinho mesmo quando deslogar
        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        return redirect('produto:lista')
