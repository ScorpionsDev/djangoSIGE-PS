import http from 'k6/http';
import { check, sleep } from 'k6';
import { login, BASE } from './utils/auth.js';

const FORNECEDOR_ID = 18;
const LOCAL_DEST_ID = 1;
const N_ITEMS = 30; // exactamente 30, como pide PS-VOL-01
const PRODUCTO_IDS = Array.from({ length: N_ITEMS }, (_, i) => (i % 52) + 1); // ciclo sobre los 52 productos reales

const VALOR_UNIT = 10.00;
const CANTIDAD = 2;
const SUBTOTAL_ITEM = (VALOR_UNIT * CANTIDAD).toFixed(2).replace('.', ',');
const VALOR_TOTAL = (VALOR_UNIT * CANTIDAD * N_ITEMS).toFixed(2).replace('.', ',');

export const options = {
  vus: 1,
  iterations: 1,
  thresholds: {
    'http_req_duration{name:GuardarPedidoCompra30Items}': ['p(95)<5000'],
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
    [`${p}subtotal`]: SUBTOTAL_ITEM,
    [`${p}vicms`]: '0,00',
    [`${p}vipi`]: '0,00',
    [`${p}p_icms`]: '0,00',
    [`${p}p_ipi`]: '0,00',
    [`${p}auto_calcular_impostos`]: 'on',
  };
}

export default function () {
  const csrf = login();

  let payload = {
    csrfmiddlewaretoken: csrf,
    data_emissao: '19/07/2026',
    data_entrega: '19/07/2026',
    fornecedor: String(FORNECEDOR_ID),
    mod_frete: '9',
    desconto: '0,00',
    tipo_desconto: '0',
    frete: '0,00',
    despesas: '0,00',
    local_dest: String(LOCAL_DEST_ID),
    seguro: '0,00',
    total_ipi: '0,00',
    total_icms: '0,00',
    valor_total: VALOR_TOTAL,
    observacoes: 'PS-VOL-01 k6 fixture 30 items',
    status: '0',

    'produtos_form-TOTAL_FORMS': String(N_ITEMS),
    'produtos_form-INITIAL_FORMS': '0',
    'produtos_form-MIN_NUM_FORMS': '0',
    'produtos_form-MAX_NUM_FORMS': '1000',

    'pagamento_form-TOTAL_FORMS': '0',
    'pagamento_form-INITIAL_FORMS': '0',
    'pagamento_form-MIN_NUM_FORMS': '0',
    'pagamento_form-MAX_NUM_FORMS': '1000',
  };

  PRODUCTO_IDS.forEach((productoId, index) => {
    Object.assign(payload, buildItemFields(index, productoId));
  });

  const res = http.post(`${BASE}/compras/pedidocompra/adicionar/`, payload, {
    headers: {
      Cookie: `csrftoken=${csrf}`,
      'Referer': `${BASE}/compras/pedidocompra/adicionar/`,
    },
    tags: { name: 'GuardarPedidoCompra30Items' },
    redirects: 0,
  });

  console.log('STATUS:', res.status, '| items enviados:', N_ITEMS, '| total esperado:', VALOR_TOTAL);

  check(res, {
    'guardado sin error (302)': (r) => r.status === 302,
    'bajo 5 segundos': (r) => r.timings.duration < 5000,
  });

  sleep(1);
}