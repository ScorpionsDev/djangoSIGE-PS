# -*- coding: utf-8 -*-

from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from djangosige.apps.fiscal.models import NotaFiscalSaida, NotaFiscalEntrada, AutXML, ConfiguracaoNotaFiscal, TP_AMB_ESCOLHAS, MOD_NFE_ESCOLHAS
from djangosige.apps.cadastro.models import Empresa

try:
    from pysignfe.nfe.manifestacao_destinatario import MD_CONFIRMACAO_OPERACAO, MD_DESCONHECIMENTO_OPERACAO, MD_OPERACAO_NAO_REALIZADA, MD_CIENCIA_OPERACAO
except ImportError:
    MD_CONFIRMACAO_OPERACAO = u'210200'
    MD_DESCONHECIMENTO_OPERACAO = u'210220'
    MD_OPERACAO_NAO_REALIZADA = u'210240'
    MD_CIENCIA_OPERACAO = u'210210'

TP_MANIFESTO_OPCOES = (
    (MD_CONFIRMACAO_OPERACAO, u'Confirmación de la Operación'),
    (MD_DESCONHECIMENTO_OPERACAO, u'Desconocimiento de la Operación'),
    (MD_OPERACAO_NAO_REALIZADA, u'Operación No Realizada'),
    (MD_CIENCIA_OPERACAO, u'Conocimiento de la Emisión (o Conocimiento de la Operación)'),
)


class NotaFiscalForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NotaFiscalForm, self).__init__(*args, **kwargs)
        self.fields['dhemi'].input_formats = ('%d/%m/%Y %H:%M',)

    class Meta:
        fields = ('versao', 'status_nfe', 'natop', 'indpag', 'mod', 'serie', 'dhemi', 'dhsaient', 'iddest',
                  'tp_imp', 'tp_emis', 'tp_amb', 'fin_nfe', 'ind_final', 'ind_pres', 'inf_ad_fisco', 'inf_cpl',)

        widgets = {
            'versao': forms.Select(attrs={'class': 'form-control'}),
            'status_nfe': forms.Select(attrs={'class': 'form-control', 'disabled': True}),
            'natop': forms.TextInput(attrs={'class': 'form-control'}),
            'indpag': forms.Select(attrs={'class': 'form-control'}),
            'mod': forms.Select(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'dhemi': forms.DateTimeInput(attrs={'class': 'form-control datetimepicker'}, format='%d/%m/%Y %H:%M'),
            'dhsaient': forms.DateTimeInput(attrs={'class': 'form-control datetimepicker'}, format='%d/%m/%Y %H:%M'),
            'iddest': forms.Select(attrs={'class': 'form-control'}),
            'tp_imp': forms.Select(attrs={'class': 'form-control'}),
            'tp_emis': forms.Select(attrs={'class': 'form-control'}),
            'tp_amb': forms.Select(attrs={'class': 'form-control'}),
            'fin_nfe': forms.Select(attrs={'class': 'form-control'}),
            'ind_final': forms.Select(attrs={'class': 'form-control'}),
            'ind_pres': forms.Select(attrs={'class': 'form-control'}),
            'inf_ad_fisco': forms.Textarea(attrs={'class': 'form-control'}),
            'inf_cpl': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'versao': _('Versión'),
            'status_nfe': _('Estado'),
            'natop': _('Naturaleza de la Operación'),
            'indpag': _('Forma de pago'),
            'mod': _('Modelo'),
            'serie': _('Serie'),
            'dhemi': _('Fecha y hora de emisión'),
            'dhsaient': _('Fecha y hora de Salida/Entrada'),
            'iddest': _('Destino de la operación'),
            'tp_imp': _('Tipo de impresión del DANFE'),
            'tp_emis': _('Forma de emisión'),
            'tp_amb': _('Ambiente'),
            'fin_nfe': _('Finalidad de la emisión'),
            'ind_final': _('Consumidor final'),
            'ind_pres': _('Tipo de atención'),
            'inf_ad_fisco': _('Información Adicional de Interés del Fisco'),
            'inf_cpl': _('Información Complementaria de interés del Contribuyente'),
        }

        error_messages = {
            'n_nf': {
                'unique': _("Ya existe una nota fiscal con este número"),
            },
        }


class NotaFiscalSaidaForm(NotaFiscalForm):

    def __init__(self, *args, **kwargs):
        super(NotaFiscalSaidaForm, self).__init__(*args, **kwargs)
        self.fields['v_orig'].localize = True
        self.fields['v_desc'].localize = True
        self.fields['v_liq'].localize = True

    class Meta(NotaFiscalForm.Meta):
        model = NotaFiscalSaida
        fields = NotaFiscalForm.Meta.fields + ('n_nf_saida', 'tpnf', 'venda', 'emit_saida',
                                               'dest_saida', 'n_fat', 'v_orig', 'v_desc', 'v_liq', 'grupo_cobr', 'arquivo_proc',)
        widgets = NotaFiscalForm.Meta.widgets
        widgets['n_nf_saida'] = forms.TextInput(
            attrs={'class': 'form-control'})
        widgets['venda'] = forms.Select(attrs={'class': 'form-control'})
        widgets['emit_saida'] = forms.Select(attrs={'class': 'form-control'})
        widgets['dest_saida'] = forms.Select(attrs={'class': 'form-control'})
        widgets['n_fat'] = forms.TextInput(attrs={'class': 'form-control'})
        widgets['tpnf'] = forms.Select(attrs={'class': 'form-control'})
        widgets['v_orig'] = forms.TextInput(
            attrs={'class': 'form-control decimal-mask'})
        widgets['v_desc'] = forms.TextInput(
            attrs={'class': 'form-control decimal-mask'})
        widgets['v_liq'] = forms.TextInput(
            attrs={'class': 'form-control decimal-mask'})
        widgets['grupo_cobr'] = forms.CheckboxInput(
            attrs={'class': 'form-control'})
        widgets['arquivo_proc'] = forms.FileInput(
            attrs={'class': 'form-control'})
        labels = NotaFiscalForm.Meta.labels
        labels['n_nf_saida'] = _('Número')
        labels['venda'] = _('Venta')
        labels['emit_saida'] = _('Emisor (Empresa)')
        labels['dest_saida'] = _('Destinatario (Cliente)')
        labels['n_fat'] = _('Número de factura')
        labels['tpnf'] = _('Tipo de Operación')
        labels['v_orig'] = _('Monto original de la factura')
        labels['v_desc'] = _('Monto del descuento')
        labels['v_liq'] = _('Monto líquido de la factura')
        labels['grupo_cobr'] = _(
            '¿Insertar datos de cobro (Factura/Letras) en la NF-e?')
        labels['arquivo_proc'] = _('Archivo de procesamiento (*_procNFe.xml)')


class NotaFiscalEntradaForm(NotaFiscalForm):

    class Meta(NotaFiscalForm.Meta):
        model = NotaFiscalEntrada
        fields = NotaFiscalForm.Meta.fields + \
            ('n_nf_entrada', 'compra', 'emit_entrada', 'dest_entrada',)
        widgets = NotaFiscalForm.Meta.widgets
        widgets['n_nf_entrada'] = forms.TextInput(
            attrs={'class': 'form-control'})
        widgets['compra'] = forms.Select(attrs={'class': 'form-control'})
        widgets['emit_entrada'] = forms.Select(attrs={'class': 'form-control'})
        widgets['dest_entrada'] = forms.Select(attrs={'class': 'form-control'})
        labels = NotaFiscalForm.Meta.labels
        labels['n_nf_entrada'] = _('Número')
        labels['compra'] = _('Compra')
        labels['emit_entrada'] = _('Emisor (Proveedor)')
        labels['dest_entrada'] = _('Destinatario (Empresa)')


class EmissaoNotaFiscalForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EmissaoNotaFiscalForm, self).__init__(*args, **kwargs)
        self.fields['dhemi'].input_formats = ('%d/%m/%Y %H:%M',)

    class Meta:
        model = NotaFiscalSaida
        fields = ('versao', 'dhemi', 'dhsaient',
                  'tp_imp', 'tp_emis', 'tp_amb',)

        widgets = {
            'versao': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'dhemi': forms.DateTimeInput(attrs={'class': 'form-control datetimepicker', 'required': True}, format='%d/%m/%Y %H:%M'),
            'dhsaient': forms.DateTimeInput(attrs={'class': 'form-control datetimepicker'}, format='%d/%m/%Y %H:%M'),
            'tp_imp': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'tp_emis': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'tp_amb': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'versao': _('Versión'),
            'dhemi': _('Fecha y hora de emisión'),
            'dhsaient': _('Fecha y hora de Salida/Entrada'),
            'tp_imp': _('Tipo de impresión del DANFE'),
            'tp_emis': _('Forma de emisión'),
            'tp_amb': _('Ambiente'),
        }


