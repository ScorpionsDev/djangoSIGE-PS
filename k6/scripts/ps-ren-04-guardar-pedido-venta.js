import http from 'k6/http';
import { check, sleep } from 'k6';
import { login, BASE } from './utils/auth.js';

const CLIENTE_ID = 3;
const N_ITEMS = 20;
const PRODUCTO_IDS = Array.from({ length: N_ITEMS }, (_, i) => i + 1);
const VALOR_UNIT = 10.00;
const CANTIDAD = 2;
const SUBTOTAL_ITEM = (VALOR_UNIT * CANTIDAD).toFixed(2).replace('.', ',');
const VALOR_TOTAL = (VALOR_UNIT * CANTIDAD * N_ITEMS).toFixed(2).replace('.', ',');

export const options = {
  vus: 1,
  iterations: 5,
  thresholds: {
    'http_req_duration{name:GuardarPedidoVenta}': ['p(95)<4000'],
  },
};

function buildItemFields(index, productoId) {
  const p = `produtos_form-${index}-`;
  return {
    [`${p}produto`]: String(productoId),
    [`${p}quantidade`]: `${CANTIDAD},00`,
    [`${p}valor_unit`]: VALOR_UNIT.toFixed(2).replace('.', ','),
    [`${p}tipo_desconto`]: '0',
    [`${p}desconto`]: '0,00',
    [`${p}valor_rateio_frete`]: '0,00',
    [`${p}valor_rateio_despesas`]: '0,00',
    [`${p}valor_rateio_seguro`]: '0,00',
    [`${p}vbc_icms`]: '0,00',
    [`${p}vbc_icms_st`]: '0,00',
    [`${p}vbc_ipi`]: '0,00',
    [`${p}subtotal`]: SUBTOTAL_ITEM,
    [`${p}vicms`]: '0,00',
    [`${p}vicms_st`]: '0,00',
    [`${p}vipi`]: '0,00',
    [`${p}p_icms`]: '0,00',
    [`${p}p_ipi`]: '0,00',
    [`${p}p_icmsst`]: '0,00',
    [`${p}vfcp`]: '0,00',
    [`${p}vicmsufdest`]: '0,00',
    [`${p}vicmsufremet`]: '0,00',
    [`${p}auto_calcular_impostos`]: 'on',
  };
}

function buildPayload(csrf) {
  let payload = {
    csrfmiddlewaretoken: csrf,
    data_emissao: '19/07/2026',
    cliente: String(CLIENTE_ID),
    status: '0',
    local_orig: '1',
    mod_frete: '9',
    desconto: '0,00',
    tipo_desconto: '0',
    frete: '0,00',
    despesas: '0,00',
    seguro: '0,00',
    impostos: '0,00',
    valor_total: VALOR_TOTAL,
    observacoes: 'Carga de rendimiento k6 - PS-REN-04',
    total_sem_imposto: VALOR_TOTAL,

    'produtos_form-TOTAL_FORMS': String(N_ITEMS),
    'produtos_form-INITIAL_FORMS': '0',
    'produtos_form-MIN_NUM_FORMS': '0',
    'produtos_form-MAX_NUM_FORMS': '1000',

    'pagamento_form-TOTAL_FORMS': '0',
    'pagamento_form-INITIAL_FORMS': '0',
    'pagamento_form-MIN_NUM_FORMS': '0',
    'pagamento_form-MAX_NUM_FORMS': '1000',
  };

  PRODUCTO_IDS.forEach((prodId, idx) => {
    payload = Object.assign(payload, buildItemFields(idx, prodId));
  });

  return payload;
}

export default function () {
  const csrf = login();

  // redirects: 'manual' para medir el POST real sin que k6 siga el 302
  // y así el status y el tiempo reflejen exactamente el guardado del servidor
  const res = http.post(
    `${BASE}/vendas/pedidovenda/adicionar/`,
    buildPayload(csrf),
    {
      headers: {
        Cookie: `csrftoken=${csrf}`,
        Referer: `${BASE}/vendas/pedidovenda/adicionar/`,
      },
      redirects: 0, // no seguir el redirect, para medir el 302 real del guardado
      tags: { name: 'GuardarPedidoVenta' },
    }
  );

  check(res, {
    'guardado correctamente (302)': (r) => r.status === 302,
    'bajo 4 segundos': (r) => r.timings.duration < 4000,
  });

  if (res.status !== 302) {
    console.log(`tatus inesperado: ${res.status} (esperado 302)`);
  }

  sleep(1);
}
