# -*- coding: utf-8 -*-
"""
Pruebas UNITARIAS — módulo compras (SOLO modelos)

Estrategia de aislamiento:
- Los modelos se instancian sin guardar en BD (sin .save() ni fixtures).
- Las ForeignKeys se reemplazan con unittest.mock.MagicMock.
- No se hereda de BaseTestCase (que levanta fixtures y BD completa).
"""

from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock, patch


# ─────────────────────────────────────────────
# MODELOS — ItensCompra
# ─────────────────────────────────────────────

class ItensCompraCalculosTestCase(TestCase):
    """Pruebas unitarias de los métodos de cálculo de ItensCompra."""

    def _make_item(self, quantidade, valor_unit, tipo_desconto, desconto, subtotal,
                   vicms=None, vipi=None):
        from djangosige.apps.compras.models import ItensCompra
        item = ItensCompra.__new__(ItensCompra)
        item.quantidade = Decimal(str(quantidade))
        item.valor_unit = Decimal(str(valor_unit))
        item.tipo_desconto = tipo_desconto
        item.desconto = Decimal(str(desconto))
        item.subtotal = Decimal(str(subtotal))
        item.vicms = Decimal(str(vicms)) if vicms is not None else None
        item.vipi = Decimal(str(vipi)) if vipi is not None else None
        return item

    def test_vprod_es_cantidad_por_valor_unitario(self):
        item = self._make_item(5, '20.00', '0', '0.00', '100.00')
        self.assertEqual(item.vprod, Decimal('100.00'))

    def test_vprod_redondea_a_dos_decimales(self):
        item = self._make_item(3, '10.333', '0', '0.00', '30.999')
        self.assertEqual(item.vprod, Decimal('31.00'))

    def test_total_sem_desconto_tipo_valor_fijo(self):
        item = self._make_item(1, '100.00', '0', '20.00', '80.00')
        self.assertEqual(item.get_total_sem_desconto(), Decimal('100.00'))

    def test_total_sem_desconto_tipo_porcentaje(self):
        item = self._make_item(1, '100.00', '1', '20.00', '80.00')
        resultado = item.get_total_sem_desconto()
        self.assertAlmostEqual(float(resultado), 100.0, places=2)

    def test_valor_desconto_tipo_valor_fijo(self):
        item = self._make_item(1, '100.00', '0', '15.00', '85.00')
        self.assertEqual(item.get_valor_desconto(), Decimal('15.00'))

    def test_valor_desconto_tipo_porcentaje(self):
        item = self._make_item(1, '100.00', '1', '20.00', '80.00')
        resultado = item.get_valor_desconto()
        self.assertAlmostEqual(float(resultado), 20.0, places=2)

    def test_total_impostos_con_ambos_impuestos(self):
        item = self._make_item(1, '100.00', '0', '0.00', '100.00',
                               vicms='10.00', vipi='5.00')
        self.assertEqual(item.get_total_impostos(), Decimal('15.00'))

    def test_total_impostos_sin_ninguno(self):
        item = self._make_item(1, '100.00', '0', '0.00', '100.00')
        self.assertEqual(item.get_total_impostos(), 0)

    def test_total_impostos_solo_icms(self):
        item = self._make_item(1, '100.00', '0', '0.00', '100.00',
                               vicms='8.00')
        self.assertEqual(item.get_total_impostos(), Decimal('8.00'))

    def test_total_com_impostos(self):
        item = self._make_item(1, '100.00', '0', '0.00', '90.00',
                               vicms='5.00', vipi='3.00')
        self.assertEqual(item.get_total_com_impostos(), Decimal('98.00'))


# ─────────────────────────────────────────────
# MODELOS — Compra
# ─────────────────────────────────────────────

