from django import forms
from django.forms import fields
from django.contrib.auth.models import User
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil  # referencia a qual model
        fields = '__all__'
        exclude = ('usuario',)


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False, widget=forms.PasswordInput(), label='Senha')

    password2 = forms.CharField(
        required=False, widget=forms.PasswordInput(), label='Confirmação Senha')

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)  # para ajudar a verificar se o usuario existe

        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password', 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data  # pega dados zerados
        validation_error_msg = {}

        usuario_data = cleaned.get('username')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')
        email_data = cleaned.get('email')

        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_user_exists = 'Usuario já existe'
        error_msg_email_exists = 'Email já existe'
        error_msg_password_math = 'Senha não conferem'
        error_msg_password_short = 'Senha precisa ter mais de 6 caracters'
        error_msg_required_fild = 'Campo Obrigatorio'
        # print(data)  # verificando os dados pegos no form
        if self.usuario:
            # em analises
            if usuario_db:
                if usuario_data != usuario_db.username:
                    validation_error_msg['username'] = error_msg_user_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msg['email'] = error_msg_email_exists

            if password_data:
                if password_data != password2_data:
                    validation_error_msg['password'] = error_msg_password_math
                    validation_error_msg['password2'] = error_msg_password_math

                if len(password_data) < 6:
                    validation_error_msg['password'] = error_msg_password_short

        else:
            # usuario se não logado
            if usuario_db:
                validation_error_msg['username'] = error_msg_user_exists

            if email_db:
                validation_error_msg['email'] = error_msg_email_exists

            if password_data != password2_data:
                validation_error_msg['password'] = error_msg_password_math
                validation_error_msg['password2'] = error_msg_password_math

            if not password_data:
                validation_error_msg['password'] = error_msg_required_fild

            if not password2_data:
                validation_error_msg['password2'] = error_msg_required_fild

            if len(password_data) < 6:
                validation_error_msg['password'] = error_msg_password_short

        if validation_error_msg:
            raise(forms.ValidationError(validation_error_msg))
