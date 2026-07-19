# -*- coding: utf-8 -*-
"""
Pruebas — módulo estoque (modelos)

Dos estrategias combinadas:
1. Pruebas de integración con BD real (django.test.TestCase) — señal pre_delete
2. Pruebas unitarias en memoria (unittest.TestCase + mocks) — métodos y propiedades
"""

import datetime
import operator
from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase as DjangoTestCase
from unittest import TestCase


# ─────────────────────────────────────────────
# INTEGRACIÓN CON BD — señal pre_delete real
# ─────────────────────────────────────────────

class MovimentoEstoqueSignalIntegracaoTestCase(DjangoTestCase):
    """
    Prueba que la señal pre_delete reajusta correctamente el stock
    usando base de datos real.
    """

    def test_saida_estoque_delete_suma_estoque(self):
        """Al eliminar una SaidaEstoque, el stock debe incrementarse."""
        from djangosige.apps.cadastro.models import Produto
        from djangosige.apps.estoque.models import LocalEstoque, ItensMovimento, SaidaEstoque

        produto = Produto.objects.create(
            codigo="123", descricao="produto", estoque_atual=100)
        local = LocalEstoque.objects.create(descricao="localTeste")
        produto_estocado = local.local_produto_estocado.create(
            produto=produto, quantidade=100)
        mov = SaidaEstoque.objects.create(local_orig=local, quantidade_itens=50)
        ItensMovimento.objects.create(produto=produto, movimento_id=mov, quantidade=50)

        mov.delete()

        produto.refresh_from_db()
        produto_estocado.refresh_from_db()
        self.assertEqual(int(produto.estoque_atual), 150)
        self.assertEqual(int(produto_estocado.quantidade), 150)

    def test_entrada_estoque_delete_resta_estoque(self):
        """Al eliminar una EntradaEstoque, el stock debe decrementarse."""
        from djangosige.apps.cadastro.models import Produto
        from djangosige.apps.estoque.models import LocalEstoque, ItensMovimento, EntradaEstoque

        produto = Produto.objects.create(
            codigo="123", descricao="produto", estoque_atual=100)
        local = LocalEstoque.objects.create(descricao="localTeste")
        produto_estocado = local.local_produto_estocado.create(
            produto=produto, quantidade=100)
        mov = EntradaEstoque.objects.create(local_dest=local, quantidade_itens=50)
        ItensMovimento.objects.create(produto=produto, movimento_id=mov, quantidade=50)

        mov.delete()

        produto.refresh_from_db()
        produto_estocado.refresh_from_db()
        self.assertEqual(int(produto.estoque_atual), 50)
        self.assertEqual(int(produto_estocado.quantidade), 50)


# ─────────────────────────────────────────────
# UNITARIO — LocalEstoque
# ─────────────────────────────────────────────

class LocalEstoqueStrTestCase(TestCase):
    """Verifica representaciones string de LocalEstoque."""

    def test_str_retorna_descricao(self):
        from djangosige.apps.estoque.models import LocalEstoque
        local = LocalEstoque.__new__(LocalEstoque)
        local.descricao = 'Depósito Central'
        self.assertEqual(str(local), 'Depósito Central')

    def test_unicode_retorna_descricao(self):
        from djangosige.apps.estoque.models import LocalEstoque
        local = LocalEstoque.__new__(LocalEstoque)
        local.descricao = 'Almoxarifado'
        self.assertEqual(local.__unicode__(), 'Almoxarifado')

    def test_str_con_descricao_vacia(self):
        from djangosige.apps.estoque.models import LocalEstoque
        local = LocalEstoque.__new__(LocalEstoque)
        local.descricao = ''
        self.assertEqual(str(local), '')


class DEFAULT_LOCAL_ID_TestCase(TestCase):
    """Verifica que la constante DEFAULT_LOCAL_ID sea 1."""

    def test_default_local_id_es_1(self):
        from djangosige.apps.estoque.models import DEFAULT_LOCAL_ID
        self.assertEqual(DEFAULT_LOCAL_ID, 1)


# ─────────────────────────────────────────────
# UNITARIO — ItensMovimento
# ─────────────────────────────────────────────

class ItensMovimentoGetEstoqueAtualTestCase(TestCase):
    """Prueba el método get_estoque_atual_produto de ItensMovimento."""

    def _make_item(self, controlar=True, estoque_atual=None):
        from djangosige.apps.estoque.models import ItensMovimento
        from django.db.models.base import ModelState
        item = ItensMovimento.__new__(ItensMovimento)
        item._state = ModelState()
        produto = MagicMock()
        produto.controlar_estoque = controlar
        produto.estoque_atual = estoque_atual
        item._state.fields_cache = {'produto': produto}
        return item

    def test_retorna_estoque_atual_quando_controlado(self):
        item = self._make_item(controlar=True, estoque_atual=Decimal('10.00'))
        self.assertEqual(item.get_estoque_atual_produto(), Decimal('10.00'))

    def test_retorna_nao_controlado_quando_nao_controla_estoque(self):
        item = self._make_item(controlar=False, estoque_atual=None)
        self.assertEqual(item.get_estoque_atual_produto(), 'No controlado')

    def test_retorna_nao_controlado_quando_estoque_atual_none(self):
        item = self._make_item(controlar=True, estoque_atual=None)
        self.assertEqual(item.get_estoque_atual_produto(), 'No controlado')

    def test_retorna_none_quando_produto_none(self):
        from djangosige.apps.estoque.models import ItensMovimento
        from django.db.models.base import ModelState
        item = ItensMovimento.__new__(ItensMovimento)
        item._state = ModelState()
        item._state.fields_cache = {'produto': None}
        self.assertIsNone(item.get_estoque_atual_produto())


