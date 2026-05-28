# -*- coding: utf-8 -*-
"""
Regressão para o issue #143 — Security Audit.

Antes do fix, as 8 views Info* (que retornam JSON de cliente, fornecedor,
empresa, transportadora, produto, venda, compra e condição de pagamento)
herdavam de `django.views.generic.View` em vez de `CustomView`, o que
fazia elas ignorarem por completo o `CheckPermissionMixin`. Qualquer
usuário autenticado conseguia ler dados sensíveis (CPF, CNPJ, RG,
endereços, preços, etc.) sem ter a permissão `view_<modelo>`.

O fix muda a herança para `CustomView` e define `permission_codename`
em cada uma. Este arquivo confirma que usuários sem a permissão
correspondente são bloqueados.
"""

from django.contrib.auth.models import Permission
from django.urls import reverse

from djangosige.tests.test_case import BaseTestCase, TEST_USERNAME, TEST_PASSWORD


class InfoViewsExigemPermissaoTestCase(BaseTestCase):
    """Cada Info* deve redirecionar com `permission_warning` quando
    o usuário autenticado não tem `view_<modelo>`."""

    def _post_sem_permissao(self, url, post_data, codename):
        # Remove a permissão específica, sai do superuser e re-loga.
        self.user.is_superuser = False
        perm = Permission.objects.get(codename=codename)
        self.user.user_permissions.remove(perm)
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        response = self.client.post(url, post_data, follow=True)
        try:
            message_tags = " ".join(
                str(m.tags) for m in list(response.context['messages']))
            self.assertIn("permission_warning", message_tags)
        finally:
            # Restaura superuser para não contaminar outros testes.
            self.user.is_superuser = True
            self.user.save()
            self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_info_cliente_bloqueia_sem_view_cliente(self):
        url = reverse('cadastro:infocliente')
        self._post_sem_permissao(url, {'pessoaId': 1}, 'view_cliente')

    def test_info_fornecedor_bloqueia_sem_view_fornecedor(self):
        url = reverse('cadastro:infofornecedor')
        self._post_sem_permissao(url, {'pessoaId': 1}, 'view_fornecedor')

    def test_info_empresa_bloqueia_sem_view_empresa(self):
        url = reverse('cadastro:infoempresa')
        self._post_sem_permissao(url, {'pessoaId': 1}, 'view_empresa')

    def test_info_transportadora_bloqueia_sem_view_transportadora(self):
        url = reverse('cadastro:infotransportadora')
        self._post_sem_permissao(
            url, {'transportadoraId': 1}, 'view_transportadora')

    def test_info_produto_bloqueia_sem_view_produto(self):
        url = reverse('cadastro:infoproduto')
        self._post_sem_permissao(url, {'produtoId': 1}, 'view_produto')

    def test_info_venda_bloqueia_sem_view_pedidovenda(self):
        url = reverse('vendas:infovenda')
        self._post_sem_permissao(url, {'vendaId': 1}, 'view_pedidovenda')

    def test_info_compra_bloqueia_sem_view_pedidocompra(self):
        url = reverse('compras:infocompra')
        self._post_sem_permissao(url, {'compraId': 1}, 'view_pedidocompra')

    def test_info_condicao_pagamento_bloqueia_sem_view_condicaopagamento(self):
        url = reverse('vendas:infocondpagamento')
        self._post_sem_permissao(
            url, {'pagamentoId': 1}, 'view_condicaopagamento')