class CompraCalculosTestCase(TestCase):
    """Pruebas unitarias de los métodos de cálculo de Compra."""

    def _make_compra(self, valor_total, total_icms, total_ipi,
                     tipo_desconto='0', desconto='0.00',
                     frete='0.00', seguro='0.00', despesas='0.00'):
        from djangosige.apps.compras.models import Compra
        from django.db.models.base import ModelState
        compra = Compra.__new__(Compra)
        compra._state = ModelState()
        compra._state.fields_cache = {}
        compra.valor_total = Decimal(valor_total)
        compra.total_icms = Decimal(total_icms)
        compra.total_ipi = Decimal(total_ipi)
        compra.tipo_desconto = tipo_desconto
        compra.desconto = Decimal(desconto)
        compra.frete = Decimal(frete)
        compra.seguro = Decimal(seguro)
        compra.despesas = Decimal(despesas)
        compra.id = None
        compra.cond_pagamento_id = None
        compra.local_dest_id = None
        compra.fornecedor_id = None
        compra._state.fields_cache['cond_pagamento'] = None
        _mock_local = MagicMock()
        _mock_local.id = None
        _mock_local.__bool__ = lambda self: False
        compra._state.fields_cache['local_dest'] = _mock_local
        return compra

    def test_impostos_suma_icms_e_ipi(self):
        compra = self._make_compra('460.00', '20.00', '10.00')
        self.assertEqual(compra.impostos, Decimal('30.00'))

    def test_get_total_sem_imposto(self):
        compra = self._make_compra('460.00', '20.00', '10.00')
        self.assertEqual(compra.get_total_sem_imposto(), Decimal('430.00'))

    def test_get_total_sem_imposto_sin_impuestos(self):
        compra = self._make_compra('460.00', '0.00', '0.00')
        self.assertEqual(compra.get_total_sem_imposto(), Decimal('460.00'))

    def test_get_forma_pagamento_sin_condicion(self):
        compra = self._make_compra('100.00', '0.00', '0.00')
        self.assertEqual(compra.get_forma_pagamento(), "")

    def test_get_local_dest_id_sin_local(self):
        compra = self._make_compra('100.00', '0.00', '0.00')
        self.assertEqual(compra.get_local_dest_id(), "")

    def test_str_representacion(self):
        compra = self._make_compra('100.00', '0.00', '0.00')
        compra.id = 42
        self.assertIn('42', str(compra))

    @patch('djangosige.apps.compras.models.ItensCompra.objects')
    def test_format_desconto_tipo_valor_fijo(self, mock_qs):
        compra = self._make_compra('460.00', '0.00', '0.00',
                                   tipo_desconto='0', desconto='40.00')
        resultado = compra.format_desconto()
        self.assertIn('40', resultado)

    def test_format_valor_total(self):
        compra = self._make_compra('460.00', '0.00', '0.00')
        resultado = compra.format_valor_total()
        self.assertIn('460', resultado)


# ─────────────────────────────────────────────
# MODELOS — Pagamento
# ─────────────────────────────────────────────

class PagamentoModelTestCase(TestCase):

    def _make_pago(self, valor, vencimiento_str):
        from djangosige.apps.compras.models.pagamento import Pagamento
        from datetime import date
        pago = Pagamento.__new__(Pagamento)
        pago.indice_parcela = 1
        pago.valor_parcela = Decimal(valor)
        pago.vencimento = date.fromisoformat(vencimiento_str)
        return pago

    def test_format_valor_parcela_contiene_valor(self):
        pago = self._make_pago('150.50', '2024-07-31')
        self.assertIn('150', pago.format_valor_parcela)

    def test_format_vencimento_formato_br(self):
        pago = self._make_pago('100.00', '2024-07-31')
        self.assertEqual(pago.format_vencimento, '31/07/2024')


# ─────────────────────────────────────────────
# MODELOS — Compra (métodos adicionales)
# ─────────────────────────────────────────────

