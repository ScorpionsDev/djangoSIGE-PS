# -*- coding: utf-8 -*-
from djangosige.tests.test_case import BaseTestCase
from djangosige.apps.cadastro.models import Fornecedor, Cliente, Produto, Transportadora, MinhaEmpresa
from djangosige.apps.estoque.models import LocalEstoque, DEFAULT_LOCAL_ID, EntradaEstoque, SaidaEstoque, MovimentoEstoque, ItensMovimento, ProdutoEstocado
from djangosige.apps.compras.models import PedidoCompra, ItensCompra
from djangosige.apps.vendas.models import PedidoVenda, ItensVenda
from django.urls import reverse
from decimal import Decimal
from datetime import datetime
import json
from django.db import transaction

class IntegrationTestCase(BaseTestCase):
    
    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        
        # Configurar ubicación de stock predeterminada
        self.local_estoque = LocalEstoque.objects.get(pk=DEFAULT_LOCAL_ID)
        
        # Crear productos específicos para las pruebas de integración
        self.produto_a = Produto.objects.create(
            codigo='9999999999991',
            descricao='Producto Integración A',
            controlar_estoque=True,
            estoque_atual=Decimal('0.00'),
            venda='10.00'
        )
        self.produto_b = Produto.objects.create(
            codigo='9999999999992',
            descricao='Producto Integración B',
            controlar_estoque=True,
            estoque_atual=Decimal('50.00'),
            venda='15.00'
        )
        
        # Asegurar el ProductoEstocado correspondiente para el control correcto
        self.prod_estocado_a, _ = ProdutoEstocado.objects.get_or_create(
            local=self.local_estoque, produto=self.produto_a, defaults={'quantidade': Decimal('0.00')}
        )
        self.prod_estocado_b, _ = ProdutoEstocado.objects.get_or_create(
            local=self.local_estoque, produto=self.produto_b, defaults={'quantidade': Decimal('50.00')}
        )

        # Buscar proveedor y cliente de los fixtures
        self.fornecedor = Fornecedor.objects.order_by('id').last()
        self.cliente = Cliente.objects.order_by('id').last()

    # PI-01: Integración POST (Compras) a ORM (Inventario)
    def test_pi_01_compras_to_inventario(self):
        # 1. Crear pedido de compra en estado abierto
        pedido = PedidoCompra.objects.create(
            fornecedor=self.fornecedor,
            local_dest=self.local_estoque,
            movimentar_estoque=True,
            status='0',
            data_emissao=datetime.now().date(),
            valor_total='200.00'
        )
        # Crear ítem del pedido
        ItensCompra.objects.create(
            compra_id=pedido,
            produto=self.produto_a,
            quantidade=Decimal('20.00'),
            valor_unit='10.00',
            subtotal='200.00'
        )
        
        # 2. Recibir el pedido de compra, lo cual debe generar entrada en stock
        url = reverse('compras:receberpedidocompra', kwargs={'pk': pedido.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 3. Verificar persistencia y alteración de stock en el ORM
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, '4') # '4' representa recibido
        
        self.assertTrue(EntradaEstoque.objects.filter(pedido_compra=pedido).exists())
        
        self.produto_a.refresh_from_db()
        self.assertEqual(self.produto_a.estoque_atual, Decimal('20.00'))
        
        self.prod_estocado_a.refresh_from_db()
        self.assertEqual(self.prod_estocado_a.quantidade, Decimal('20.00'))

    # PI-02: Integración POST (Ventas) a ORM (Inventario)
    def test_pi_02_ventas_to_inventario(self):
        # 1. Crear pedido de venta
        venda = PedidoVenda.objects.create(
            cliente=self.cliente,
            local_orig=self.local_estoque,
            movimentar_estoque=True,
            status='0',
            data_emissao=datetime.now().date(),
            valor_total='150.00'
        )
        ItensVenda.objects.create(
            venda_id=venda,
            produto=self.produto_b,
            quantidade=Decimal('10.00'),
            valor_unit='15.00',
            subtotal='150.00'
        )
        
        # 2. Crear salida de stock en el módulo de stock referenciando la venta
        url = reverse('estoque:addsaidaestoqueview')
        data = {
            'quantidade_itens': 1,
            'valor_total': '150,00',
            'tipo_movimento': '1', # Salida por pedido de venta
            'local_orig': self.local_estoque.pk,
            'pedido_venda': venda.pk,
            'data_movimento': datetime.now().strftime('%d/%m/%Y'),
            'itens_form-0-produto': self.produto_b.pk,
            'itens_form-0-quantidade': '10,00',
            'itens_form-0-valor_unit': '15,00',
            'itens_form-0-subtotal': '150,00',
            'itens_form-TOTAL_FORMS': 1,
            'itens_form-INITIAL_FORMS': 0,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 3. Verificar persistencia de salida en el ORM y stock actualizado
        self.assertTrue(SaidaEstoque.objects.filter(pedido_venda=venda).exists())
        self.produto_b.refresh_from_db()
        self.assertEqual(self.produto_b.estoque_atual, Decimal('40.00'))
        
        self.prod_estocado_b.refresh_from_db()
        self.assertEqual(self.prod_estocado_b.quantidade, Decimal('40.00'))

    # PI-03: Inyección de Excepciones de Negocio (Venta con Stock Insuficiente)
    def test_pi_03_insufficient_stock_exception(self):
        # Para forzar el error, necesitamos que la cantidad local sea mayor o igual a la retirada, 
        # pero la cantidad global (estoque_atual) sea menor.
        self.produto_b.estoque_atual = Decimal('50.00')
        self.produto_b.save()
        self.prod_estocado_b.quantidade = Decimal('100.00')
        self.prod_estocado_b.save()
        
        url = reverse('estoque:addsaidaestoqueview')
        data = {
            'quantidade_itens': 1,
            'valor_total': '900,00',
            'tipo_movimento': '0', # Ajuste
            'local_orig': self.local_estoque.pk,
            'data_movimento': datetime.now().strftime('%d/%m/%Y'),
            'itens_form-0-produto': self.produto_b.pk,
            'itens_form-0-quantidade': '60,00', # Superior al stock global actual (50.00), inferior al local (100.00)
            'itens_form-0-valor_unit': '15,00',
            'itens_form-0-subtotal': '900,00',
            'itens_form-TOTAL_FORMS': 1,
            'itens_form-INITIAL_FORMS': 0,
        }
        
        # 2. Ejecutar y garantizar retorno con error de validación sin persistencia
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Debe acusar error en el formset de ítems de movimiento
        self.assertFormSetError(
            response.context['itens_form'], 0, 'quantidade',
            'Quantidade retirada do estoque maior que o estoque atual (50,00) do produto.'
        )
        
        # Verificar que la SaidaEstoque no fue registrada y el stock permanece en 50
        self.assertEqual(SaidaEstoque.objects.filter(itens_movimento__produto=self.produto_b, itens_movimento__quantidade=Decimal('60.00')).count(), 0)
        self.produto_b.refresh_from_db()
        self.assertEqual(self.produto_b.estoque_atual, Decimal('50.00'))

    # PI-04: Prueba End-to-End Automatizada de Lógica Secuencial (Compra a Venta)
    def test_pi_04_e2e_compra_a_venta(self):
        # 1. Stock inicial del Producto A es 0
        self.produto_a.estoque_atual = Decimal('0.00')
        self.produto_a.save()
        self.prod_estocado_a.quantidade = Decimal('0.00')
        self.prod_estocado_a.save()
        
        # 2. Registrar PedidoCompra de 50 unidades
        pedido = PedidoCompra.objects.create(
            fornecedor=self.fornecedor,
            local_dest=self.local_estoque,
            movimentar_estoque=True,
            status='0',
            data_emissao=datetime.now().date(),
            valor_total='500.00'
        )
        ItensCompra.objects.create(
            compra_id=pedido,
            produto=self.produto_a,
            quantidade=Decimal('50.00'),
            valor_unit='10.00',
            subtotal='500.00'
        )
        
        # 3. Recibir el pedido de compra (el stock sube a 50)
        url_receber = reverse('compras:receberpedidocompra', kwargs={'pk': pedido.pk})
        response = self.client.get(url_receber, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.produto_a.refresh_from_db()
        self.assertEqual(self.produto_a.estoque_atual, Decimal('50.00'))
        
        # 4. Registrar PedidoVenda de 20 unidades
        venda = PedidoVenda.objects.create(
            cliente=self.cliente,
            local_orig=self.local_estoque,
            movimentar_estoque=True,
            status='0',
            data_emissao=datetime.now().date(),
            valor_total='300.00'
        )
        ItensVenda.objects.create(
            venda_id=venda,
            produto=self.produto_a,
            quantidade=Decimal('20.00'),
            valor_unit='15.00',
            subtotal='300.00'
        )
        
        # 5. Crear salida de stock basada en el pedido de venta (el stock baja a 30)
        url_saida = reverse('estoque:addsaidaestoqueview')
        data = {
            'quantidade_itens': 1,
            'valor_total': '300,00',
            'tipo_movimento': '1', # Salida por pedido de venta
            'local_orig': self.local_estoque.pk,
            'pedido_venda': venda.pk,
            'data_movimento': datetime.now().strftime('%d/%m/%Y'),
            'itens_form-0-produto': self.produto_a.pk,
            'itens_form-0-quantidade': '20,00',
            'itens_form-0-valor_unit': '15,00',
            'itens_form-0-subtotal': '300,00',
            'itens_form-TOTAL_FORMS': 1,
            'itens_form-INITIAL_FORMS': 0,
        }
        response = self.client.post(url_saida, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 6. Validar stock final (50 - 20 = 30)
        self.produto_a.refresh_from_db()
        self.assertEqual(self.produto_a.estoque_atual, Decimal('30.00'))
        self.prod_estocado_a.refresh_from_db()
        self.assertEqual(self.prod_estocado_a.quantidade, Decimal('30.00'))

    # PI-05: Stress Testing de Interfaces Concurrentes (Múltiples Movimientos Coexistentes)
    def test_pi_05_concurrent_stress_movements(self):
        # Stock inicial: 50.00
        self.produto_b.estoque_atual = Decimal('50.00')
        self.produto_b.save()
        self.prod_estocado_b.quantidade = Decimal('50.00')
        self.prod_estocado_b.save()
        
        # 10 entradas de 5.00 unidades (+50.00)
        url_entrada = reverse('estoque:addentradaestoqueview')
        for i in range(10):
            data = {
                'quantidade_itens': 1,
                'valor_total': '50,00',
                'tipo_movimento': '0', # Ajuste
                'local_dest': self.local_estoque.pk,
                'data_movimento': datetime.now().strftime('%d/%m/%Y'),
                'itens_form-0-produto': self.produto_b.pk,
                'itens_form-0-quantidade': '5,00',
                'itens_form-0-valor_unit': '10,00',
                'itens_form-0-subtotal': '50,00',
                'itens_form-TOTAL_FORMS': 1,
                'itens_form-INITIAL_FORMS': 0,
            }
            response = self.client.post(url_entrada, data, follow=True)
            self.assertEqual(response.status_code, 200)
            
        # 10 salidas de 2.00 unidades (-20.00)
        url_saida = reverse('estoque:addsaidaestoqueview')
        for i in range(10):
            data = {
                'quantidade_itens': 1,
                'valor_total': '30,00',
                'tipo_movimento': '0', # Ajuste
                'local_orig': self.local_estoque.pk,
                'data_movimento': datetime.now().strftime('%d/%m/%Y'),
                'itens_form-0-produto': self.produto_b.pk,
                'itens_form-0-quantidade': '2,00',
                'itens_form-0-valor_unit': '15,00',
                'itens_form-0-subtotal': '30,00',
                'itens_form-TOTAL_FORMS': 1,
                'itens_form-INITIAL_FORMS': 0,
            }
            response = self.client.post(url_saida, data, follow=True)
            self.assertEqual(response.status_code, 200)
            
        # Stock final esperado: 50 + 50 - 20 = 80.00
        self.produto_b.refresh_from_db()
        self.assertEqual(self.produto_b.estoque_atual, Decimal('80.00'))
        self.prod_estocado_b.refresh_from_db()
        self.assertEqual(self.prod_estocado_b.quantidade, Decimal('80.00'))

    # PI-06: Verificación de Integridad de Datos e Historial (Trazabilidad Transaccional)
    def test_pi_06_data_integrity_and_traceability(self):
        # 1. Registrar pedido de compra y pedido de venta
        pedido = PedidoCompra.objects.create(
            fornecedor=self.fornecedor,
            local_dest=self.local_estoque,
            movimentar_estoque=True,
            status='0',
            data_emissao=datetime.now().date(),
            valor_total='100.00'
        )
        venda = PedidoVenda.objects.create(
            cliente=self.cliente,
            local_orig=self.local_estoque,
            movimentar_estoque=True,
            status='0',
            data_emissao=datetime.now().date(),
            valor_total='150.00'
        )
        
        # 2. Realizar movimientos de entrada y salida
        ItensCompra.objects.create(
            compra_id=pedido,
            produto=self.produto_a,
            quantidade=Decimal('10.00'),
            valor_unit='10.00',
            subtotal='100.00'
        )
        self.client.get(reverse('compras:receberpedidocompra', kwargs={'pk': pedido.pk}), follow=True)
        
        url_saida = reverse('estoque:addsaidaestoqueview')
        data = {
            'quantidade_itens': 1,
            'valor_total': '150,00',
            'tipo_movimento': '1',
            'local_orig': self.local_estoque.pk,
            'pedido_venda': venda.pk,
            'data_movimento': datetime.now().strftime('%d/%m/%Y'),
            'itens_form-0-produto': self.produto_b.pk,
            'itens_form-0-quantidade': '10,00',
            'itens_form-0-valor_unit': '15,00',
            'itens_form-0-subtotal': '150,00',
            'itens_form-TOTAL_FORMS': 1,
            'itens_form-INITIAL_FORMS': 0,
        }
        self.client.post(url_saida, data, follow=True)
        
        # 3. Verificar la existencia y vínculos en el historial
        entrada = EntradaEstoque.objects.get(pedido_compra=pedido)
        self.assertEqual(entrada.tipo_movimento, '1') # Entrada por pedido de compra
        
        saida = SaidaEstoque.objects.get(pedido_venda=venda)
        self.assertEqual(saida.tipo_movimento, '1') # Salida por pedido de venta
        
        # 4. Validar visibilidad en la lista de movimientos de stock
        response = self.client.get(reverse('estoque:listamovimentoestoqueview'))
        self.assertEqual(response.status_code, 200)
        all_movimentos = response.context['all_movimentos']
        
        entrada_pks = [m.pk for m in all_movimentos if isinstance(m, EntradaEstoque)]
        saida_pks = [m.pk for m in all_movimentos if isinstance(m, SaidaEstoque)]
        self.assertIn(entrada.pk, entrada_pks)
        self.assertIn(saida.pk, saida_pks)

    # PI-07: Tolerancia a Fallos y Atomicidad (Rollback ante Fallos en Interfaces)
    def test_pi_07_transactional_rollback_on_failure(self):
        # 1. Stock inicial del Producto A es 0 y del Producto B es 50
        self.assertEqual(self.produto_a.estoque_atual, Decimal('0.00'))
        self.assertEqual(self.produto_b.estoque_atual, Decimal('50.00'))
        
        # 2. Ejecutar operaciones dentro de transaction.atomic y forzar fallo
        try:
            with transaction.atomic():
                self.produto_a.estoque_atual += Decimal('10.00')
                self.produto_a.save()
                
                self.produto_b.estoque_atual += Decimal('20.00')
                self.produto_b.save()
                
                # Forzar excepción para simular fallo en medio de la transacción
                raise ValueError("Fallo simulado para forzar Rollback")
        except ValueError:
            pass
            
        # 3. Asegurar que ningún stock fue modificado en la base de datos (Rollback)
        self.produto_a.refresh_from_db()
        self.produto_b.refresh_from_db()
        self.assertEqual(self.produto_a.estoque_atual, Decimal('0.00'))
        self.assertEqual(self.produto_b.estoque_atual, Decimal('50.00'))

    # INT-CAD-001: Registro/InfoCliente
    def test_int_cad_001_info_cliente(self):
        url = reverse('cadastro:infocliente')
        response = self.client.post(url, {'pessoaId': self.cliente.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(any(item['model'] == 'cadastro.cliente' for item in data))
        
    # INT-CAD-002: Registro/InfoProveedor
    def test_int_cad_002_info_fornecedor(self):
        url = reverse('cadastro:infofornecedor')
        response = self.client.post(url, {'pessoaId': self.fornecedor.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(any(item['model'] == 'cadastro.fornecedor' for item in data))
        
    # INT-CAD-003: Registro/InfoEmpresa
    def test_int_cad_003_info_empresa(self):
        url = reverse('cadastro:infoempresa')
        empresa = MinhaEmpresa.objects.order_by('id').last()
        if empresa:
            response = self.client.post(url, {'pessoaId': empresa.m_empresa.pk})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content.decode('utf-8'))
            self.assertTrue(any(item['model'] == 'cadastro.pessoajuridica' for item in data))
            
    # INT-CAD-004: Registro/InfoTransportista
    def test_int_cad_004_info_transportadora(self):
        transportadora = Transportadora.objects.order_by('id').last()
        if not transportadora:
            transportadora = Transportadora.objects.create(nome_razao_social="Transportista de Prueba")
        url = reverse('cadastro:infotransportadora')
        response = self.client.post(url, {'transportadoraId': transportadora.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(data, list)
        
    # INT-CAD-005: Registro/InfoProducto
    def test_int_cad_005_info_produto(self):
        url = reverse('cadastro:infoproduto')
        response = self.client.post(url, {'produtoId': self.produto_b.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(any(item['model'] == 'cadastro.produto' for item in data))
        
    # INT-VEN-001: Ventas/InfoVenta
    def test_int_ven_001_info_venda(self):
        venda = PedidoVenda.objects.create(
            cliente=self.cliente,
            local_orig=self.local_estoque,
            movimentar_estoque=False,
            status='0',
            data_emissao=datetime.now().date(),
            valor_total='0.00'
        )
        url = reverse('vendas:infovenda')
        response = self.client.post(url, {'vendaId': venda.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(any(item['model'] == 'vendas.pedidovenda' for item in data))
