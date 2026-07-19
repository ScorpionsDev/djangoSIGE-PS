# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import re

UF_SIGLA = [
    ('AC', 'AC'),
    ('AL', 'AL'),
    ('AP', 'AP'),
    ('AM', 'AM'),
    ('BA', 'BA'),
    ('CE', 'CE'),
    ('DF', 'DF'),
    ('ES', 'ES'),
    ('EX', 'EX'),
    ('GO', 'GO'),
    ('MA', 'MA'),
    ('MT', 'MT'),
    ('MS', 'MS'),
    ('MG', 'MG'),
    ('PA', 'PA'),
    ('PB', 'PB'),
    ('PR', 'PR'),
    ('PE', 'PE'),
    ('PI', 'PI'),
    ('RJ', 'RJ'),
    ('RN', 'RN'),
    ('RS', 'RS'),
    ('RO', 'RO'),
    ('RR', 'RR'),
    ('SC', 'SC'),
    ('SP', 'SP'),
    ('SE', 'SE'),
    ('TO', 'TO'),
]

CST_ICMS_ESCOLHAS = (
    (u'00', u'00 - Tributada integralmente'),
    (u'10', u'10 - Tributada y con cobro del ICMS por sustitución tributaria'),
    (u'10p', u'10 - Tributada y con cobro del ICMS por sustitución tributaria (con partición del ICMS)'),
    (u'20', u'20 - Con reducción de base de cálculo.'),
    (u'30', u'30 - Exenta o no tributada y con cobro del ICMS por sustitución tributaria'),
    (u'40', u'40 - Exenta'),
    (u'41', u'41 - No tributada'),
    (u'41r', u'41 - No tributada (ICMS ST adeudado a la UF de destino, en operaciones interestatales de productos con retención anticipada)'),
    (u'50', u'50 - Suspensión'),
    (u'51', u'51 - Diferimiento'),
    (u'60', u'60 - Cobrado anteriormente por sustitución tributaria'),
    (u'70', u'70 - Con reducción de base de cálculo y cobro del ICMS por sustitución tributaria'),
    (u'90p', u'90 - Otros (con partición del ICMS)'),
    (u'90', u'90 -  Otros'),
)

CST_IPI_ESCOLHAS = (
    (u'00', u'00 - Entrada con Recuperación de Crédito'),
    (u'01', u'01 - Entrada Tributable con Alícuota Cero'),
    (u'02', u'02 - Entrada Exenta'),
    (u'03', u'03 - Entrada No Tributada'),
    (u'04', u'04 - Entrada Inmune'),
    (u'05', u'05 - Entrada con Suspensión'),
    (u'49', u'49 - Otras Entradas'),
    (u'50', u'50 - Salida Tributada'),
    (u'51', u'51 - Salida Tributable con Alícuota Cero'),
    (u'52', u'52 - Salida Exenta'),
    (u'53', u'53 - Salida No Tributada'),
    (u'54', u'54 - Salida Inmune'),
    (u'55', u'55 - Salida con Suspensión'),
    (u'99', u'99 - Otras Salidas'),
)