class CompraFormatMethodsTestCase(TestCase):
    """Cubre los métodos format_* de Compra."""

    def _make_compra(self, valor_total='100.00', total_icms='10.00', total_ipi='5.00',
                     frete='3.00', seguro='2.00', despesas='1.00',
                     desconto='0.00', tipo_desconto='0'):
        from djangosige.apps.compras.models import Compra
        from django.db.models.base import ModelState
        compra = Compra.__new__(Compra)
        compra._state = ModelState()
        compra._state.fields_cache = {}
        compra.valor_total = Decimal(valor_total)
        compra.total_icms = Decimal(total_icms)
        compra.total_ipi = Decimal(total_ipi)
        compra.frete = Decimal(frete)
        compra.seguro = Decimal(seguro)
        compra.despesas = Decimal(despesas)
        compra.desconto = Decimal(desconto)
        compra.tipo_desconto = tipo_desconto
        compra.id = 1
        compra.cond_pagamento_id = None
        compra.local_dest_id = None
        compra.fornecedor_id = None
        compra._state.fields_cache['cond_pagamento'] = None
        _mock_local = MagicMock()
        _mock_local.__bool__ = lambda self: False
        compra._state.fields_cache['local_dest'] = _mock_local
        return compra

    def test_format_frete(self):
        compra = self._make_compra(frete='3.50')
        self.assertIn('3', compra.format_frete())

    def test_format_seguro(self):
        compra = self._make_compra(seguro='2.00')
        self.assertIn('2', compra.format_seguro())

    def test_format_despesas(self):
        compra = self._make_compra(despesas='1.75')
        self.assertIn('1', compra.format_despesas())

    def test_format_impostos(self):
        compra = self._make_compra(total_icms='10.00', total_ipi='5.00')
        self.assertIn('15', compra.format_impostos())

    def test_format_vicms(self):
        compra = self._make_compra(total_icms='10.00')
        self.assertIn('10', compra.format_vicms())

    def test_format_vipi(self):
        compra = self._make_compra(total_ipi='5.00')
        self.assertIn('5', compra.format_vipi())

    def test_format_total_sem_imposto(self):
        compra = self._make_compra(valor_total='100.00', total_icms='10.00', total_ipi='5.00')
        self.assertIn('85', compra.format_total_sem_imposto())

    def test_format_total_sem_desconto_tipo_fijo(self):
        compra = self._make_compra(valor_total='100.00', desconto='10.00', tipo_desconto='0')
        self.assertIn('90', compra.format_total_sem_desconto())

    def test_format_desconto_tipo_porcentaje(self):
        compra = self._make_compra(desconto='10.00', tipo_desconto='1')
        item_mock = MagicMock()
        item_mock.get_total_sem_desconto.return_value = Decimal('200.00')
        with patch('djangosige.apps.compras.models.compras.ItensCompra.objects.filter',
                   return_value=[item_mock]):
            resultado = compra.format_desconto()
        self.assertIn('20', resultado)

    def test_get_total_produtos_con_items_mockeados(self):
        compra = self._make_compra()
        item1 = MagicMock()
        item1.vprod = Decimal('50.00')
        item2 = MagicMock()
        item2.vprod = Decimal('30.00')
        with patch('djangosige.apps.compras.models.compras.ItensCompra.objects.filter',
                   return_value=[item1, item2]):
            total = compra.get_total_produtos()
        self.assertEqual(total, Decimal('80.00'))

    def test_format_total_produtos(self):
        compra = self._make_compra()
        item = MagicMock()
        item.vprod = Decimal('75.00')
        with patch('djangosige.apps.compras.models.compras.ItensCompra.objects.filter',
                   return_value=[item]):
            resultado = compra.format_total_produtos()
        self.assertIn('75', resultado)

    def test_get_total_produtos_estoque_solo_controla_estoque(self):
        compra = self._make_compra()
        item_con = MagicMock()
        item_con.produto.controlar_estoque = True
        item_con.vprod = Decimal('40.00')
        item_sin = MagicMock()
        item_sin.produto.controlar_estoque = False
        item_sin.vprod = Decimal('99.00')
        mock_manager = MagicMock()
        mock_manager.all.return_value = [item_con, item_sin]
        with patch.object(type(compra), 'itens_compra',
                          new_callable=lambda: property(lambda self: mock_manager)):
            total = compra.get_total_produtos_estoque()
        self.assertEqual(total, Decimal('40.00'))

    def test_get_forma_pagamento_con_condicion(self):
        compra = self._make_compra()
        mock_cond = MagicMock()
        mock_cond.get_forma_display.return_value = 'À Vista'
        compra._state.fields_cache['cond_pagamento'] = mock_cond
        self.assertEqual(compra.get_forma_pagamento(), 'À Vista')

    def test_get_local_dest_id_con_local(self):
        compra = self._make_compra()
        mock_local = MagicMock()
        mock_local.id = 7
        mock_local.__bool__ = lambda self: True
        compra._state.fields_cache['local_dest'] = mock_local
        self.assertEqual(compra.get_local_dest_id(), 7)


# ─────────────────────────────────────────────
# MODELOS — OrcamentoCompra
# ─────────────────────────────────────────────

class OrcamentoCompraTestCase(TestCase):

    def _make_orcamento(self, status='0', data_vencimento='2024-07-31'):
        from djangosige.apps.compras.models import OrcamentoCompra
        from django.db.models.base import ModelState
        from datetime import date
        orc = OrcamentoCompra.__new__(OrcamentoCompra)
        orc._state = ModelState()
        orc._state.fields_cache = {}
        orc.id = 10
        orc.status = status
        orc.data_vencimento = date.fromisoformat(data_vencimento)
        orc.fornecedor_id = None
        orc.local_dest_id = None
        orc.cond_pagamento_id = None
        _mock_local = MagicMock()
        _mock_local.__bool__ = lambda self: False
        orc._state.fields_cache['local_dest'] = _mock_local
        orc._state.fields_cache['cond_pagamento'] = None
        return orc

    def test_tipo_compra_es_orcamento(self):
        orc = self._make_orcamento()
        self.assertEqual(orc.tipo_compra, 'Orçamento')

    def test_str_contiene_id(self):
        orc = self._make_orcamento()
        self.assertIn('10', str(orc))

    def test_format_data_vencimento(self):
        orc = self._make_orcamento(data_vencimento='2024-07-31')
        self.assertEqual(orc.format_data_vencimento, '31/07/2024')

    def test_edit_url_contiene_pk(self):
        orc = self._make_orcamento()
        self.assertIn('10', str(orc.edit_url()))