class CancelamentoNotaFiscalForm(forms.ModelForm):

    class Meta:
        model = NotaFiscalSaida
        fields = ('just_canc', 'chave',
                  'numero_protocolo', 'tp_emis', 'tp_amb',)

        widgets = {
            'just_canc': forms.Textarea(attrs={'class': 'form-control', 'required': True}),
            'chave': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'numero_protocolo': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'tp_emis': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'tp_amb': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'just_canc': _('Justificación de anulación'),
            'chave': _('Clave'),
            'numero_protocolo': _('Número de protocolo'),
            'tp_emis': _('Forma de emisión'),
            'tp_amb': _('Ambiente'),
        }


class ConsultarCadastroForm(forms.Form):
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control', }), label='Seleccionar empresa', required=True)
    salvar_arquivos = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-control', }), label='Guardar archivos XML generados?', required=False)


class InutilizarNotasForm(forms.Form):
    ambiente = forms.ChoiceField(choices=TP_AMB_ESCOLHAS, widget=forms.Select(
        attrs={'class': 'form-control', }), label='Ambiente', initial='2', required=True)
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control', }), label='Seleccionar empresa emisora', required=True)
    modelo = forms.ChoiceField(choices=MOD_NFE_ESCOLHAS, widget=forms.Select(
        attrs={'class': 'form-control', }), label='Modelo', required=True)
    serie = forms.CharField(max_length=3, widget=forms.TextInput(
        attrs={'class': 'form-control', }), label='Serie', required=True)
    numero_inicial = forms.CharField(max_length=9, widget=forms.TextInput(
        attrs={'class': 'form-control', }), label='Número inicial', required=True)
    numero_final = forms.CharField(max_length=9, widget=forms.TextInput(
        attrs={'class': 'form-control', }), label='Número final', required=False)
    justificativa = forms.CharField(max_length=255, widget=forms.Textarea(
        attrs={'class': 'form-control', }), label='Justificación', required=False)
    salvar_arquivos = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-control', }), label='Guardar archivos XML generados?', required=False)