CST_PIS_COFINS_ESCOLHAS = (
    (u'01', u'01 - Operación Tributable con Alícuota Básica'),
    (u'02', u'02 - Operación Tributable con Alícuota Diferenciada'),
    (u'03', u'03 - Operación Tributable con Alícuota por Unidad de Medida de Producto'),
    (u'04', u'04 - Operación Tributable Monofásica - Reventa a Alícuota Cero'),
    (u'05', u'05 - Operación Tributable por Sustitución Tributaria'),
    (u'06', u'06 - Operación Tributable a Alícuota Cero'),
    (u'07', u'07 - Operación Exenta de la Contribución'),
    (u'08', u'08 - Operación sin Incidencia de la Contribución'),
    (u'09', u'09 - Operación con Suspensión de la Contribución'),
    (u'49', u'49 - Otras Operaciones de Salida'),
    (u'50', u'50 - Operación con Derecho a Crédito - Vinculada Exclusivamente a Ingreso Tributado en el Mercado Interno'),
    (u'51', u'51 - Operación con Derecho a Crédito - Vinculada Exclusivamente a Ingreso No Tributado en el Mercado Interno'),
    (u'52', u'52 - Operación con Derecho a Crédito - Vinculada Exclusivamente a Ingreso de Exportación'),
    (u'53', u'53 - Operación con Derecho a Crédito - Vinculada a Ingresos Tributados y No Tributados en el Mercado Interno'),
    (u'54', u'54 - Operación con Derecho a Crédito - Vinculada a Ingresos Tributados en el Mercado Interno y de Exportación'),
    (u'55', u'55 - Operación con Derecho a Crédito - Vinculada a Ingresos No Tributados en el Mercado Interno y de Exportación'),
    (u'56', u'56 - Operación con Derecho a Crédito - Vinculada a Ingresos Tributados y No Tributados en el Mercado Interno y de Exportación'),
    (u'60', u'60 - Crédito Presumido - Operación de Adquisición Vinculada Exclusivamente a Ingreso Tributado en el Mercado Interno'),
    (u'61', u'61 - Crédito Presumido - Operación de Adquisición Vinculada Exclusivamente a Ingreso No Tributado en el Mercado Interno'),
    (u'62', u'62 - Crédito Presumido - Operación de Adquisición Vinculada Exclusivamente a Ingreso de Exportación'),
    (u'63', u'63 - Crédito Presumido - Operación de Adquisición Vinculada a Ingresos Tributados y No Tributados en el Mercado Interno'),
    (u'64', u'64 - Crédito Presumido - Operación de Adquisición Vinculada a Ingresos Tributados en el Mercado Interno y de Exportación'),
    (u'65', u'65 - Crédito Presumido - Operación de Adquisición Vinculada a Ingresos No Tributados en el Mercado Interno y de Exportación'),
    (u'66', u'66 - Crédito Presumido - Operación de Adquisición Vinculada a Ingresos Tributados y No Tributados en el Mercado Interno y de Exportación'),
    (u'67', u'67 - Crédito Presumido - Otras Operaciones'),
    (u'70', u'70 - Operación de Adquisición sin Derecho a Crédito'),
    (u'71', u'71 - Operación de Adquisición con Exención'),
    (u'72', u'72 - Operación de Adquisición con Suspensión'),
    (u'73', u'73 - Operación de Adquisición a Alícuota Cero'),
    (u'74', u'74 - Operación de Adquisición sin Incidencia de la Contribución'),
    (u'75', u'75 - Operación de Adquisición por Sustitución Tributaria'),
    (u'98', u'98 - Otras Operaciones de Entrada'),
    (u'99', u'99 - Otras Operaciones'),
)

CSOSN_ESCOLHAS = (
    (u'101', u'101 - Tributada con permiso de crédito'),
    (u'102', u'102 - Tributada sin permiso de crédito'),
    (u'103', u'103 - Exención del ICMS para rango de ingreso bruto'),
    (u'201', u'201 - Tributada con permiso de crédito y con cobro del ICMS por Sustitución Tributaria'),
    (u'202', u'202 - Tributada sin permiso de crédito y con cobro del ICMS por Sustitución Tributaria'),
    (u'203', u'203 - Exención del ICMS para rango de ingreso bruto y con cobro del ICMS por Sustitución Tributaria'),
    (u'300', u'300 - Inmune'),
    (u'400', u'400 - No tributada'),
    (u'500', u'500 - ICMS cobrado anteriormente por sustitución tributaria (sustituido) o por anticipación.'),
    (u'900', u'900 - Otros'),
)

MOD_BCST_ESCOLHAS = (
    (u'0', u'0 - Precio tabulado o máximo sugerido'),
    (u'1', u'1 - Lista Negativa (valor)'),
    (u'2', u'2 - Lista Positiva (valor)'),
    (u'3', u'3 - Lista Neutra (valor)'),
    (u'4', u'4 - Margen de Valor Agregado (%)'),
    (u'5', u'5 - Pauta (valor)'),
)

MOD_BC_ESCOLHAS = (
    (u'0', u'0 - Margen de Valor Agregado (%)'),
    (u'1', u'1 - Pauta (Valor)'),
    (u'2', u'2 - Precio Tabulado Máx. (valor)'),
    (u'3', u'3 - Valor de la operación'),
)

MOT_DES_ICMS = (
    (u'1', u'1 - Taxi'),
    (u'3', u'3 - Productor Agropecuario'),
    (u'4', u'4 - Flotista/Arrendadora'),
    (u'5', u'5 - Diplomático/Consular'),
    (u'6', u'6 - Utilitarios y Motocicletas de la Amazonia Occidental y Áreas de Libre Comercio'),
    (u'7', u'7 - SUFRAMA'),
    (u'8', u'8 - Venta a Órgano Público'),
    (u'9', u'9 - Otros'),
    (u'10', u'10 - Deficiente Conductor'),
    (u'11', u'11 - Deficiente No Conductor'),
    (u'12', u'12 - Órgano de fomento y desarrollo agropecuario'),
    (u'16', u'16 - Olimpiadas Río 2016'),
)

