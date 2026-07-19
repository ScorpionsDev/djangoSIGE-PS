# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _
from djangosige.apps.fiscal.models import GrupoFiscal, ICMS, ICMSSN, ICMSUFDest, IPI, PIS, COFINS


class GrupoFiscalForm(forms.ModelForm):

    class Meta:
        model = GrupoFiscal
        fields = ('descricao', 'regime_trib',)
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'title': 'Insira uma breve descrição do grupo fiscal, EX: ICMS (Simples Nacional) + IPI'}),
            'regime_trib': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'descricao': _('Descripción'),
            'regime_trib': _('Régimen Tributario'),
        }


class ICMSForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'grupo_fiscal' in kwargs:
            grupo_fiscal = kwargs.pop('grupo_fiscal')
            instance = ICMS.objects.get(grupo_fiscal=grupo_fiscal)
            super(ICMSForm, self).__init__(instance=instance, *args, **kwargs)
        else:
            super(ICMSForm, self).__init__(*args, **kwargs)

        self.fields['cst'].required = False

        self.fields['p_icms'].localize = True
        self.fields['p_red_bc'].localize = True
        self.fields['p_mvast'].localize = True
        self.fields['p_red_bcst'].localize = True
        self.fields['p_icmsst'].localize = True
        self.fields['p_dif'].localize = True
        self.fields['p_bc_op'].localize = True

    class Meta:
        model = ICMS
        fields = ('cst', 'mod_bc', 'p_icms', 'p_red_bc', 'mod_bcst', 'p_mvast', 'p_red_bcst', 'p_icmsst', 'mot_des_icms',
                  'p_dif', 'p_bc_op', 'ufst', 'icms_incluido_preco', 'icmsst_incluido_preco', )
        widgets = {
            'cst': forms.Select(attrs={'class': 'form-control'}),
            'mod_bc': forms.Select(attrs={'class': 'form-control'}),
            'p_icms': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_red_bc': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'mod_bcst': forms.Select(attrs={'class': 'form-control'}),
            'p_mvast': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_red_bcst': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_icmsst': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'mot_des_icms': forms.Select(attrs={'class': 'form-control'}),
            'p_dif': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_bc_op': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'ufst': forms.Select(attrs={'class': 'form-control'}),
            'icms_incluido_preco': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'icmsst_incluido_preco': forms.CheckboxInput(attrs={'class': 'form-control'}),

        }
        labels = {
            'cst': _('CST ICMS'),
            'mod_bc': _('Modalidad de determinación de la BC del ICMS'),
            'p_icms': _('Alícuota ICMS'),
            'p_red_bc': _('% de Reducción de BC'),
            'mod_bcst': _('Modalidad de determinación de la BC del ICMS ST'),
            'p_mvast': _('% Margen de valor Agregado del ICMS ST'),
            'p_red_bcst': _('% de Reducción de BC del ICMS ST'),
            'p_icmsst': _('Alícuota ICMS ST'),
            'mot_des_icms': _('Motivo de exoneración del ICMS'),
            'p_dif': _('% de diferimiento'),
            'p_bc_op': _('% de la BC operación propia'),
            'ufst': _('UF para la cual se debe el ICMS ST'),
            'icms_incluido_preco': _('ICMS incluido en el precio'),
            'icmsst_incluido_preco': _('ICMS-ST incluido en el precio'),
        }


class ICMSSNForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'grupo_fiscal' in kwargs:
            grupo_fiscal = kwargs.pop('grupo_fiscal')
            instance = ICMSSN.objects.get(grupo_fiscal=grupo_fiscal)
            super(ICMSSNForm, self).__init__(
                instance=instance, *args, **kwargs)
        else:
            super(ICMSSNForm, self).__init__(*args, **kwargs)

        self.fields['csosn'].required = False

        self.fields['p_cred_sn'].localize = True
        self.fields['p_icms'].localize = True
        self.fields['p_red_bc'].localize = True
        self.fields['p_mvast'].localize = True
        self.fields['p_red_bcst'].localize = True
        self.fields['p_icmsst'].localize = True

    class Meta:
        model = ICMSSN
        fields = ('csosn', 'p_cred_sn', 'p_icms', 'mod_bcst', 'mod_bc', 'p_red_bc', 'p_mvast', 'p_red_bcst', 'p_icmsst',
                  'icmssn_incluido_preco', 'icmssnst_incluido_preco',)
        widgets = {
            'csosn': forms.Select(attrs={'class': 'form-control'}),
            'p_cred_sn': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'mod_bc': forms.Select(attrs={'class': 'form-control'}),
            'p_icms': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_red_bc': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'mod_bcst': forms.Select(attrs={'class': 'form-control'}),
            'p_mvast': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_red_bcst': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_icmsst': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'icmssn_incluido_preco': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'icmssnst_incluido_preco': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'csosn': _('CSOSN'),
            'p_cred_sn': _('Alícuota aplicable de cálculo del crédito'),
            'mod_bc': _('Modalidad de determinación de la BC del ICMS'),
            'p_icms': _('Alícuota ICMS'),
            'p_red_bc': _('% de Reducción de BC'),
            'mod_bcst': _('Modalidad de determinación de la BC del ICMS ST'),
            'p_mvast': _('% Margen de valor Agregado del ICMS ST'),
            'p_red_bcst': _('% de Reducción de BC del ICMS ST'),
            'p_icmsst': _('Alícuota ICMS ST'),
            'icmssn_incluido_preco': _('ICMS incluido en el precio'),
            'icmssnst_incluido_preco': _('ICMS-ST incluido en el precio'),
        }


class ICMSUFDestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'grupo_fiscal' in kwargs:
            grupo_fiscal = kwargs.pop('grupo_fiscal')
            instance = ICMSUFDest.objects.get(grupo_fiscal=grupo_fiscal)
            super(ICMSUFDestForm, self).__init__(
                instance=instance, *args, **kwargs)
        else:
            super(ICMSUFDestForm, self).__init__(*args, **kwargs)

        self.fields['p_fcp_dest'].localize = True
        self.fields['p_icms_dest'].localize = True
        self.fields['p_icms_inter'].localize = True
        self.fields['p_icms_inter_part'].localize = True

    class Meta:
        model = ICMSUFDest
        fields = ('p_fcp_dest', 'p_icms_dest',
                  'p_icms_inter', 'p_icms_inter_part', )
        widgets = {
            'p_fcp_dest': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_icms_dest': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'p_icms_inter': forms.Select(attrs={'class': 'form-control'}),
            'p_icms_inter_part': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'p_fcp_dest': _('% del ICMS relativo al FCP de destino'),
            'p_icms_dest': _('Alícuota interna de la UF de destino'),
            'p_icms_inter': _('Alícuota interestatal de las UF involucradas'),
            'p_icms_inter_part': _('% provisorio de partición del ICMS Interestatal'),
        }


class IPIForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'grupo_fiscal' in kwargs:
            grupo_fiscal = kwargs.pop('grupo_fiscal')
            instance = IPI.objects.get(grupo_fiscal=grupo_fiscal)
            super(IPIForm, self).__init__(instance=instance, *args, **kwargs)
        else:
            super(IPIForm, self).__init__(*args, **kwargs)

        self.fields['p_ipi'].localize = True
        self.fields['valor_fixo'].localize = True

    class Meta:
        model = IPI
        fields = ('cst', 'cl_enq', 'c_enq', 'cnpj_prod', 'tipo_ipi', 'p_ipi',
                  'valor_fixo', 'ipi_incluido_preco', 'incluir_bc_icms', 'incluir_bc_icmsst',)
        widgets = {
            'cst': forms.Select(attrs={'class': 'form-control'}),
            'cl_enq': forms.TextInput(attrs={'class': 'form-control'}),
            'c_enq': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj_prod': forms.TextInput(attrs={'class': 'form-control'}),
            'p_ipi': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'tipo_ipi': forms.Select(attrs={'class': 'form-control'}),
            'valor_fixo': forms.TextInput(attrs={'class': 'form-control decimal-mask'}),
            'ipi_incluido_preco': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'incluir_bc_icms': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'incluir_bc_icmsst': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'cst': _('CST IPI'),
            'cl_enq': _('Clase de encuadramiento para Cigarros y Bebidas'),
            'c_enq': _('Código de Encuadramiento Legal'),
            'cnpj_prod': _('CNPJ del productor de la mercancía'),
            'p_ipi': _('Alícuota del IPI'),
            'tipo_ipi': _('Tipo de cálculo'),
            'valor_fixo': _('Val. fijo IPI (por producto)'),
            'ipi_incluido_preco': _('IPI incluido en el precio'),
            'incluir_bc_icms': _('Incluir IPI en la BC del ICMS'),
            'incluir_bc_icmsst': _('Incluir IPI en la BC del ICMS-ST'),
        }


class PISForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'grupo_fiscal' in kwargs:
            grupo_fiscal = kwargs.pop('grupo_fiscal')
            instance = PIS.objects.get(grupo_fiscal=grupo_fiscal)
            super(PISForm, self).__init__(instance=instance, *args, **kwargs)
        else:
            super(PISForm, self).__init__(*args, **kwargs)

        self.fields['p_pis'].localize = True
        self.fields['valiq_pis'].localize = True

    class Meta:
        model = PIS
        fields = ('cst', 'p_pis', 'valiq_pis',)
        widgets = {
            'cst': forms.Select(attrs={'class': 'form-control'}),
            'p_pis': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'valiq_pis': forms.TextInput(attrs={'class': 'form-control decimal-mask'}),
        }
        labels = {
            'cst': _('CST PIS'),
            'p_pis': _('Alícuota del PIS (en %)'),
            'valiq_pis': _('Alícuota del PIS por producto (en S/)'),
        }


class COFINSForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'grupo_fiscal' in kwargs:
            grupo_fiscal = kwargs.pop('grupo_fiscal')
            instance = COFINS.objects.get(grupo_fiscal=grupo_fiscal)
            super(COFINSForm, self).__init__(
                instance=instance, *args, **kwargs)
        else:
            super(COFINSForm, self).__init__(*args, **kwargs)

        self.fields['p_cofins'].localize = True
        self.fields['valiq_cofins'].localize = True

    class Meta:
        model = COFINS
        fields = ('cst', 'p_cofins', 'valiq_cofins',)
        widgets = {
            'cst': forms.Select(attrs={'class': 'form-control'}),
            'p_cofins': forms.TextInput(attrs={'class': 'form-control percentual-mask'}),
            'valiq_cofins': forms.TextInput(attrs={'class': 'form-control decimal-mask'}),
        }
        labels = {
            'cst': _('CST COFINS'),
            'p_cofins': _('Alícuota del COFINS (en %)'),
            'valiq_cofins': _('Alícuota del COFINS por producto (en S/)'),
        }
