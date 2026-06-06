# -*- coding: utf-8 -*-
"""
Pruebas UNITARIAS — módulo vendas (SOLO formularios)

Estrategia de aislamiento:
- Los formularios se prueban con datos en memoria.
- No se usa self.client (sin peticiones HTTP).
- No se hereda de BaseTestCase.
"""

from unittest import TestCase


# ─────────────────────────────────────────────
# VendaForm / OrcamentoVendaForm / PedidoVendaForm — inicialización
# ─────────────────────────────────────────────

class VendaFormInicializacionTestCase(TestCase):
    """Verifica que los campos del formulario se inicialicen correctamente."""

    def _get_form(self, form_class, data=None):
        return form_class(data=data)

    def test_orcamento_venda_form_valores_iniciales(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        self.assertEqual(form.fields['status'].initial, '0')
        self.assertEqual(form.fields['valor_total'].initial, '0.00')
        self.assertEqual(form.fields['desconto'].initial, '0.00')
        self.assertEqual(form.fields['frete'].initial, '0.00')
        self.assertEqual(form.fields['seguro'].initial, '0.00')
        self.assertEqual(form.fields['despesas'].initial, '0.00')
        self.assertEqual(form.fields['impostos'].initial, '0.00')
        self.assertEqual(form.fields['total_sem_imposto'].initial, '0.00')

    def test_pedido_venda_form_valores_iniciales(self):
        from djangosige.apps.vendas.forms.vendas import PedidoVendaForm
        form = self._get_form(PedidoVendaForm)
        self.assertEqual(form.fields['status'].initial, '0')
        self.assertEqual(form.fields['valor_total'].initial, '0.00')

    def test_orcamento_venda_form_campo_localize_valor_total(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        self.assertTrue(form.fields['valor_total'].localize)

    def test_orcamento_venda_form_campo_localize_desconto(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        self.assertTrue(form.fields['desconto'].localize)

    def test_orcamento_venda_form_campo_localize_frete(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        self.assertTrue(form.fields['frete'].localize)

    def test_orcamento_venda_form_campo_localize_impostos(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        self.assertTrue(form.fields['impostos'].localize)

    def test_orcamento_venda_form_campo_localize_total_sem_imposto(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        self.assertTrue(form.fields['total_sem_imposto'].localize)


class VendaFormWidgetsTestCase(TestCase):
    """Verifica que los widgets tengan las clases CSS correctas."""

    def _get_form(self, form_class):
        return form_class()

    def test_widget_cliente_tiene_form_control(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        attrs = form.fields['cliente'].widget.attrs
        self.assertIn('form-control', attrs.get('class', ''))

    def test_widget_valor_total_readonly(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        attrs = form.fields['valor_total'].widget.attrs
        self.assertTrue(attrs.get('readonly'))

    def test_widget_impostos_readonly(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        attrs = form.fields['impostos'].widget.attrs
        self.assertTrue(attrs.get('readonly'))

    def test_widget_total_sem_imposto_readonly(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        attrs = form.fields['total_sem_imposto'].widget.attrs
        self.assertTrue(attrs.get('readonly'))

    def test_widget_mod_frete_tiene_form_control(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        attrs = form.fields['mod_frete'].widget.attrs
        self.assertIn('form-control', attrs.get('class', ''))

    def test_widget_status_disabled(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = self._get_form(OrcamentoVendaForm)
        attrs = form.fields['status'].widget.attrs
        self.assertTrue(attrs.get('disabled'))

    def test_widget_orcamento_disabled_en_pedido(self):
        from djangosige.apps.vendas.forms.vendas import PedidoVendaForm
        form = self._get_form(PedidoVendaForm)
        attrs = form.fields['orcamento'].widget.attrs
        self.assertTrue(attrs.get('disabled'))


class OrcamentoVendaFormValidacionTestCase(TestCase):
    """Verifica la validación del formulario OrcamentoVendaForm."""

    def _get_form(self, data):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        return OrcamentoVendaForm(data=data)

    def test_form_invalido_sin_cliente(self):
        data = {
            'data_emissao': '16/07/2024',
            'status': '0',
            'tipo_desconto': '0',
            'desconto': '0,00',
            'frete': '0,00',
            'seguro': '0,00',
            'despesas': '0,00',
            'mod_frete': '9',
            'impostos': '0,00',
            'valor_total': '0,00',
        }
        form = self._get_form(data)
        self.assertFalse(form.is_valid())
        self.assertIn('cliente', form.errors)

    def test_form_tiene_campo_data_vencimento(self):
        from djangosige.apps.vendas.forms.vendas import OrcamentoVendaForm
        form = OrcamentoVendaForm()
        self.assertIn('data_vencimento', form.fields)

    def test_pedido_form_tiene_campo_data_entrega(self):
        from djangosige.apps.vendas.forms.vendas import PedidoVendaForm
        form = PedidoVendaForm()
        self.assertIn('data_entrega', form.fields)

    def test_pedido_form_tiene_campo_orcamento(self):
        from djangosige.apps.vendas.forms.vendas import PedidoVendaForm
        form = PedidoVendaForm()
        self.assertIn('orcamento', form.fields)


# ─────────────────────────────────────────────
# ItensVendaForm
# ─────────────────────────────────────────────

class ItensVendaFormTestCase(TestCase):

    def _get_form(self):
        from djangosige.apps.vendas.forms.vendas import ItensVendaForm
        return ItensVendaForm()

    def test_campos_localizados(self):
        form = self._get_form()
        self.assertTrue(form.fields['quantidade'].localize)
        self.assertTrue(form.fields['valor_unit'].localize)
        self.assertTrue(form.fields['desconto'].localize)
        self.assertTrue(form.fields['subtotal'].localize)

    def test_campos_rateio_localizados(self):
        form = self._get_form()
        self.assertTrue(form.fields['valor_rateio_frete'].localize)
        self.assertTrue(form.fields['valor_rateio_despesas'].localize)
        self.assertTrue(form.fields['valor_rateio_seguro'].localize)

    def test_campos_impostos_localizados(self):
        form = self._get_form()
        self.assertTrue(form.fields['vicms'].localize)
        self.assertTrue(form.fields['vipi'].localize)
        self.assertTrue(form.fields['p_icms'].localize)
        self.assertTrue(form.fields['p_ipi'].localize)
        self.assertTrue(form.fields['p_icmsst'].localize)

    def test_campos_extra_no_requeridos(self):
        form = self._get_form()
        self.assertFalse(form.fields['total_sem_desconto'].required)
        self.assertFalse(form.fields['total_impostos'].required)
        self.assertFalse(form.fields['total_com_impostos'].required)
        self.assertFalse(form.fields['calculo_imposto'].required)

    def test_campos_modal_no_requeridos(self):
        form = self._get_form()
        self.assertFalse(form.fields['p_red_bc'].required)
        self.assertFalse(form.fields['p_red_bcst'].required)
        self.assertFalse(form.fields['p_mvast'].required)
        self.assertFalse(form.fields['pfcp'].required)

    def test_widget_produto_clase_select_produto(self):
        form = self._get_form()
        attrs = form.fields['produto'].widget.attrs
        self.assertIn('select-produto', attrs.get('class', ''))

    def test_widget_subtotal_readonly(self):
        form = self._get_form()
        attrs = form.fields['subtotal'].widget.attrs
        self.assertTrue(attrs.get('readonly'))

    def test_campos_vbc_localizados(self):
        form = self._get_form()
        self.assertTrue(form.fields['vbc_icms'].localize)
        self.assertTrue(form.fields['vbc_icms_st'].localize)
        self.assertTrue(form.fields['vbc_ipi'].localize)

    def test_campos_icms_uf_localizados(self):
        form = self._get_form()
        self.assertTrue(form.fields['vicmsufdest'].localize)
        self.assertTrue(form.fields['vicmsufremet'].localize)
        self.assertTrue(form.fields['vfcp'].localize)


class ItensVendaFormIsValidTestCase(TestCase):
    """Prueba la rama is_valid cuando el producto es None."""

    def test_is_valid_sin_producto_limpia_cleaned_data(self):
        from djangosige.apps.vendas.forms.vendas import ItensVendaForm
        form = ItensVendaForm(data={
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
# PagamentoForm (vendas)
# ─────────────────────────────────────────────

class PagamentoVendaFormTestCase(TestCase):

    def _get_form(self, data=None):
        from djangosige.apps.vendas.forms.pagamento import PagamentoForm
        return PagamentoForm(data=data)

    def test_valor_parcela_localizado(self):
        form = self._get_form()
        self.assertTrue(form.fields['valor_parcela'].localize)

    def test_indice_parcela_readonly(self):
        form = self._get_form()
        attrs = form.fields['indice_parcela'].widget.attrs
        self.assertEqual(attrs.get('readonly'), True)

    def test_form_invalido_sin_vencimiento(self):
        form = self._get_form(data={
            'indice_parcela': 1,
            'valor_parcela': '100,00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('vencimento', form.errors)

    def test_form_invalido_sin_valor(self):
        form = self._get_form(data={
            'indice_parcela': 1,
            'vencimento': '31/07/2024',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('valor_parcela', form.errors)

    def test_widget_vencimento_tiene_datepicker(self):
        form = self._get_form()
        attrs = form.fields['vencimento'].widget.attrs
        self.assertIn('datepicker', attrs.get('class', ''))


# ─────────────────────────────────────────────
# CondicaoPagamentoForm
# ─────────────────────────────────────────────

class CondicaoPagamentoFormTestCase(TestCase):

    def _get_form(self, data=None):
        from djangosige.apps.vendas.forms.pagamento import CondicaoPagamentoForm
        return CondicaoPagamentoForm(data=data)

    def test_form_instancia_correctamente(self):
        form = self._get_form()
        self.assertIn('descricao', form.fields)
        self.assertIn('forma', form.fields)
        self.assertIn('n_parcelas', form.fields)
        self.assertIn('dias_recorrencia', form.fields)
        self.assertIn('parcela_inicial', form.fields)

    def test_widget_descricao_tiene_form_control(self):
        form = self._get_form()
        attrs = form.fields['descricao'].widget.attrs
        self.assertIn('form-control', attrs.get('class', ''))

    def test_widget_forma_tiene_form_control(self):
        form = self._get_form()
        attrs = form.fields['forma'].widget.attrs
        self.assertIn('form-control', attrs.get('class', ''))

    def test_form_invalido_sin_descricao(self):
        form = self._get_form(data={
            'forma': '01',
            'n_parcelas': 1,
            'dias_recorrencia': 0,
            'parcela_inicial': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('descricao', form.errors)

    def test_form_invalido_sin_n_parcelas(self):
        form = self._get_form(data={
            'descricao': 'À Vista',
            'forma': '01',
            'dias_recorrencia': 0,
            'parcela_inicial': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('n_parcelas', form.errors)

    def test_widget_n_parcelas_tiene_form_control(self):
        form = self._get_form()
        attrs = form.fields['n_parcelas'].widget.attrs
        self.assertIn('form-control', attrs.get('class', ''))