P_ICMS_INTER_ESCOLHAS = (
    (Decimal('4.00'), u'4% alícuota interestatal para productos importados'),
    (Decimal('7.00'), u'7% para los Estados de origen del Sur y Sudeste (excepto ES), destinado para los Estados del Norte, Nordeste, Centro-Oeste y Espírito Santo'),
    (Decimal('12.00'), u'12% para los demás casos'),
)

P_ICMS_INTER_PART_ESCOLHAS = (
    (Decimal('40.00'), u'40% en 2016'),
    (Decimal('60.00'), u'60% en 2017'),
    (Decimal('80.00'), u'80% en 2018'),
    (Decimal('100.00'), u'100% a partir de 2019'),
)

REGIME_TRIB_ESCOLHAS = (
    (u'0', u'Tributación Normal'),
    (u'1', u'Simples Nacional'),
)

TIPO_IPI = (
    (u'0', u'No sujeto al IPI'),
    (u'1', u'Valor fijo'),
    (u'2', u'Alícuota'),
)


class GrupoFiscal(models.Model):
    descricao = models.CharField(max_length=255)
    regime_trib = models.CharField(max_length=1, choices=REGIME_TRIB_ESCOLHAS)

    class Meta:
        verbose_name = "Grupo Fiscal"

    def __unicode__(self):
        s = u'%s' % (self.descricao)
        return s

    def __str__(self):
        s = u'%s' % (self.descricao)
        return s


class ICMS(models.Model):
    # Nota Fiscal
    cst = models.CharField(
        max_length=3, choices=CST_ICMS_ESCOLHAS, help_text='icms-cst')
    mod_bc = models.CharField(max_length=1, choices=MOD_BC_ESCOLHAS, default='3',
                              help_text='icms00 icms10 icms20 icms51 icms70 icms90 icms10p icms90p')
    p_icms = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                 help_text='icms00 icms10 icms20 icms51 icms70 icms90 icms10p icms90p')
    p_red_bc = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                   help_text='icms20 icms51 icms70 icms90 icms10p icms90p')
    mod_bcst = models.CharField(max_length=1, choices=MOD_BCST_ESCOLHAS, default='4',
                                help_text='icms10 icms30 icms70 icms90 icms10p icms90p')
    p_mvast = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                  help_text='icms10 icms30 icms70 icms90 icms10p icms90p')
    p_red_bcst = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                     help_text='icms10 icms30 icms70 icms90 icms10p icms90p')
    p_icmsst = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                   help_text='icms10 icms30 icms70 icms90 icms10p icms90p')
    mot_des_icms = models.CharField(max_length=3, choices=MOT_DES_ICMS, null=True, blank=True,
                                    help_text='icms20 icms30 icms40 icms41 icms50 icms70 icms90')
    p_dif = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                help_text='icms51')
    p_bc_op = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                  help_text='icms10p icms90p')
    ufst = models.CharField(max_length=2, choices=UF_SIGLA, null=True, blank=True,
                            help_text='icms10p icms90p')
    grupo_fiscal = models.ForeignKey(
        'fiscal.GrupoFiscal', related_name="icms_padrao", on_delete=models.CASCADE, null=True, blank=True)

    # Calculo do imposto
    icms_incluido_preco = models.BooleanField(
        default=False, help_text='calculo-icms')
    icmsst_incluido_preco = models.BooleanField(
        default=False, help_text='calculo-icms')


class ICMSUFDest(models.Model):
    p_fcp_dest = models.DecimalField(max_digits=6, decimal_places=2, validators=[
                                     MinValueValidator(Decimal('0.00'))], null=True, blank=True)
    p_icms_dest = models.DecimalField(max_digits=6, decimal_places=2, validators=[
                                      MinValueValidator(Decimal('0.00'))], null=True, blank=True)
    p_icms_inter = models.DecimalField(max_digits=6, decimal_places=2, validators=[
                                       MinValueValidator(Decimal('0.00'))], choices=P_ICMS_INTER_ESCOLHAS, null=True, blank=True)
    p_icms_inter_part = models.DecimalField(max_digits=6, decimal_places=2, validators=[
                                            MinValueValidator(Decimal('0.00'))], choices=P_ICMS_INTER_PART_ESCOLHAS, null=True, blank=True)
    grupo_fiscal = models.ForeignKey(
        'fiscal.GrupoFiscal', related_name="icms_dest_padrao", on_delete=models.CASCADE, null=True, blank=True)


