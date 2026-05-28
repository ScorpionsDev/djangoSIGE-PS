# -*- coding: utf-8 -*-
"""
Testes do processador de NF-e (importação de XML).

Issue #122 — NOT NULL constraint failed: fiscal_notafiscal.dhemi

Quando o XML da NF-e v4.0 não traz o elemento `<dhEmi>` legível, o
`pysignfe` retorna `None` para `nfe.infNFe.ide.dhEmi.valor`. Antes do
fix, a importação quebrava ao salvar a nota porque o campo `dhemi` é
NOT NULL no model. O fix em
`djangosige/apps/fiscal/views/processador_nf.py` aplica fallback para
`datetime.now()` em `importar_xml_cliente` e `importar_xml_fornecedor`.
"""

from datetime import datetime

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from djangosige.apps.fiscal.models import NotaFiscalEntrada


def _kwargs_minimos_nota_entrada(**overrides):
    """Campos NOT NULL mínimos pra `NotaFiscalEntrada` salvar.

    `dhemi` é omitido propositalmente — quem chama escolhe se passa
    `None` (reproduzindo o bug) ou o fallback (`datetime.now()`).
    """
    base = dict(
        n_nf_entrada='12345',
        chave='35200499999999999999550010000000011000000010',
        natop='Compra',
        indpag='0',
        serie='1',
        iddest='1',
        tp_imp='1',
        tp_emis='1',
        tp_amb='2',
        fin_nfe='1',
        ind_final='0',
        ind_pres='9',
    )
    base.update(overrides)
    return base


class DhemiFallbackTestCase(TestCase):
    """Regressão para o issue #122."""

    def test_save_sem_dhemi_dispara_integrity_error(self):
        """Documenta o bug: salvar com `dhemi=None` quebra o NOT NULL.

        Antes do fix, `importar_xml_cliente`/`importar_xml_fornecedor`
        chegavam aqui quando o XML não trazia `<dhEmi>` legível.
        """
        nota = NotaFiscalEntrada(dhemi=None, **_kwargs_minimos_nota_entrada())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                nota.save()

    def test_save_com_fallback_para_now_funciona(self):
        """Aplica o mesmo fallback do fix (`valor or datetime.now()`)
        e confirma que a nota persiste sem disparar IntegrityError.
        """
        valor_do_xml = None  # `nfe.infNFe.ide.dhEmi.valor` quando ausente

        nota = NotaFiscalEntrada(
            dhemi=valor_do_xml or datetime.now(),
            **_kwargs_minimos_nota_entrada(n_nf_entrada='99999'),
        )
        nota.save()

        nota.refresh_from_db()
        self.assertIsNotNone(nota.dhemi)
        self.assertIsInstance(nota.dhemi, datetime)

    def test_fallback_preserva_data_real_quando_xml_traz(self):
        """O `or` só dispara quando o valor é falsy — se o XML tem
        `<dhEmi>` legível, a data original deve ser preservada."""
        valor_do_xml = timezone.make_aware(datetime(2025, 6, 15, 14, 30))

        nota = NotaFiscalEntrada(
            dhemi=valor_do_xml or datetime.now(),
            **_kwargs_minimos_nota_entrada(n_nf_entrada='88888'),
        )
        nota.save()

        nota.refresh_from_db()
        self.assertEqual(nota.dhemi, valor_do_xml)
