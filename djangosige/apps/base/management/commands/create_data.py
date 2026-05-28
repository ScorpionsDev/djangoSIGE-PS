# -*- coding: utf-8 -*-
"""
Popula o banco com dados de exemplo (clientes, fornecedores, produtos,
empresas, transportadoras, usuários).

Uso:
    python manage.py create_data
    python manage.py create_data --clear        # apaga antes de recriar
    python manage.py create_data --clientes 50  # ajusta a quantidade
"""

from __future__ import unicode_literals

import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from faker import Faker

from djangosige.apps.cadastro.models import (
    Banco,
    Categoria,
    Cliente,
    Email,
    Empresa,
    Endereco,
    Fornecedor,
    Marca,
    Produto,
    Telefone,
    Transportadora,
    Unidade,
)
from djangosige.apps.cadastro.models.base import (
    PessoaFisica,
    PessoaJuridica,
)
from djangosige.apps.login.models import Usuario


UFS = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
]

UNIDADES_BASE = [
    ('UN', 'Unidade'),
    ('KG', 'Quilograma'),
    ('CX', 'Caixa'),
    ('LT', 'Litro'),
    ('PC', 'Peça'),
    ('MT', 'Metro'),
]

CATEGORIAS_BASE = [
    'Eletrônicos', 'Vestuário', 'Alimentos', 'Limpeza',
    'Papelaria', 'Ferramentas', 'Móveis', 'Bebidas',
]

MARCAS_BASE = [
    'Acme', 'Globex', 'Initech', 'Umbrella', 'Stark',
    'Wayne', 'Pied Piper', 'Hooli',
]


