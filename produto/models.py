from django.conf import settings
import os
import PIL
from PIL import Image
from django.db import models
from django.utils.text import slugify
# Create your models here.
from utils import utils


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    # permite deixar imagem em branco
    imagem = models.ImageField(
        upload_to='produto_imagens/%Y/%m', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True,
                            null=True)  # precisa ser unico
    preco_marketing = models.FloatField()  # sem defalt precisa passar algum valor
    preco_marketing_promocional = models.FloatField(
        default=0, verbose_name='Preço Promocional')
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variável'),
            ('S', 'Simples')
        )
    )

    def get_preco_formatado(self):
        # return f'R${self.preco_marketing:.2f}'.replace('.', ',')
        return utils.formata_preco(self.preco_marketing)
    get_preco_formatado.short_description = 'Preço'

    def get_preco_promocional_formatado(self):
        # return f'R${self.preco_marketing_promocional:.2f}'.replace('.', ',')
        return utils.formata_preco(self.preco_marketing_promocional)
    get_preco_promocional_formatado.short_description = 'Preço Promocional'

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_height = img_pil.size

        if original_width <= new_width:
            #print('retornando ,largura org menor ou igual que a nova')
            img_pil.close()
            return

        new_height = round((new_width*original_height)/original_width)
        # redimencionando a image-calculo lanczos
        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(
            img_full_path,
            optimize=True,
            quality=50
        )
        #print('imagem redimencionada')

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug

        super().save(*args, **kwargs)
        max_image_size = 800
        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.nome  # pra mostra str do produto


class Variacao(models.Model):
    # se apagar um produto todas as variações tbem serão apagadas
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    # pode ser deixado em branco
    nome = models.CharField(max_length=50, blank=True, null=True)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveBigIntegerField(
        default=1)  # produto sempre começará com 1

    def __str__(self):
        # o que será exibido
        return self.nome or self.produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