# ─────────────────────────────────────────────
# MODELOS — PedidoCompra
# ─────────────────────────────────────────────

class PedidoCompraTestCase(TestCase):

    def _make_pedido(self, status='0', data_entrega='2024-08-15'):
        from djangosige.apps.compras.models import PedidoCompra
        from django.db.models.base import ModelState
        from datetime import date
        ped = PedidoCompra.__new__(PedidoCompra)
        ped._state = ModelState()
        ped._state.fields_cache = {}
        ped.id = 20
        ped.status = status
        ped.data_entrega = date.fromisoformat(data_entrega)
        ped.fornecedor_id = None
        ped.local_dest_id = None
        ped.orcamento_id = None
        ped.cond_pagamento_id = None
        _mock_local = MagicMock()
        _mock_local.__bool__ = lambda self: False
        ped._state.fields_cache['local_dest'] = _mock_local
        ped._state.fields_cache['cond_pagamento'] = None
        ped._state.fields_cache['orcamento'] = None
        return ped

    def test_tipo_compra_es_pedido(self):
        ped = self._make_pedido()
        self.assertEqual(ped.tipo_compra, 'Pedido')

    def test_str_contiene_id_y_status(self):
        ped = self._make_pedido(status='0')
        texto = str(ped)
        self.assertIn('20', texto)
        self.assertIn('Aberto', texto)

    def test_str_status_cancelado(self):
        ped = self._make_pedido(status='2')
        self.assertIn('Cancelado', str(ped))

    def test_str_status_recebido(self):
        ped = self._make_pedido(status='4')
        self.assertIn('Recebido', str(ped))

    def test_format_data_entrega(self):
        ped = self._make_pedido(data_entrega='2024-08-15')
        self.assertEqual(ped.format_data_entrega, '15/08/2024')

    def test_edit_url_contiene_pk(self):
        ped = self._make_pedido()
        self.assertIn('20', str(ped.edit_url()))


# ─────────────────────────────────────────────
# MODELOS — ItensCompra (métodos format_*)
# ─────────────────────────────────────────────

class ItensCompraFormatMethodsTestCase(TestCase):

    def _make_item(self, quantidade='2.00', valor_unit='50.00',
                   tipo_desconto='0', desconto='5.00', subtotal='95.00',
                   vicms='3.00', vipi='2.00'):
        from djangosige.apps.compras.models import ItensCompra
        item = ItensCompra.__new__(ItensCompra)
        item.quantidade = Decimal(quantidade)
        item.valor_unit = Decimal(valor_unit)
        item.tipo_desconto = tipo_desconto
        item.desconto = Decimal(desconto)
        item.subtotal = Decimal(subtotal)
        item.vicms = Decimal(vicms) if vicms else None
        item.vipi = Decimal(vipi) if vipi else None
        return item

    def test_format_quantidade(self):
        item = self._make_item(quantidade='3.00')
        self.assertIn('3', item.format_quantidade())

    def test_format_valor_unit(self):
        item = self._make_item(valor_unit='50.00')
        self.assertIn('50', item.format_valor_unit())

    def test_format_total(self):
        item = self._make_item(subtotal='95.00')
        self.assertIn('95', item.format_total())

    def test_format_vprod(self):
        item = self._make_item(quantidade='2.00', valor_unit='50.00')
        self.assertIn('100', item.format_vprod())

    def test_format_desconto_tipo_fijo(self):
        item = self._make_item(tipo_desconto='0', desconto='5.00')
        self.assertIn('5', item.format_desconto())

    def test_format_desconto_tipo_porcentaje(self):
        item = self._make_item(tipo_desconto='1', desconto='20.00', subtotal='80.00')
        self.assertIn('20', item.format_desconto())

    def test_format_total_impostos(self):
        item = self._make_item(vicms='3.00', vipi='2.00')
        self.assertIn('5', item.format_total_impostos())

    def test_format_total_com_imposto(self):
        item = self._make_item(subtotal='95.00', vicms='3.00', vipi='2.00')
        self.assertIn('100', item.format_total_com_imposto())

    def test_format_valor_attr_existente(self):
        item = self._make_item(vicms='7.00')
        self.assertIn('7', item.format_valor_attr('vicms'))

    def test_format_valor_attr_none_retorna_none(self):
        item = self._make_item(vicms=None)
        self.assertIsNone(item.format_valor_attr('vicms'))