class Command(BaseCommand):
    help = 'Popula o banco com dados de exemplo usando Faker (pt_BR).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Apaga os dados de exemplo antes de criar novamente.')
        parser.add_argument(
            '--usuarios', type=int, default=3,
            help='Quantidade de usuários comuns (default: 3).')
        parser.add_argument(
            '--empresas', type=int, default=2,
            help='Quantidade de empresas (default: 2).')
        parser.add_argument(
            '--clientes', type=int, default=15,
            help='Quantidade de clientes (default: 15).')
        parser.add_argument(
            '--fornecedores', type=int, default=8,
            help='Quantidade de fornecedores (default: 8).')
        parser.add_argument(
            '--transportadoras', type=int, default=3,
            help='Quantidade de transportadoras (default: 3).')
        parser.add_argument(
            '--produtos', type=int, default=25,
            help='Quantidade de produtos (default: 25).')
        parser.add_argument(
            '--seed', type=int, default=None,
            help='Seed do Faker para resultados reprodutíveis.')

    def handle(self, *args, **options):
        self.fake = Faker('pt_BR')
        if options['seed'] is not None:
            Faker.seed(options['seed'])
            random.seed(options['seed'])

        if options['clear']:
            self._clear()

        with transaction.atomic():
            self._criar_usuarios(options['usuarios'])
            self._criar_categorias_marcas_unidades()
            self._criar_produtos(options['produtos'])
            self._criar_empresas(options['empresas'])
            self._criar_clientes(options['clientes'])
            self._criar_fornecedores(options['fornecedores'])
            self._criar_transportadoras(options['transportadoras'])

        self.stdout.write(self.style.SUCCESS('Dados de exemplo criados com sucesso.'))
        self._print_resumo()

    # ------------------------------------------------------------------
    # Limpeza
    # ------------------------------------------------------------------
    def _clear(self):
        self.stdout.write('Limpando dados anteriores...')
        # Pessoa abstrata via multi-tabela: deletar subclasses dispara cascade.
        Cliente.objects.all().delete()
        Fornecedor.objects.all().delete()
        Transportadora.objects.all().delete()
        Empresa.objects.all().delete()
        # Tabelas auxiliares: só remove se nada externo referenciar mais.
        Produto.objects.all().delete()
        Categoria.objects.all().delete()
        Marca.objects.all().delete()
        Unidade.objects.all().delete()
        # Usuários: preserva superusers e staff manualmente criados.
        User.objects.filter(is_superuser=False, is_staff=False).delete()

    # ------------------------------------------------------------------
    # Usuários
    # ------------------------------------------------------------------
    def _criar_usuarios(self, quantidade):
        self.stdout.write(f'Criando {quantidade} usuários...')
        for _ in range(quantidade):
            username = self.fake.unique.user_name()
            user = User.objects.create_user(
                username=username,
                email=self.fake.email(),
                password='senha123',
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
            )
            Usuario.objects.create(user=user)

    # ------------------------------------------------------------------
    # Tabelas auxiliares de produto
    # ------------------------------------------------------------------
    def _criar_categorias_marcas_unidades(self):
        self.stdout.write('Garantindo categorias, marcas e unidades...')
        self.categorias = [
            Categoria.objects.get_or_create(categoria_desc=desc)[0]
            for desc in CATEGORIAS_BASE
        ]
        self.marcas = [
            Marca.objects.get_or_create(marca_desc=desc)[0]
            for desc in MARCAS_BASE
        ]
        self.unidades = [
            Unidade.objects.get_or_create(
                sigla_unidade=sigla, defaults={'unidade_desc': desc})[0]
            for sigla, desc in UNIDADES_BASE
        ]

    def _criar_produtos(self, quantidade):
        self.stdout.write(f'Criando {quantidade} produtos...')
        for i in range(quantidade):
            custo = Decimal(str(round(random.uniform(5, 500), 2)))
            margem = Decimal(str(round(random.uniform(1.2, 2.5), 2)))
            Produto.objects.create(
                codigo=f'PRD{i + 1:05d}',
                codigo_barras=self.fake.ean13(),
                descricao=self.fake.unique.catch_phrase(),
                categoria=random.choice(self.categorias),
                marca=random.choice(self.marcas),
                unidade=random.choice(self.unidades),
                custo=custo,
                venda=(custo * margem).quantize(Decimal('0.01')),
                ncm=f'{random.randint(1000, 9999)}.{random.randint(10, 99)}.{random.randint(10, 99)}',
                origem='0',
            )

    # ------------------------------------------------------------------
    # Pessoa (compartilhado por cliente/fornecedor/transportadora/empresa)
    # ------------------------------------------------------------------
    def _criar_pessoa(self, instance, tipo_pessoa):
        """Preenche e salva uma subclasse de Pessoa + endereço/telefone padrão.

        `instance` é uma subclasse de Pessoa ainda não persistida.
        `tipo_pessoa` deve ser 'PF' ou 'PJ'.
        """
        if tipo_pessoa == 'PJ':
            instance.nome_razao_social = self.fake.company()
        else:
            instance.nome_razao_social = self.fake.name()
        instance.tipo_pessoa = tipo_pessoa
        instance.save()

        if tipo_pessoa == 'PF':
            PessoaFisica.objects.create(
                pessoa_id=instance,
                cpf=self.fake.cpf(),
                rg=self.fake.rg() if hasattr(self.fake, 'rg') else str(random.randint(10000000, 99999999)),
                nascimento=self.fake.date_of_birth(minimum_age=18, maximum_age=80),
            )
        else:
            PessoaJuridica.objects.create(
                pessoa_id=instance,
                cnpj=self.fake.cnpj(),
                nome_fantasia=self.fake.company_suffix() + ' ' + instance.nome_razao_social,
                inscricao_estadual=str(random.randint(10**8, 10**9 - 1)),
                responsavel=self.fake.name(),
                sit_fiscal=random.choice(['LR', 'LP', 'SN']),
            )

        endereco = Endereco.objects.create(
            pessoa_end=instance,
            tipo_endereco='UNI',
            logradouro=self.fake.street_name(),
            numero=str(random.randint(1, 9999)),
            bairro=self.fake.bairro() if hasattr(self.fake, 'bairro') else 'Centro',
            municipio=self.fake.city(),
            cep=self.fake.postcode().replace('-', ''),
            uf=random.choice(UFS),
            pais='Brasil',
            cpais='1058',
        )
        telefone = Telefone.objects.create(
            pessoa_tel=instance,
            tipo_telefone=random.choice(['FIX', 'CEL']),
            telefone=self.fake.phone_number()[:32],
        )
        email = Email.objects.create(
            pessoa_email=instance,
            email=self.fake.email(),
        )
        banco = Banco.objects.create(
            pessoa_banco=instance,
            banco='001',
            agencia=str(random.randint(1000, 9999)),
            conta=str(random.randint(10000, 999999)),
            digito=str(random.randint(0, 9)),
        )

        instance.endereco_padrao = endereco
        instance.telefone_padrao = telefone
        instance.email_padrao = email
        instance.banco_padrao = banco
        instance.save()

    # ------------------------------------------------------------------
    # Empresas / Clientes / Fornecedores / Transportadoras
    # ------------------------------------------------------------------
    def _criar_empresas(self, quantidade):
        self.stdout.write(f'Criando {quantidade} empresas...')
        for _ in range(quantidade):
            empresa = Empresa(
                cnae=f'{random.randint(1000, 9999)}-{random.randint(0, 9)}/{random.randint(10, 99)}',
            )
            self._criar_pessoa(empresa, 'PJ')

    def _criar_clientes(self, quantidade):
        self.stdout.write(f'Criando {quantidade} clientes...')
        for _ in range(quantidade):
            tipo = random.choice(['PF', 'PJ'])
            cliente = Cliente(
                limite_de_credito=Decimal(str(round(random.uniform(500, 50000), 2))),
                indicador_ie='9' if tipo == 'PF' else random.choice(['1', '2', '9']),
            )
            self._criar_pessoa(cliente, tipo)

    def _criar_fornecedores(self, quantidade):
        self.stdout.write(f'Criando {quantidade} fornecedores...')
        ramos = ['Atacado', 'Distribuidor', 'Indústria', 'Importador', 'Varejo']
        for _ in range(quantidade):
            fornecedor = Fornecedor(ramo=random.choice(ramos))
            self._criar_pessoa(fornecedor, 'PJ')

    def _criar_transportadoras(self, quantidade):
        self.stdout.write(f'Criando {quantidade} transportadoras...')
        for _ in range(quantidade):
            transp = Transportadora()
            self._criar_pessoa(transp, 'PJ')

    # ------------------------------------------------------------------
    # Resumo
    # ------------------------------------------------------------------
    def _print_resumo(self):
        self.stdout.write('')
        self.stdout.write('Resumo:')
        for label, model in [
            ('Usuários (auth)', User),
            ('Empresas', Empresa),
            ('Clientes', Cliente),
            ('Fornecedores', Fornecedor),
            ('Transportadoras', Transportadora),
            ('Produtos', Produto),
            ('Categorias', Categoria),
            ('Marcas', Marca),
            ('Unidades', Unidade),
        ]:
            self.stdout.write(f'  - {label}: {model.objects.count()}')