class ICMSSN(models.Model):
    csosn = models.CharField(
        max_length=3, choices=CSOSN_ESCOLHAS, help_text='icmssn-csosn')
    p_cred_sn = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                    help_text='icmssn101 icmssn201 icmssn900')
    mod_bc = models.CharField(max_length=1, choices=MOD_BC_ESCOLHAS, default='3',
                              help_text='icmssn900')
    mod_bcst = models.CharField(max_length=1, choices=MOD_BCST_ESCOLHAS, default='4',
                                help_text='icmssn201 icmssn202 icmssn203 icmssn900')
    p_mvast = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                  help_text='icmssn201 icmssn202 icmssn203 icmssn900')
    p_red_bcst = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                     help_text='icmssn201 icmssn202 icmssn203 icmssn900')
    p_icmsst = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                   help_text='icmssn201 icmssn202 icmssn203 icmssn900')
    p_red_bc = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                   help_text='icmssn201 icmssn202 icmssn203 icmssn900')
    p_icms = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True, blank=True,
                                 help_text='icmssn201 icmssn202 icmssn203 icmssn900')
    grupo_fiscal = models.ForeignKey(
        'fiscal.GrupoFiscal', related_name="icms_sn_padrao", on_delete=models.CASCADE, null=True, blank=True)

    # Calculo do imposto
    icmssn_incluido_preco = models.BooleanField(
        default=False, help_text='calculo-icmssn')
    icmssnst_incluido_preco = models.BooleanField(
        default=False, help_text='calculo-icmssn')


class IPI(models.Model):
    cst = models.CharField(
        max_length=2, choices=CST_IPI_ESCOLHAS, null=True, blank=True)
    cl_enq = models.CharField(max_length=5, null=True, blank=True)
    c_enq = models.CharField(max_length=3, null=True, blank=True)
    cnpj_prod = models.CharField(max_length=32, null=True, blank=True)
    tipo_ipi = models.CharField(max_length=1, choices=TIPO_IPI, default='2')
    p_ipi = models.DecimalField(max_digits=6, decimal_places=2, validators=[
                                MinValueValidator(Decimal('0.00'))], null=True, blank=True)
    valor_fixo = models.DecimalField(max_digits=13, decimal_places=2, validators=[
                                     MinValueValidator(Decimal('0.00'))], null=True, blank=True)  # Caso IPI for valor fixo
    grupo_fiscal = models.ForeignKey(
        'fiscal.GrupoFiscal', related_name="ipi_padrao", on_delete=models.CASCADE, null=True, blank=True)

    # Calculo do imposto
    ipi_incluido_preco = models.BooleanField(
        default=False, help_text='calculo-ipi')
    incluir_bc_icms = models.BooleanField(
        default=False, help_text='calculo-ipi')
    incluir_bc_icmsst = models.BooleanField(
        default=False, help_text='calculo-ipi')

    def get_cnpj_prod_apenas_digitos(self):
        return re.sub('[./-]', '', self.cnpj_prod)


class PIS(models.Model):
    cst = models.CharField(
        max_length=2, choices=CST_PIS_COFINS_ESCOLHAS, null=True, blank=True)
    p_pis = models.DecimalField(max_digits=5, decimal_places=2, validators=[
                                MinValueValidator(Decimal('0.00'))], null=True, blank=True)
    valiq_pis = models.DecimalField(max_digits=13, decimal_places=2, validators=[
                                    MinValueValidator(Decimal('0.00'))], null=True, blank=True)
    grupo_fiscal = models.ForeignKey(
        'fiscal.GrupoFiscal', related_name="pis_padrao", on_delete=models.CASCADE, null=True, blank=True)


class COFINS(models.Model):
    cst = models.CharField(
        max_length=2, choices=CST_PIS_COFINS_ESCOLHAS, null=True, blank=True)
    p_cofins = models.DecimalField(max_digits=5, decimal_places=2, validators=[
                                   MinValueValidator(Decimal('0.00'))], null=True, blank=True)
    valiq_cofins = models.DecimalField(max_digits=13, decimal_places=2, validators=[
                                       MinValueValidator(Decimal('0.00'))], null=True, blank=True)
    grupo_fiscal = models.ForeignKey(
        'fiscal.GrupoFiscal', related_name="cofins_padrao", on_delete=models.CASCADE, null=True, blank=True)


# class ISSQN(models.Model):