class ConsultarNotaForm(forms.Form):
    ambiente = forms.ChoiceField(choices=TP_AMB_ESCOLHAS, widget=forms.Select(
        attrs={'class': 'form-control', }), label='Ambiente', initial='2', required=True)
    nota = forms.ModelChoiceField(queryset=NotaFiscalSaida.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control', }), label='Seleccionar nota de la base de datos', required=False)
    chave = forms.CharField(max_length=44, widget=forms.TextInput(
        attrs={'class': 'form-control', }), label='Clave de la nota', required=False)
    salvar_arquivos = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-control', }), label='Salvar arquivos XML gerados?', required=False)


class BaixarNotaForm(forms.Form):
    ambiente = forms.ChoiceField(choices=TP_AMB_ESCOLHAS, widget=forms.Select(
        attrs={'class': 'form-control', }), label='Ambiente', initial='2', required=True)
    nota = forms.ModelChoiceField(queryset=NotaFiscalSaida.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control', }), label='Seleccionar nota de la base de datos', required=False)
    chave = forms.CharField(max_length=44, widget=forms.TextInput(
        attrs={'class': 'form-control', }), label='Clave de la nota', required=False)
    ambiente_nacional = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-control', }), label='Utilizar ambiente nacional? (Recomendado)', initial=True, required=False)
    salvar_arquivos = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-control', }), label='Guardar archivos XML generados?', required=False)


class ManifestacaoDestinatarioForm(forms.Form):
    cnpj = forms.CharField(max_length=16, widget=forms.TextInput(attrs={
                           'class': 'form-control', }), label='CNPJ del autor del Evento (solo dígitos)', required=True)
    tipo_manifesto = forms.ChoiceField(choices=TP_MANIFESTO_OPCOES, widget=forms.Select(
        attrs={'class': 'form-control', }), label='Tipo de manifiesto', required=True)
    ambiente = forms.ChoiceField(choices=TP_AMB_ESCOLHAS, widget=forms.Select(
        attrs={'class': 'form-control', }), label='Ambiente', initial='2', required=True)
    nota = forms.ModelChoiceField(queryset=NotaFiscalSaida.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control', }), label='Seleccionar nota de la base de datos', required=False)
    chave = forms.CharField(max_length=44, widget=forms.TextInput(
        attrs={'class': 'form-control', }), label='Clave de la nota', required=False)
    ambiente_nacional = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-control', }), label='Utilizar ambiente nacional? (Recomendado)', initial=True, required=False)
    justificativa = forms.CharField(max_length=255, widget=forms.Textarea(
        attrs={'class': 'form-control', }), label='Justificación', required=False)
    salvar_arquivos = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-control', }), label='Guardar archivos XML generados?', required=False)


class AutXMLForm(forms.ModelForm):

    class Meta:
        model = AutXML
        fields = ('cpf_cnpj',)
        labels = {
            'cpf_cnpj': _('CPF/CNPJ (Solo dígitos)'),
        }
        widgets = {
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ConfiguracaoNotaFiscalForm(forms.ModelForm):

    class Meta:
        model = ConfiguracaoNotaFiscal
        fields = ('serie_atual', 'ambiente', 'imp_danfe', 'arquivo_certificado_a1',
                  'senha_certificado', 'inserir_logo_danfe', 'orientacao_logo_danfe', 'csc', 'cidtoken',)
        labels = {
            'arquivo_certificado_a1': _('Certificado A1'),
            'serie_atual': _('Serie actual'),
            'ambiente': _('Ambiente'),
            'imp_danfe': _('Tipo de impresión DANFE'),
            'senha_certificado': _('Contraseña del certificado'),
            'inserir_logo_danfe': _('¿Insertar logo de la empresa en el DANFE?'),
            'orientacao_logo_danfe': _('Orientación del logo'),
            'csc': _('Código de Seguridad del Contribuyente'),
            'cidtoken': _('Identificador del CSC'),
        }
        widgets = {
            'arquivo_certificado_a1': forms.FileInput(attrs={'class': 'form-control'}),
            'serie_atual': forms.TextInput(attrs={'class': 'form-control'}),
            'ambiente': forms.Select(attrs={'class': 'form-control'}),
            'imp_danfe': forms.Select(attrs={'class': 'form-control'}),
            'senha_certificado': forms.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
            'inserir_logo_danfe': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'orientacao_logo_danfe': forms.Select(attrs={'class': 'form-control'}),
            'csc': forms.TextInput(attrs={'class': 'form-control'}),
            'cidtoken': forms.TextInput(attrs={'class': 'form-control'}),
        }


AutXMLFormSet = inlineformset_factory(
    NotaFiscalSaida, AutXML, form=AutXMLForm, extra=1, can_delete=True)
