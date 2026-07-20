# -*- coding: utf-8 -*-
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from djangosige.apps.cadastro.models import Produto, Fornecedor
from djangosige.apps.compras.models import PedidoCompra, ItensCompra
from djangosige.apps.estoque.models import (
    LocalEstoque, EntradaEstoque, SaidaEstoque, TransferenciaEstoque, ItensMovimento
)


class Command(BaseCommand):
    help = "Genera datos de volumen para Pruebas de Sistema (PS-VOL): pedidos de compra y movimientos de estoque"

    def add_arguments(self, parser):
        parser.add_argument('--pedidos', type=int, default=100,
                             help='Total de pedidos de compra deseados (incluye los ya existentes)')
        parser.add_argument('--movimientos', type=int, default=200,
                             help='Total de movimientos de estoque deseados (incluye los ya existentes)')

    def handle(self, *args, **options):
        n_pedidos = options['pedidos']
        n_movimientos = options['movimientos']

        productos = list(Produto.objects.all())
        fornecedores = list(Fornecedor.objects.all())
        locales = list(LocalEstoque.objects.all())

        if not productos:
            self.stderr.write(self.style.ERROR("No hay productos en la base. Abortando."))
            return
        if not fornecedores:
            self.stderr.write(self.style.ERROR("No hay fornecedores en la base. Abortando."))
            return
        if not locales:
            self.stderr.write(self.style.ERROR("No hay locales de estoque en la base. Abortando."))
            return

        self.stdout.write(f"Productos: {len(productos)} | Fornecedores: {len(fornecedores)} | Locales: {len(locales)}")

        # ---------- PEDIDOS DE COMPRA ----------
        existentes = PedidoCompra.objects.count()
        a_crear = max(0, n_pedidos - existentes)
        self.stdout.write(f"Pedidos de compra existentes: {existentes}. Creando {a_crear} adicionales...")

        with transaction.atomic():
            for i in range(a_crear):
                fornecedor = random.choice(fornecedores)
                local = random.choice(locales)

                pedido = PedidoCompra.objects.create(
                    fornecedor=fornecedor,
                    mod_frete='9',
                    local_dest=local,
                    movimentar_estoque=False,
                    data_emissao=date.today() - timedelta(days=random.randint(0, 365)),
                    valor_total=Decimal('0.00'),
                    tipo_desconto='0',
                    desconto=Decimal('0.00'),
                    despesas=Decimal('0.00'),
                    frete=Decimal('0.00'),
                    seguro=Decimal('0.00'),
                    total_icms=Decimal('0.00'),
                    total_ipi=Decimal('0.00'),
                    observacoes=f'Fixture volumen k6/PS-VOL #{i + 1}',
                    data_entrega=date.today() + timedelta(days=random.randint(1, 30)),
                    status='0',
                )

                n_items = random.randint(1, 5)
                total = Decimal('0.00')
                for _ in range(n_items):
                    producto = random.choice(productos)
                    qtd = Decimal(random.randint(1, 10))
                    valor_unit = Decimal('10.00')
                    subtotal = qtd * valor_unit
                    total += subtotal

                    item = ItensCompra(
                        produto=producto,
                        quantidade=qtd,
                        valor_unit=valor_unit,
                        subtotal=subtotal,
                        tipo_desconto='0',
                        desconto=Decimal('0.00'),
                        p_icms=Decimal('0.00'),
                        p_ipi=Decimal('0.00'),
                        vicms=Decimal('0.00'),
                        vipi=Decimal('0.00'),
                        auto_calcular_impostos=True,
                        icms_incluido_preco=False,
                        ipi_incluido_preco=False,
                        incluir_bc_icms=False,
                    )
                    item.compra_id = pedido  # FK literalmente llamada 'compra_id'
                    item.save()

                pedido.valor_total = total
                pedido.save()

                if (i + 1) % 20 == 0:
                    self.stdout.write(f"  ... {i + 1}/{a_crear} pedidos creados")

        self.stdout.write(self.style.SUCCESS(f"Total pedidos de compra: {PedidoCompra.objects.count()}"))

        # ---------- MOVIMIENTOS DE ESTOQUE ----------
        existentes_mov = (
            EntradaEstoque.objects.count()
            + SaidaEstoque.objects.count()
            + TransferenciaEstoque.objects.count()
        )
        a_crear_mov = max(0, n_movimientos - existentes_mov)
        self.stdout.write(f"Movimientos existentes: {existentes_mov}. Creando {a_crear_mov} adicionales...")

        with transaction.atomic():
            creados = 0
            intentos = 0
            while creados < a_crear_mov and intentos < a_crear_mov * 3:
                intentos += 1
                tipo = random.choice(['entrada', 'salida', 'transferencia'])

                if tipo == 'entrada':
                    local = random.choice(locales)
                    mov = EntradaEstoque.objects.create(
                        data_movimento=date.today() - timedelta(days=random.randint(0, 365)),
                        quantidade_itens=0,
                        valor_total=Decimal('0.00'),
                        observacoes=f'Fixture volumen k6/PS-VOL #{creados + 1}',
                        local_dest=local,
                        tipo_movimento='0',  # Ajuste
                    )
                elif tipo == 'salida':
                    local = random.choice(locales)
                    mov = SaidaEstoque.objects.create(
                        data_movimento=date.today() - timedelta(days=random.randint(0, 365)),
                        quantidade_itens=0,
                        valor_total=Decimal('0.00'),
                        observacoes=f'Fixture volumen k6/PS-VOL #{creados + 1}',
                        local_orig=local,
                        tipo_movimento='0',  # Ajuste
                    )
                else:
                    if len(locales) < 2:
                        continue
                    orig, dest = random.sample(locales, 2)
                    mov = TransferenciaEstoque.objects.create(
                        data_movimento=date.today() - timedelta(days=random.randint(0, 365)),
                        quantidade_itens=0,
                        valor_total=Decimal('0.00'),
                        observacoes=f'Fixture volumen k6/PS-VOL #{creados + 1}',
                        local_estoque_orig=orig,
                        local_estoque_dest=dest,
                    )

                n_items = random.randint(1, 3)
                qtd_total = 0
                valor_total = Decimal('0.00')
                for _ in range(n_items):
                    producto = random.choice(productos)
                    qtd = Decimal(random.randint(1, 5))
                    valor_unit = Decimal('10.00')
                    subtotal = qtd * valor_unit
                    qtd_total += qtd
                    valor_total += subtotal

                    ItensMovimento.objects.create(
                        produto=producto,
                        movimento_id=mov,
                        quantidade=qtd,
                        valor_unit=valor_unit,
                        subtotal=subtotal,
                    )

                mov.quantidade_itens = int(qtd_total)
                mov.valor_total = valor_total
                mov.save()

                creados += 1
                if creados % 40 == 0:
                    self.stdout.write(f"  ... {creados}/{a_crear_mov} movimientos creados")

        self.stdout.write(self.style.SUCCESS(
            f"Total movimientos: entradas={EntradaEstoque.objects.count()}, "
            f"salidas={SaidaEstoque.objects.count()}, "
            f"transferencias={TransferenciaEstoque.objects.count()}"
        ))
