# -*- coding: utf-8 -*-
"""
Pruebas UNITARIAS — módulo estoque (SOLO formularios)

Estrategia de aislamiento:
- Los formularios se prueban con datos en memoria.
- No se usa self.client (sin peticiones HTTP).
- No se hereda de BaseTestCase.
"""

from unittest import TestCase


# ─────────────────────────────────────────────
# FORMULARIOS — LocalEstoqueForm
# ─────────────────────────────────────────────

class LocalEstoqueFormTestCase(TestCase):

    def test_campo_descricao_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import LocalEstoqueForm
        form = LocalEstoqueForm()
        widget_attrs = form.fields['descricao'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_form_invalido_sin_descricao(self):
        from djangosige.apps.estoque.forms import LocalEstoqueForm
        form = LocalEstoqueForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('descricao', form.errors)

    def test_form_valido_con_descricao(self):
        from djangosige.apps.estoque.forms import LocalEstoqueForm
        form = LocalEstoqueForm(data={'descricao': 'Depósito A'})
        self.assertTrue(form.is_valid())

    def test_form_invalido_descricao_vacia(self):
        from djangosige.apps.estoque.forms import LocalEstoqueForm
        form = LocalEstoqueForm(data={'descricao': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('descricao', form.errors)


# ─────────────────────────────────────────────
# FORMULARIOS — MovimentoForm (base)
# ─────────────────────────────────────────────

class MovimentoFormInicializacionTestCase(TestCase):

    def test_quantidade_itens_localizado(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        form = EntradaEstoqueForm()
        self.assertTrue(form.fields['quantidade_itens'].localize)

    def test_valor_total_localizado(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        form = EntradaEstoqueForm()
        self.assertTrue(form.fields['valor_total'].localize)

    def test_data_movimento_widget_tiene_datepicker(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        form = EntradaEstoqueForm()
        widget_attrs = form.fields['data_movimento'].widget.attrs
        self.assertIn('datepicker', widget_attrs.get('class', ''))

    def test_observacoes_widget_es_textarea(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        from django.forms import Textarea
        form = EntradaEstoqueForm()
        self.assertIsInstance(form.fields['observacoes'].widget, Textarea)


# ─────────────────────────────────────────────
# FORMULARIOS — EntradaEstoqueForm
# ─────────────────────────────────────────────

class EntradaEstoqueFormTestCase(TestCase):

    def test_campo_tipo_movimento_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        form = EntradaEstoqueForm()
        widget_attrs = form.fields['tipo_movimento'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_campo_local_dest_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        form = EntradaEstoqueForm()
        widget_attrs = form.fields['local_dest'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_campo_fornecedor_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        form = EntradaEstoqueForm()
        widget_attrs = form.fields['fornecedor'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_campos_en_meta_fields(self):
        from djangosige.apps.estoque.forms import EntradaEstoqueForm
        form = EntradaEstoqueForm()
        self.assertIn('tipo_movimento', form.fields)
        self.assertIn('pedido_compra', form.fields)
        self.assertIn('fornecedor', form.fields)
        self.assertIn('local_dest', form.fields)


# ─────────────────────────────────────────────
# FORMULARIOS — SaidaEstoqueForm
# ─────────────────────────────────────────────

class SaidaEstoqueFormTestCase(TestCase):

    def test_campo_tipo_movimento_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import SaidaEstoqueForm
        form = SaidaEstoqueForm()
        widget_attrs = form.fields['tipo_movimento'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_campo_local_orig_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import SaidaEstoqueForm
        form = SaidaEstoqueForm()
        widget_attrs = form.fields['local_orig'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_campo_pedido_venda_en_fields(self):
        from djangosige.apps.estoque.forms import SaidaEstoqueForm
        form = SaidaEstoqueForm()
        self.assertIn('pedido_venda', form.fields)

    def test_campos_en_meta_fields(self):
        from djangosige.apps.estoque.forms import SaidaEstoqueForm
        form = SaidaEstoqueForm()
        self.assertIn('tipo_movimento', form.fields)
        self.assertIn('local_orig', form.fields)


# ─────────────────────────────────────────────
# FORMULARIOS — TransferenciaEstoqueForm
# ─────────────────────────────────────────────

class TransferenciaEstoqueFormTestCase(TestCase):

    def test_campo_local_orig_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import TransferenciaEstoqueForm
        form = TransferenciaEstoqueForm()
        widget_attrs = form.fields['local_estoque_orig'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_campo_local_dest_tiene_clase_form_control(self):
        from djangosige.apps.estoque.forms import TransferenciaEstoqueForm
        form = TransferenciaEstoqueForm()
        widget_attrs = form.fields['local_estoque_dest'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_ambos_locales_en_fields(self):
        from djangosige.apps.estoque.forms import TransferenciaEstoqueForm
        form = TransferenciaEstoqueForm()
        self.assertIn('local_estoque_orig', form.fields)
        self.assertIn('local_estoque_dest', form.fields)

    def test_hereda_campos_de_movimentoform(self):
        from djangosige.apps.estoque.forms import TransferenciaEstoqueForm
        form = TransferenciaEstoqueForm()
        self.assertIn('data_movimento', form.fields)
        self.assertIn('quantidade_itens', form.fields)
        self.assertIn('valor_total', form.fields)


# ─────────────────────────────────────────────
# FORMULARIOS — ItensMovimentoForm
# ─────────────────────────────────────────────

class ItensMovimentoFormTestCase(TestCase):

    def test_campos_localizados(self):
        from djangosige.apps.estoque.forms.movimento import ItensMovimentoForm
        form = ItensMovimentoForm()
        self.assertTrue(form.fields['quantidade'].localize)
        self.assertTrue(form.fields['valor_unit'].localize)
        self.assertTrue(form.fields['subtotal'].localize)

    def test_campo_estoque_atual_no_requerido(self):
        from djangosige.apps.estoque.forms.movimento import ItensMovimentoForm
        form = ItensMovimentoForm()
        self.assertFalse(form.fields['estoque_atual'].required)

    def test_campo_estoque_atual_es_readonly(self):
        from djangosige.apps.estoque.forms.movimento import ItensMovimentoForm
        form = ItensMovimentoForm()
        widget_attrs = form.fields['estoque_atual'].widget.attrs
        self.assertEqual(widget_attrs.get('readonly'), True)

    def test_campo_produto_tiene_clase_select_produto(self):
        from djangosige.apps.estoque.forms.movimento import ItensMovimentoForm
        form = ItensMovimentoForm()
        widget_attrs = form.fields['produto'].widget.attrs
        self.assertIn('select-produto', widget_attrs.get('class', ''))

    def test_campo_subtotal_es_readonly(self):
        from djangosige.apps.estoque.forms.movimento import ItensMovimentoForm
        form = ItensMovimentoForm()
        widget_attrs = form.fields['subtotal'].widget.attrs
        self.assertEqual(widget_attrs.get('readonly'), True)

    def test_orden_de_campos(self):
        from djangosige.apps.estoque.forms.movimento import ItensMovimentoForm
        form = ItensMovimentoForm()
        campos = list(form.fields.keys())
        self.assertEqual(campos[0], 'produto')
        self.assertEqual(campos[1], 'quantidade')
        self.assertEqual(campos[2], 'estoque_atual')


# ─────────────────────────────────────────────
# FORMULARIOS — ItensMovimentoForm (rama is_valid)
# ─────────────────────────────────────────────

class ItensMovimentoFormIsValidTestCase(TestCase):

    def test_is_valid_sin_producto_limpia_cleaned_data(self):
        from djangosige.apps.estoque.forms.movimento import ItensMovimentoForm
        form = ItensMovimentoForm(data={
            'produto': '',
            'quantidade': '1,00',
            'valor_unit': '10,00',
            'subtotal': '10,00',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data, {} if not form.errors else form.cleaned_data)
