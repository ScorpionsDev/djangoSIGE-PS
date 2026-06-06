# -*- coding: utf-8 -*-
"""
Pruebas UNITARIAS — módulo vendas (SOLO modelos)

Estrategia de aislamiento:
- Se instancian objetos de modelo en memoria sin guardar en BD (sin .save()).
- No se usa self.client (sin peticiones HTTP).
- No se hereda de BaseTestCase.
- Los métodos que dependen de FK o BD se omiten o mockean con unittest.mock.
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock
from decimal import Decimal


# ─────────────────────────────────────────────
# CONSTANTES / CHOICES
# ─────────────────────────────────────────────

class ChoicesVendasTestCase(TestCase):
    """Verifica que las constantes de choices estén definidas correctamente."""

    def test_status_orcamento_escolhas(self):
        from djangosige.apps.vendas.models.vendas import STATUS_ORCAMENTO_ESCOLHAS
        codigos = [c[0] for c in STATUS_ORCAMENTO_ESCOLHAS]
        self.assertIn('0', codigos)  # Aberto
        self.assertIn('1', codigos)  # Baixado
        self.assertIn('2', codigos)  # Cancelado

    def test_status_pedido_venda_escolhas(self):
        from djangosige.apps.vendas.models.vendas import STATUS_PEDIDO_VENDA_ESCOLHAS
        codigos = [c[0] for c in STATUS_PEDIDO_VENDA_ESCOLHAS]
        self.assertIn('0', codigos)  # Aberto
        self.assertIn('1', codigos)  # Faturado
        self.assertIn('2', codigos)  # Cancelado
        self.assertIn('3', codigos)  # Importado por XML

    def test_tipos_desconto_escolhas(self):
        from djangosige.apps.vendas.models.vendas import TIPOS_DESCONTO_ESCOLHAS
        codigos = [c[0] for c in TIPOS_DESCONTO_ESCOLHAS]
        self.assertIn('0', codigos)  # Valor
        self.assertIn('1', codigos)  # Percentual

    def test_mod_frete_escolhas(self):
        from djangosige.apps.vendas.models.vendas import MOD_FRETE_ESCOLHAS
        codigos = [c[0] for c in MOD_FRETE_ESCOLHAS]
        self.assertIn('0', codigos)
        self.assertIn('9', codigos)  # Sem frete

    def test_formas_pag_escolhas(self):
        from djangosige.apps.vendas.models.pagamento import FORMAS_PAG_ESCOLHAS
        codigos = [c[0] for c in FORMAS_PAG_ESCOLHAS]
        self.assertIn('01', codigos)  # Dinheiro
        self.assertIn('99', codigos)  # Outros


# ─────────────────────────────────────────────
# ItensVenda — propiedades y métodos de cálculo
# ─────────────────────────────────────────────

class ItensVendaVprodTestCase(TestCase):
    """Pruebas para la propiedad vprod de ItensVenda."""

    def _make_item(self, quantidade, valor_unit):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.quantidade = Decimal(str(quantidade))
        item.valor_unit = Decimal(str(valor_unit))
        return item

    def test_vprod_calculo_basico(self):
        item = self._make_item(5, '10.00')
        self.assertEqual(item.vprod, Decimal('50.00'))

    def test_vprod_calculo_decimales(self):
        item = self._make_item('2.50', '4.00')
        self.assertEqual(item.vprod, Decimal('10.00'))

    def test_vprod_cantidad_uno(self):
        item = self._make_item(1, '99.99')
        self.assertEqual(item.vprod, Decimal('99.99'))


class ItensVendaDescontoTestCase(TestCase):
    """Pruebas para get_valor_desconto y get_total_sem_desconto."""

    def _make_item(self, subtotal, desconto, tipo_desconto='0'):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.subtotal = Decimal(str(subtotal))
        item.desconto = Decimal(str(desconto))
        item.tipo_desconto = tipo_desconto
        return item

    def test_desconto_tipo_valor(self):
        item = self._make_item('100.00', '10.00', '0')
        self.assertEqual(item.get_valor_desconto(), Decimal('10.00'))

    def test_desconto_tipo_percentual(self):
        # subtotal = 90, desconto = 10%  → total_sem_desc = 100, desconto = 10
        item = self._make_item('90.00', '10.00', '1')
        desconto = item.get_valor_desconto()
        self.assertAlmostEqual(float(desconto), 10.0, places=1)

    def test_total_sem_desconto_tipo_valor(self):
        item = self._make_item('90.00', '10.00', '0')
        self.assertEqual(item.get_total_sem_desconto(), Decimal('100.00'))

    def test_total_sem_desconto_tipo_percentual(self):
        item = self._make_item('90.00', '10.00', '1')
        total = item.get_total_sem_desconto()
        self.assertAlmostEqual(float(total), 100.0, places=1)


class ItensVendaImpostosTestCase(TestCase):
    """Pruebas para get_total_impostos y get_total_com_impostos."""

    def _make_item(self, subtotal, vicms=None, vicms_st=None, vipi=None,
                   vfcp=None, vicmsufdest=None, vicmsufremet=None):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.subtotal = Decimal(str(subtotal))
        item.vicms = Decimal(str(vicms)) if vicms is not None else None
        item.vicms_st = Decimal(str(vicms_st)) if vicms_st is not None else None
        item.vipi = Decimal(str(vipi)) if vipi is not None else None
        item.vfcp = Decimal(str(vfcp)) if vfcp is not None else None
        item.vicmsufdest = Decimal(str(vicmsufdest)) if vicmsufdest is not None else None
        item.vicmsufremet = Decimal(str(vicmsufremet)) if vicmsufremet is not None else None
        return item

    def test_total_impostos_todos_nulos(self):
        item = self._make_item('100.00')
        self.assertEqual(item.get_total_impostos(), 0)

    def test_total_impostos_solo_vicms(self):
        item = self._make_item('100.00', vicms='12.00')
        self.assertEqual(item.get_total_impostos(), Decimal('12.00'))

    def test_total_impostos_multiples(self):
        item = self._make_item('100.00', vicms='12.00', vipi='5.00', vfcp='2.00')
        self.assertEqual(item.get_total_impostos(), Decimal('19.00'))

    def test_total_com_impostos(self):
        item = self._make_item('100.00', vicms='12.00', vipi='5.00')
        self.assertEqual(item.get_total_com_impostos(), Decimal('117.00'))

    def test_total_com_impostos_sin_impuestos(self):
        item = self._make_item('200.00')
        self.assertEqual(item.get_total_com_impostos(), Decimal('200.00'))


class ItensVendaFormatTestCase(TestCase):
    """Pruebas para los métodos format_* de ItensVenda."""

    def _make_item(self):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.quantidade = Decimal('3.00')
        item.valor_unit = Decimal('10.00')
        item.subtotal = Decimal('30.00')
        item.desconto = Decimal('0.00')
        item.tipo_desconto = '0'
        item.vicms = Decimal('3.60')
        item.vicms_st = None
        item.vipi = None
        item.vfcp = None
        item.vicmsufdest = None
        item.vicmsufremet = None
        return item

    def test_format_quantidade(self):
        item = self._make_item()
        result = item.format_quantidade()
        self.assertIn('3', result)

    def test_format_valor_unit(self):
        item = self._make_item()
        result = item.format_valor_unit()
        self.assertIn('10', result)

    def test_format_total(self):
        item = self._make_item()
        result = item.format_total()
        self.assertIn('30', result)

    def test_format_vprod(self):
        item = self._make_item()
        result = item.format_vprod()
        self.assertIn('30', result)

    def test_format_total_impostos(self):
        item = self._make_item()
        result = item.format_total_impostos()
        self.assertIn('3', result)

    def test_format_total_com_imposto(self):
        item = self._make_item()
        result = item.format_total_com_imposto()
        self.assertIn('33', result)

    def test_format_desconto(self):
        item = self._make_item()
        result = item.format_desconto()
        self.assertIn('0', result)

    def test_format_valor_attr_existente(self):
        item = self._make_item()
        result = item.format_valor_attr('vicms')
        self.assertIn('3', result)

    def test_format_valor_attr_nulo(self):
        item = self._make_item()
        result = item.format_valor_attr('vipi')
        self.assertIsNone(result)


class ItensVendaVbcUfDestTestCase(TestCase):
    """Prueba la propiedad vbc_uf_dest."""

    def test_vbc_uf_dest(self):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.subtotal = Decimal('100.00')
        item.vipi = Decimal('5.00')
        self.assertEqual(item.vbc_uf_dest, Decimal('105.00'))


# ─────────────────────────────────────────────
# Venda — métodos de cálculo
# ─────────────────────────────────────────────

class VendaMetodosTestCase(TestCase):
    """
    Pruebas para los métodos de Venda que no requieren BD.

    Se llaman los métodos directamente como funciones no ligadas (Venda.metodo(ns))
    pasando un SimpleNamespace como 'self', evitando así los descriptores de FK
    de Django que requieren _state inicializado.
    """

    def _make_ns(self, valor_total, impostos, desconto='0.00', tipo_desconto='0'):
        from types import SimpleNamespace
        ns = SimpleNamespace(
            valor_total=Decimal(str(valor_total)),
            impostos=Decimal(str(impostos)),
            desconto=Decimal(str(desconto)),
            tipo_desconto=tipo_desconto,
            frete=Decimal('0.00'),
            despesas=Decimal('0.00'),
            seguro=Decimal('0.00'),
            cond_pagamento=None,
            local_orig=None,
        )
        ns.get_total_sem_imposto = lambda: ns.valor_total - ns.impostos
        return ns

    def test_get_total_sem_imposto(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('1000.00', '120.00')
        self.assertEqual(Venda.get_total_sem_imposto(ns), Decimal('880.00'))

    def test_get_total_sem_imposto_sin_impuestos(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00')
        self.assertEqual(Venda.get_total_sem_imposto(ns), Decimal('500.00'))

    def test_format_valor_total(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('1500.00', '0.00')
        self.assertIn('1500', Venda.format_valor_total(ns))

    def test_format_frete(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00')
        self.assertIn('0', Venda.format_frete(ns))

    def test_format_impostos(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '50.00')
        self.assertIn('50', Venda.format_impostos(ns))

    def test_format_total_sem_imposto(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '50.00')
        self.assertIn('450', Venda.format_total_sem_imposto(ns))

    def test_format_seguro(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00')
        self.assertIn('0', Venda.format_seguro(ns))

    def test_format_despesas(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00')
        self.assertIn('0', Venda.format_despesas(ns))

    def test_format_desconto_tipo_valor(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00', desconto='20.00', tipo_desconto='0')
        self.assertIn('20', Venda.format_desconto(ns))

    def test_get_forma_pagamento_sin_cond(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00')
        self.assertEqual(Venda.get_forma_pagamento(ns), "")

    def test_get_local_orig_id_sin_local(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00')
        self.assertEqual(Venda.get_local_orig_id(ns), "")

    def test_get_valor_desconto_total_tipo_valor(self):
        from djangosige.apps.vendas.models.vendas import Venda
        ns = self._make_ns('500.00', '0.00', desconto='25.00', tipo_desconto='0')
        self.assertEqual(Venda.get_valor_desconto_total(ns), Decimal('25.00'))

    def test_str(self):
        from djangosige.apps.vendas.models.vendas import Venda
        from types import SimpleNamespace
        ns = SimpleNamespace(id=42)
        self.assertIn('42', Venda.__str__(ns))

    def test_unicode(self):
        from djangosige.apps.vendas.models.vendas import Venda
        from types import SimpleNamespace
        ns = SimpleNamespace(id=7)
        self.assertIn('7', Venda.__unicode__(ns))


class VendaGetValorTotalAttrTestCase(TestCase):
    """
    Prueba get_valor_total_attr iterando sobre itens_venda mockeados.

    Se usa patch.object para reemplazar el related manager de Django sin
    hacer asignación directa, que Django prohíbe en el reverse side de FKs.
    """

    def test_get_valor_total_attr_suma_correctamente(self):
        from djangosige.apps.vendas.models.vendas import Venda

        item1 = MagicMock()
        item1.vicms = Decimal('10.00')
        item2 = MagicMock()
        item2.vicms = Decimal('15.00')

        manager_mock = MagicMock()
        manager_mock.all.return_value = [item1, item2]

        venda = Venda.__new__(Venda)
        with patch.object(type(venda), 'itens_venda',
                          new_callable=lambda: property(lambda self: manager_mock)):
            result = venda.get_valor_total_attr('vicms')

        self.assertEqual(result, Decimal('25.00'))

    def test_get_valor_total_attr_valor_nulo(self):
        from djangosige.apps.vendas.models.vendas import Venda

        item1 = MagicMock()
        item1.vicms = None

        manager_mock = MagicMock()
        manager_mock.all.return_value = [item1]

        venda = Venda.__new__(Venda)
        with patch.object(type(venda), 'itens_venda',
                          new_callable=lambda: property(lambda self: manager_mock)):
            result = venda.get_valor_total_attr('vicms')

        self.assertEqual(result, 0)


# ─────────────────────────────────────────────
# OrcamentoVenda
# ─────────────────────────────────────────────

class OrcamentoVendaTestCase(TestCase):

    def _make_orcamento(self):
        from djangosige.apps.vendas.models.vendas import OrcamentoVenda
        orc = OrcamentoVenda.__new__(OrcamentoVenda)
        orc.id = 1
        orc.status = '0'
        return orc

    def test_status_default(self):
        orc = self._make_orcamento()
        self.assertEqual(orc.status, '0')

    def test_tipo_venda(self):
        orc = self._make_orcamento()
        self.assertEqual(orc.tipo_venda, 'Orçamento')

    def test_str(self):
        orc = self._make_orcamento()
        self.assertIn('1', str(orc))

    def test_unicode(self):
        orc = self._make_orcamento()
        self.assertIn('1', orc.__unicode__())

    def test_edit_url(self):
        orc = self._make_orcamento()
        url = orc.edit_url()
        self.assertIn('1', str(url))


# ─────────────────────────────────────────────
# PedidoVenda
# ─────────────────────────────────────────────

class PedidoVendaTestCase(TestCase):

    def _make_pedido(self):
        from djangosige.apps.vendas.models.vendas import PedidoVenda
        ped = PedidoVenda.__new__(PedidoVenda)
        ped.id = 5
        ped.status = '0'
        return ped

    def test_status_default(self):
        ped = self._make_pedido()
        self.assertEqual(ped.status, '0')

    def test_tipo_venda(self):
        ped = self._make_pedido()
        self.assertEqual(ped.tipo_venda, 'Pedido')

    def test_str(self):
        ped = self._make_pedido()
        ped.get_status_display = lambda: 'Aberto'
        self.assertIn('5', str(ped))

    def test_unicode(self):
        ped = self._make_pedido()
        ped.get_status_display = lambda: 'Aberto'
        self.assertIn('5', ped.__unicode__())

    def test_edit_url(self):
        ped = self._make_pedido()
        url = ped.edit_url()
        self.assertIn('5', str(url))


# ─────────────────────────────────────────────
# Pagamento (vendas)
# ─────────────────────────────────────────────

class PagamentoVendaModelTestCase(TestCase):

    def _make_pagamento(self, valor='250.00', vencimento_str='2024-07-31'):
        from djangosige.apps.vendas.models.pagamento import Pagamento
        from datetime import date
        pag = Pagamento.__new__(Pagamento)
        pag.valor_parcela = Decimal(valor)
        pag.vencimento = date(2024, 7, 31)
        pag.indice_parcela = 1
        return pag

    def test_format_valor_parcela(self):
        pag = self._make_pagamento('250.00')
        result = pag.format_valor_parcela
        self.assertIn('250', result)

    def test_format_vencimento(self):
        pag = self._make_pagamento()
        result = pag.format_vencimento
        self.assertEqual(result, '31/07/2024')


# ─────────────────────────────────────────────
# CondicaoPagamento
# ─────────────────────────────────────────────

class CondicaoPagamentoTestCase(TestCase):

    def _make_cond(self, descricao='À Vista', forma='01', n_parcelas=1):
        from djangosige.apps.vendas.models.pagamento import CondicaoPagamento
        cond = CondicaoPagamento.__new__(CondicaoPagamento)
        cond.descricao = descricao
        cond.forma = forma
        cond.n_parcelas = n_parcelas
        cond.dias_recorrencia = 0
        cond.parcela_inicial = 0
        return cond

    def test_str(self):
        cond = self._make_cond('30/60/90')
        self.assertEqual(str(cond), '30/60/90')

    def test_unicode(self):
        cond = self._make_cond('À Vista')
        self.assertEqual(cond.__unicode__(), 'À Vista')


# ─────────────────────────────────────────────
# ItensVenda — vicms_cred_sn (líneas 127-134)
# ─────────────────────────────────────────────

class ItensVendaVicmsCredSnTestCase(TestCase):

    def _make_item(self):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.subtotal = Decimal('100.00')
        return item

    def test_vicms_cred_sn_con_p_cred_sn(self):
        item = self._make_item()
        icms_mock = MagicMock()
        icms_mock.p_cred_sn = Decimal('10.00')
        grupo_fiscal_mock = MagicMock()
        grupo_fiscal_mock.icms_sn_padrao.get.return_value = icms_mock
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = grupo_fiscal_mock
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)):
            result = item.vicms_cred_sn
        self.assertEqual(result, Decimal('10.00'))

    def test_vicms_cred_sn_sin_p_cred_sn(self):
        item = self._make_item()
        icms_mock = MagicMock()
        icms_mock.p_cred_sn = None
        grupo_fiscal_mock = MagicMock()
        grupo_fiscal_mock.icms_sn_padrao.get.return_value = icms_mock
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = grupo_fiscal_mock
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)):
            result = item.vicms_cred_sn
        self.assertEqual(result, '')

    def test_vicms_cred_sn_excepcion(self):
        item = self._make_item()
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal.icms_sn_padrao.get.side_effect = Exception('error')
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)):
            result = item.vicms_cred_sn
        self.assertEqual(result, '')


# ─────────────────────────────────────────────
# ItensVenda — get_mot_deson_icms (líneas 167-174)
# ─────────────────────────────────────────────

class ItensVendaMotDesonTestCase(TestCase):

    def _make_item(self):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        return item

    def test_get_mot_deson_icms_con_valor(self):
        item = self._make_item()
        icms_mock = MagicMock()
        icms_mock.mot_des_icms = '3'
        icms_mock.get_mot_des_icms_display.return_value = 'Uso e Consumo'
        grupo_fiscal_mock = MagicMock()
        grupo_fiscal_mock.icms_padrao.get.return_value = icms_mock
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = grupo_fiscal_mock
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)):
            result = item.get_mot_deson_icms()
        self.assertEqual(result, 'Uso e Consumo')

    def test_get_mot_deson_icms_sin_valor(self):
        item = self._make_item()
        icms_mock = MagicMock()
        icms_mock.mot_des_icms = None
        grupo_fiscal_mock = MagicMock()
        grupo_fiscal_mock.icms_padrao.get.return_value = icms_mock
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = grupo_fiscal_mock
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)):
            result = item.get_mot_deson_icms()
        self.assertEqual(result, '')

    def test_get_mot_deson_icms_excepcion(self):
        item = self._make_item()
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal.icms_padrao.get.side_effect = Exception('error')
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)):
            result = item.get_mot_deson_icms()
        self.assertEqual(result, '')


# ─────────────────────────────────────────────
# ItensVenda — get_aliquota_pis (líneas 195-211)
# ─────────────────────────────────────────────

class ItensVendaAliquotaPisTestCase(TestCase):

    def _make_item(self):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.quantidade = Decimal('2.00')
        item.subtotal = Decimal('100.00')
        return item

    def test_get_aliquota_pis_valiq_format_true(self):
        item = self._make_item()
        pis_mock = MagicMock()
        pis_mock.valiq_pis = Decimal('1.50')
        pis_mock.p_pis = None
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', return_value=pis_mock):
            result = item.get_aliquota_pis(format=True)
        self.assertIn('1', result)

    def test_get_aliquota_pis_valiq_format_false(self):
        item = self._make_item()
        pis_mock = MagicMock()
        pis_mock.valiq_pis = Decimal('1.50')
        pis_mock.p_pis = None
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', return_value=pis_mock):
            result = item.get_aliquota_pis(format=False)
        self.assertEqual(result, Decimal('1.50'))

    def test_get_aliquota_pis_p_pis_format_true(self):
        item = self._make_item()
        pis_mock = MagicMock()
        pis_mock.valiq_pis = None
        pis_mock.p_pis = Decimal('0.65')
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', return_value=pis_mock):
            result = item.get_aliquota_pis(format=True)
        self.assertIn('0', result)

    def test_get_aliquota_pis_p_pis_format_false(self):
        item = self._make_item()
        pis_mock = MagicMock()
        pis_mock.valiq_pis = None
        pis_mock.p_pis = Decimal('0.65')
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', return_value=pis_mock):
            result = item.get_aliquota_pis(format=False)
        self.assertEqual(result, Decimal('0.65'))

    def test_get_aliquota_pis_does_not_exist(self):
        from djangosige.apps.fiscal.models import PIS
        item = self._make_item()
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', side_effect=PIS.DoesNotExist):
            result = item.get_aliquota_pis()
        self.assertIsNone(result)


# ─────────────────────────────────────────────
# ItensVenda — get_aliquota_cofins (líneas 214-230)
# ─────────────────────────────────────────────

class ItensVendaAliquotaCofinsTestCase(TestCase):

    def _make_item(self):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.quantidade = Decimal('2.00')
        item.subtotal = Decimal('100.00')
        return item

    def test_get_aliquota_cofins_valiq_format_true(self):
        item = self._make_item()
        cofins_mock = MagicMock()
        cofins_mock.valiq_cofins = Decimal('3.00')
        cofins_mock.p_cofins = None
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', return_value=cofins_mock):
            result = item.get_aliquota_cofins(format=True)
        self.assertIn('3', result)

    def test_get_aliquota_cofins_valiq_format_false(self):
        item = self._make_item()
        cofins_mock = MagicMock()
        cofins_mock.valiq_cofins = Decimal('3.00')
        cofins_mock.p_cofins = None
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', return_value=cofins_mock):
            result = item.get_aliquota_cofins(format=False)
        self.assertEqual(result, Decimal('3.00'))

    def test_get_aliquota_cofins_p_cofins_format_true(self):
        item = self._make_item()
        cofins_mock = MagicMock()
        cofins_mock.valiq_cofins = None
        cofins_mock.p_cofins = Decimal('3.00')
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', return_value=cofins_mock):
            result = item.get_aliquota_cofins(format=True)
        self.assertIn('3', result)

    def test_get_aliquota_cofins_p_cofins_format_false(self):
        item = self._make_item()
        cofins_mock = MagicMock()
        cofins_mock.valiq_cofins = None
        cofins_mock.p_cofins = Decimal('3.00')
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', return_value=cofins_mock):
            result = item.get_aliquota_cofins(format=False)
        self.assertEqual(result, Decimal('3.00'))

    def test_get_aliquota_cofins_does_not_exist(self):
        from djangosige.apps.fiscal.models import COFINS
        item = self._make_item()
        produto_mock = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', side_effect=COFINS.DoesNotExist):
            result = item.get_aliquota_cofins()
        self.assertIsNone(result)


# ─────────────────────────────────────────────
# ItensVenda — calcular_pis_cofins (líneas 233-264)
# ─────────────────────────────────────────────

class ItensVendaCalcularPisCofinsTestCase(TestCase):

    def _make_item(self, subtotal='100.00', quantidade='2.00',
                   desconto=None, valor_rateio_despesas=None):
        from djangosige.apps.vendas.models.vendas import ItensVenda
        item = ItensVenda.__new__(ItensVenda)
        item.subtotal = Decimal(subtotal)
        item.quantidade = Decimal(quantidade)
        item.desconto = Decimal(str(desconto)) if desconto is not None else None
        item.valor_rateio_despesas = Decimal(str(valor_rateio_despesas)) if valor_rateio_despesas is not None else None
        item.vpis = None
        item.vcofins = None
        item.vq_bcpis = None
        item.vq_bccofins = None
        return item

    def test_calcular_pis_cofins_con_valiq(self):
        item = self._make_item()
        pis_mock = MagicMock()
        pis_mock.valiq_pis = Decimal('1.00')
        pis_mock.p_pis = None
        cofins_mock = MagicMock()
        cofins_mock.valiq_cofins = Decimal('2.00')
        cofins_mock.p_cofins = None
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', return_value=pis_mock), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', return_value=cofins_mock):
            item.calcular_pis_cofins()
        self.assertEqual(item.vpis, Decimal('2.00'))
        self.assertEqual(item.vcofins, Decimal('4.00'))

    def test_calcular_pis_cofins_con_percentual(self):
        item = self._make_item()
        pis_mock = MagicMock()
        pis_mock.valiq_pis = None
        pis_mock.p_pis = Decimal('0.65')
        cofins_mock = MagicMock()
        cofins_mock.valiq_cofins = None
        cofins_mock.p_cofins = Decimal('3.00')
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', return_value=pis_mock), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', return_value=cofins_mock):
            item.calcular_pis_cofins()
        self.assertAlmostEqual(float(item.vpis), 0.65, places=2)
        self.assertAlmostEqual(float(item.vcofins), 3.00, places=2)

    def test_calcular_pis_cofins_con_despesas_y_desconto(self):
        item = self._make_item(desconto='5.00', valor_rateio_despesas='10.00')
        pis_mock = MagicMock()
        pis_mock.valiq_pis = None
        pis_mock.p_pis = Decimal('1.00')
        cofins_mock = MagicMock()
        cofins_mock.valiq_cofins = None
        cofins_mock.p_cofins = Decimal('1.00')
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', return_value=pis_mock), \
             patch('djangosige.apps.vendas.models.vendas.COFINS.objects.get', return_value=cofins_mock):
            item.calcular_pis_cofins()
        # vbc = 100 + 10 - 5 = 105; vpis = 105 * 1/100 = 1.05
        self.assertAlmostEqual(float(item.vpis), 1.05, places=2)

    def test_calcular_pis_cofins_does_not_exist(self):
        from djangosige.apps.fiscal.models import PIS
        item = self._make_item()
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = MagicMock()
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)), \
             patch('djangosige.apps.vendas.models.vendas.PIS.objects.get', side_effect=PIS.DoesNotExist):
            item.calcular_pis_cofins()
        self.assertIsNone(item.vpis)

    def test_calcular_pis_cofins_sin_grupo_fiscal(self):
        item = self._make_item()
        produto_mock = MagicMock()
        produto_mock.grupo_fiscal = None
        with patch.object(type(item), 'produto',
                          new_callable=lambda: property(lambda self: produto_mock)):
            item.calcular_pis_cofins()
        self.assertIsNone(item.vpis)


# ─────────────────────────────────────────────
# Venda — get_total_produtos (líneas 309-313)
# ─────────────────────────────────────────────

class VendaGetTotalProdutosTestCase(TestCase):

    def test_get_total_produtos(self):
        from djangosige.apps.vendas.models.vendas import Venda
        item1 = MagicMock()
        item1.vprod = Decimal('50.00')
        item2 = MagicMock()
        item2.vprod = Decimal('30.00')
        venda = Venda.__new__(Venda)
        venda.id = 1
        with patch('djangosige.apps.vendas.models.vendas.ItensVenda.objects.filter',
                   return_value=[item1, item2]):
            result = venda.get_total_produtos()
        self.assertEqual(result, Decimal('80.00'))

    def test_format_total_produtos(self):
        from djangosige.apps.vendas.models.vendas import Venda
        venda = Venda.__new__(Venda)
        venda.id = 1
        item1 = MagicMock()
        item1.vprod = Decimal('200.00')
        with patch('djangosige.apps.vendas.models.vendas.ItensVenda.objects.filter',
                   return_value=[item1]):
            result = venda.format_total_produtos()
        self.assertIn('200', result)


# ─────────────────────────────────────────────
# Venda — get_total_produtos_estoque (líneas 316-321)
# ─────────────────────────────────────────────

class VendaGetTotalProdutosEstoqueTestCase(TestCase):

    def test_get_total_produtos_estoque_solo_controlados(self):
        from djangosige.apps.vendas.models.vendas import Venda

        item1 = MagicMock()
        item1.produto.controlar_estoque = True
        item1.vprod = Decimal('40.00')

        item2 = MagicMock()
        item2.produto.controlar_estoque = False
        item2.vprod = Decimal('20.00')

        manager_mock = MagicMock()
        manager_mock.all.return_value = [item1, item2]

        venda = Venda.__new__(Venda)
        with patch.object(type(venda), 'itens_venda',
                          new_callable=lambda: property(lambda self: manager_mock)):
            result = venda.get_total_produtos_estoque()

        self.assertEqual(result, Decimal('40.00'))


# ─────────────────────────────────────────────
# Venda — format_data_emissao (línea 328)
# ─────────────────────────────────────────────

class VendaFormatDataEmissaoTestCase(TestCase):

    def test_format_data_emissao(self):
        from djangosige.apps.vendas.models.vendas import Venda
        from datetime import date
        venda = Venda.__new__(Venda)
        venda.data_emissao = date(2024, 7, 15)
        result = venda.format_data_emissao
        self.assertIn('15', result)
        self.assertIn('07', result)
        self.assertIn('2024', result)


# ─────────────────────────────────────────────
# Venda — get_valor_desconto_total rama percentual (líneas 334-336)
# ─────────────────────────────────────────────

class VendaGetValorDescontoTotalPercentualTestCase(TestCase):

    def test_get_valor_desconto_total_tipo_percentual(self):
        from djangosige.apps.vendas.models.vendas import Venda
        from types import SimpleNamespace
        ns = SimpleNamespace(
            tipo_desconto='1',
            desconto=Decimal('10.00'),
        )
        # get_total_sem_desconto no existe en Venda directamente,
        # se mockea como callable en el namespace
        ns.get_total_sem_desconto = lambda: Decimal('500.00')
        result = Venda.get_valor_desconto_total(ns)
        self.assertEqual(result, Decimal('50.00'))


# ─────────────────────────────────────────────
# Venda — format_desconto rama percentual (líneas 354-360)
# ─────────────────────────────────────────────

class VendaFormatDescontoPercentualTestCase(TestCase):

    def test_format_desconto_tipo_percentual(self):
        from djangosige.apps.vendas.models.vendas import Venda

        item1 = MagicMock()
        item1.get_total_sem_desconto.return_value = Decimal('200.00')
        item2 = MagicMock()
        item2.get_total_sem_desconto.return_value = Decimal('300.00')

        venda = Venda.__new__(Venda)
        venda.id = 1
        venda.tipo_desconto = '1'
        venda.desconto = Decimal('10.00')  # 10%

        with patch('djangosige.apps.vendas.models.vendas.ItensVenda.objects.filter',
                   return_value=[item1, item2]):
            result = venda.format_desconto()
        # total = 500, desconto 10% = 50
        self.assertIn('50', result)


# ─────────────────────────────────────────────
# Venda — format_total_sem_desconto (líneas 369-370)
# ─────────────────────────────────────────────

class VendaFormatTotalSemDescontoTestCase(TestCase):

    def test_format_total_sem_desconto(self):
        from djangosige.apps.vendas.models.vendas import Venda
        from types import SimpleNamespace
        ns = SimpleNamespace(
            valor_total=Decimal('1000.00'),
            desconto=Decimal('100.00'),
        )
        result = Venda.format_total_sem_desconto(ns)
        self.assertIn('900', result)


# ─────────────────────────────────────────────
# Venda — get_forma_pagamento con cond_pagamento (línea 374)
# ─────────────────────────────────────────────

class VendaGetFormaPagamentoComCondTestCase(TestCase):

    def test_get_forma_pagamento_con_cond(self):
        from djangosige.apps.vendas.models.vendas import Venda
        from types import SimpleNamespace
        cond_mock = MagicMock()
        cond_mock.get_forma_display.return_value = 'Dinheiro'
        ns = SimpleNamespace(cond_pagamento=cond_mock)
        result = Venda.get_forma_pagamento(ns)
        self.assertEqual(result, 'Dinheiro')


# ─────────────────────────────────────────────
# Venda — get_local_orig_id con local_orig (línea 380)
# ─────────────────────────────────────────────

class VendaGetLocalOrigIdComLocalTestCase(TestCase):

    def test_get_local_orig_id_con_local(self):
        from djangosige.apps.vendas.models.vendas import Venda
        from types import SimpleNamespace
        local_mock = MagicMock()
        local_mock.id = 99
        ns = SimpleNamespace(local_orig=local_mock)
        result = Venda.get_local_orig_id(ns)
        self.assertEqual(result, 99)


# ─────────────────────────────────────────────
# Venda — get_child (líneas 394-397)
# ─────────────────────────────────────────────

class VendaGetChildTestCase(TestCase):

    def test_get_child_retorna_pedido(self):
        from djangosige.apps.vendas.models.vendas import Venda, PedidoVenda
        venda = Venda.__new__(Venda)
        venda.id = 10
        pedido_mock = MagicMock(spec=PedidoVenda)
        with patch.object(PedidoVenda.objects, 'get', return_value=pedido_mock):
            result = venda.get_child()
        self.assertEqual(result, pedido_mock)

    def test_get_child_retorna_orcamento(self):
        from djangosige.apps.vendas.models.vendas import Venda, PedidoVenda, OrcamentoVenda
        venda = Venda.__new__(Venda)
        venda.id = 10
        orcamento_mock = MagicMock(spec=OrcamentoVenda)
        with patch.object(PedidoVenda.objects, 'get', side_effect=PedidoVenda.DoesNotExist), \
             patch.object(OrcamentoVenda.objects, 'get', return_value=orcamento_mock):
            result = venda.get_child()
        self.assertEqual(result, orcamento_mock)


# ─────────────────────────────────────────────
# OrcamentoVenda — format_data_vencimento (línea 418)
# ─────────────────────────────────────────────

class OrcamentoVendaFormatDataVencimentoTestCase(TestCase):

    def test_format_data_vencimento(self):
        from djangosige.apps.vendas.models.vendas import OrcamentoVenda
        from datetime import date
        orc = OrcamentoVenda.__new__(OrcamentoVenda)
        orc.data_vencimento = date(2024, 12, 31)
        result = orc.format_data_vencimento
        self.assertIn('31', result)
        self.assertIn('12', result)
        self.assertIn('2024', result)


# ─────────────────────────────────────────────
# PedidoVenda — format_data_entrega (línea 451)
# ─────────────────────────────────────────────

class PedidoVendaFormatDataEntregaTestCase(TestCase):

    def test_format_data_entrega(self):
        from djangosige.apps.vendas.models.vendas import PedidoVenda
        from datetime import date
        ped = PedidoVenda.__new__(PedidoVenda)
        ped.data_entrega = date(2024, 8, 20)
        result = ped.format_data_entrega
        self.assertIn('20', result)
        self.assertIn('08', result)
        self.assertIn('2024', result)
