from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError  # levantar excessão
import re  # para expressoes regulares

from utils.validacpf import valida_cpf

# Create your models here.


class Perfil(models.Model):
    # o mais recomendado é criar separado e não aqui
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    idade = models.PositiveIntegerField()
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11, help_text='apenas numeros')
    endereco = models.CharField(max_length=50)
    numero = models.CharField(max_length=5)
    complemento = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=8)
    cidade = models.CharField(max_length=30)
    estado = models.CharField(
        max_length=2,
        default='SP',
        choices=(
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),

        )
    )

    def __str__(self):
        # quando chamar perfil será exibido first e last_name
        return f'{self.usuario}'  # {self.usuario.last_name}'

    # classe clean para validação de campos a nivel de models
    def clean(self):
        error_messages = {}
        # error_messages[]=''
        if not valida_cpf(self.cpf):
            error_messages['cpf'] = 'CPF inválido'

        # se diferente de 0 a 9,levanta excessao
        if re.search(r'[^0-9]', self.cep) or len(self.cep) < 8:
            error_messages['cep'] = 'CEP Invalido'

        if error_messages:
            raise ValidationError(error_messages)

        print(self.idade)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
