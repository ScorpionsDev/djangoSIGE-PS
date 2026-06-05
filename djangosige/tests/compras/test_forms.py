# -*- coding: utf-8 -*-
"""
Pruebas UNITARIAS — módulo compras (SOLO formularios)

Estrategia de aislamiento:
- Los formularios se prueban con datos en memoria.
- No se usa self.client (sin peticiones HTTP).
- No se hereda de BaseTestCase.
"""

from unittest import TestCase


# ─────────────────────────────────────────────
# FORMULARIOS — CompraForm / OrcamentoCompraForm / PedidoCompraForm
# ─────────────────────────────────────────────

class CompraFormInicializacionTestCase(TestCase):
    """Verifica que los campos del formulario se inicialicen correctamente."""

    def _get_form(self, form_class, data=None):
        return form_class(data=data)

    def test_orcamento_compra_form_valores_iniciales(self):
        from djangosige.apps.compras.forms.compras import OrcamentoCompraForm
        form = self._get_form(OrcamentoCompraForm)
        self.assertEqual(form.fields['status'].initial, '0')
        self.assertEqual(form.fields['valor_total'].initial, '0.00')
        self.assertEqual(form.fields['desconto'].initial, '0.00')
        self.assertEqual(form.fields['frete'].initial, '0.00')
        self.assertEqual(form.fields['seguro'].initial, '0.00')
        self.assertEqual(form.fields['despesas'].initial, '0.00')
        self.assertEqual(form.fields['total_ipi'].initial, '0.00')
        self.assertEqual(form.fields['total_icms'].initial, '0.00')

    def test_pedido_compra_form_valores_iniciales(self):
        from djangosige.apps.compras.forms.compras import PedidoCompraForm
        form = self._get_form(PedidoCompraForm)
        self.assertEqual(form.fields['status'].initial, '0')
        self.assertEqual(form.fields['valor_total'].initial, '0.00')

    def test_orcamento_compra_form_widget_fornecedor(self):
        from djangosige.apps.compras.forms.compras import OrcamentoCompraForm
        form = self._get_form(OrcamentoCompraForm)
        widget_attrs = form.fields['fornecedor'].widget.attrs
        self.assertIn('form-control', widget_attrs.get('class', ''))

    def test_orcamento_compra_form_campo_requerido_fornecedor(self):
        from djangosige.apps.compras.forms.compras import OrcamentoCompraForm
        data = {
            'data_emissao': '16/07/2024',
            'status': '0',
            'tipo_desconto': '0',
            'desconto': '0,00',
            'frete': '0,00',
            'seguro': '0,00',
            'despesas': '0,00',
            'mod_frete': '0',
            'total_icms': '0,00',
            'total_ipi': '0,00',
            'valor_total': '0,00',
        }
        form = self._get_form(OrcamentoCompraForm, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fornecedor', form.errors)


# ─────────────────────────────────────────────
# FORMULARIOS — ItensCompraForm
# ─────────────────────────────────────────────

class ItensCompraFormTestCase(TestCase):

    def test_campos_localizados(self):
        from djangosige.apps.compras.forms.compras import ItensCompraForm
        form = ItensCompraForm()
        self.assertTrue(form.fields['quantidade'].localize)
        self.assertTrue(form.fields['valor_unit'].localize)
        self.assertTrue(form.fields['desconto'].localize)
        self.assertTrue(form.fields['subtotal'].localize)

    def test_campos_extra_no_requeridos(self):
        from djangosige.apps.compras.forms.compras import ItensCompraForm
        form = ItensCompraForm()
        self.assertFalse(form.fields['total_sem_desconto'].required)
        self.assertFalse(form.fields['total_impostos'].required)
        self.assertFalse(form.fields['total_com_impostos'].required)

    def test_widget_produto_tiene_clase_select_produto(self):
        from djangosige.apps.compras.forms.compras import ItensCompraForm
        form = ItensCompraForm()
        widget_class = form.fields['produto'].widget.attrs.get('class', '')
        self.assertIn('select-produto', widget_class)


# ─────────────────────────────────────────────
# FORMULARIOS — ItensCompraForm (rama is_valid)
# ─────────────────────────────────────────────

class ItensCompraFormIsValidTestCase(TestCase):

    def test_is_valid_sin_producto_limpia_cleaned_data(self):
        from djangosige.apps.compras.forms.compras import ItensCompraForm
        form = ItensCompraForm(data={
            'produto': '',
            'quantidade': '1,00',
            'valor_unit': '10,00',
            'tipo_desconto': '0',
            'desconto': '0,00',
            'subtotal': '10,00',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data, {} if not form.errors else form.cleaned_data)


# ─────────────────────────────────────────────
# FORMULARIOS — PagamentoForm
# ─────────────────────────────────────────────

class PagamentoFormTestCase(TestCase):

    def test_valor_parcela_localizado(self):
        from djangosige.apps.compras.forms.pagamento import PagamentoForm
        form = PagamentoForm()
        self.assertTrue(form.fields['valor_parcela'].localize)

    def test_indice_parcela_readonly(self):
        from djangosige.apps.compras.forms.pagamento import PagamentoForm
        form = PagamentoForm()
        attrs = form.fields['indice_parcela'].widget.attrs
        self.assertEqual(attrs.get('readonly'), True)

    def test_form_invalido_sin_vencimiento(self):
        from djangosige.apps.compras.forms.pagamento import PagamentoForm
        data = {
            'indice_parcela': 1,
            'valor_parcela': '100,00',
        }
        form = PagamentoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('vencimento', form.errors)

    def test_form_invalido_sin_valor(self):
        from djangosige.apps.compras.forms.pagamento import PagamentoForm
        data = {
            'indice_parcela': 1,
            'vencimento': '31/07/2024',
        }
        form = PagamentoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('valor_parcela', form.errors)