class ItensMovimentoFormatEstoqueAtualTestCase(TestCase):
    """Prueba el método format_estoque_atual_produto."""

    def _make_item(self, controlar=True, estoque_atual=None):
        from djangosige.apps.estoque.models import ItensMovimento
        from django.db.models.base import ModelState
        item = ItensMovimento.__new__(ItensMovimento)
        item._state = ModelState()
        produto = MagicMock()
        produto.controlar_estoque = controlar
        produto.estoque_atual = estoque_atual
        item._state.fields_cache = {'produto': produto}
        return item

    def test_format_retorna_string_decimal_cuando_controlado(self):
        item = self._make_item(controlar=True, estoque_atual=Decimal('25.50'))
        resultado = item.format_estoque_atual_produto()
        self.assertIsInstance(resultado, str)
        self.assertIn('25', resultado)

    def test_format_retorna_nao_controlado_string(self):
        item = self._make_item(controlar=False)
        self.assertEqual(item.format_estoque_atual_produto(), 'No controlado')


# ─────────────────────────────────────────────
# UNITARIO — MovimentoEstoque (formato)
# ─────────────────────────────────────────────

class MovimentoEstoqueFormatTestCase(TestCase):
    """Prueba los métodos de formato de MovimentoEstoque."""

    def _make_movimento(self, quantidade_itens=5, valor_total=Decimal('100.00')):
        from djangosige.apps.estoque.models import MovimentoEstoque
        mov = MovimentoEstoque.__new__(MovimentoEstoque)
        mov.quantidade_itens = quantidade_itens
        mov.valor_total = valor_total
        return mov

    def test_format_quantidade_itens_retorna_string(self):
        mov = self._make_movimento(quantidade_itens=3)
        resultado = mov.format_quantidade_itens()
        self.assertIsInstance(resultado, str)
        self.assertIn('3', resultado)

    def test_format_valor_total_retorna_string(self):
        mov = self._make_movimento(valor_total=Decimal('250.75'))
        resultado = mov.format_valor_total()
        self.assertIsInstance(resultado, str)
        self.assertIn('250', resultado)

    def test_format_data_movimento(self):
        from djangosige.apps.estoque.models import MovimentoEstoque
        mov = MovimentoEstoque.__new__(MovimentoEstoque)
        mov.data_movimento = datetime.date(2024, 7, 16)
        self.assertEqual(mov.format_data_movimento, '16/07/2024')

    def test_format_valor_total_cero(self):
        mov = self._make_movimento(valor_total=Decimal('0.00'))
        self.assertIn('0', mov.format_valor_total())


# ─────────────────────────────────────────────
# UNITARIO — EntradaEstoque
# ─────────────────────────────────────────────

class EntradaEstoqueGetTipoTestCase(TestCase):

    def test_get_tipo_retorna_entrada(self):
        from djangosige.apps.estoque.models import EntradaEstoque
        entrada = EntradaEstoque.__new__(EntradaEstoque)
        self.assertEqual(entrada.get_tipo(), 'Entrada')

    def test_get_edit_url_contiene_ruta_correcta(self):
        from djangosige.apps.estoque.models import EntradaEstoque
        entrada = EntradaEstoque.__new__(EntradaEstoque)
        entrada.id = 42
        url = str(entrada.get_edit_url())
        self.assertIn('editarentrada', url)
        self.assertIn('42', url)


# ─────────────────────────────────────────────
# UNITARIO — SaidaEstoque
# ─────────────────────────────────────────────

class SaidaEstoqueGetTipoTestCase(TestCase):

    def test_get_tipo_retorna_saida(self):
        from djangosige.apps.estoque.models import SaidaEstoque
        saida = SaidaEstoque.__new__(SaidaEstoque)
        self.assertEqual(saida.get_tipo(), 'Salida')

    def test_get_edit_url_contiene_ruta_correcta(self):
        from djangosige.apps.estoque.models import SaidaEstoque
        saida = SaidaEstoque.__new__(SaidaEstoque)
        saida.id = 7
        url = str(saida.get_edit_url())
        self.assertIn('editarsaida', url)
        self.assertIn('7', url)


# ─────────────────────────────────────────────
# UNITARIO — TransferenciaEstoque
# ─────────────────────────────────────────────

class TransferenciaEstoqueGetTipoTestCase(TestCase):

    def test_get_tipo_retorna_transferencia(self):
        from djangosige.apps.estoque.models import TransferenciaEstoque
        transf = TransferenciaEstoque.__new__(TransferenciaEstoque)
        self.assertEqual(transf.get_tipo(), 'Transferencia')

    def test_get_edit_url_contiene_ruta_correcta(self):
        from djangosige.apps.estoque.models import TransferenciaEstoque
        transf = TransferenciaEstoque.__new__(TransferenciaEstoque)
        transf.id = 15
        url = str(transf.get_edit_url())
        self.assertIn('editartransferencia', url)
        self.assertIn('15', url)
