import http from 'k6/http';
import { check, sleep } from 'k6';
import { login, BASE } from './utils/auth.js';

const PRODUCTO_ID = 1;
const LOCAL_DEST_ID = 1;
const N_ENTRADAS = 50;
const CANTIDAD = 5.00;
const VALOR_UNIT = 10.00;
const SUBTOTAL = (CANTIDAD * VALOR_UNIT).toFixed(2).replace('.', ',');

export const options = {
  vus: 1,
  iterations: 1,
  thresholds: {
    'http_req_duration{name:CrearEntradaEstoque}': ['p(95)<5000'],
  },
};

function hoy() {
  const d = new Date();
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}/${mm}/${yyyy}`;
}

export default function () {
  const csrf = login();
  let exitosas = 0;
  let fallidas = 0;

  for (let i = 1; i <= N_ENTRADAS; i++) {
    const payload = {
      csrfmiddlewaretoken: csrf,
      data_movimento: hoy(),
      quantidade_itens: '1',
      valor_total: SUBTOTAL,
      observacoes: `PS-VOL-03 k6 fixture #${i}`,
      tipo_movimento: '0',
      pedido_compra: '',
      fornecedor: '',
      local_dest: String(LOCAL_DEST_ID),

      'itens_form-TOTAL_FORMS': '1',
      'itens_form-INITIAL_FORMS': '0',
      'itens_form-MIN_NUM_FORMS': '0',
      'itens_form-MAX_NUM_FORMS': '1000',

      'itens_form-0-produto': String(PRODUCTO_ID),
      'itens_form-0-quantidade': `${CANTIDAD.toFixed(2).replace('.', ',')}`,
      'itens_form-0-valor_unit': `${VALOR_UNIT.toFixed(2).replace('.', ',')}`,
      'itens_form-0-subtotal': SUBTOTAL,
    };

    const res = http.post(`${BASE}/estoque/movimento/adicionarentrada/`, payload, {
      headers: {
        Cookie: `csrftoken=${csrf}`,
        'Referer': `${BASE}/estoque/movimento/adicionarentrada/`,
      },
      tags: { name: 'CrearEntradaEstoque' },
      redirects: 0,
    });

    sleep(0.3);

    const ok = check(res, {
      'entrada guardada (302)': (r) => r.status === 302,
    });

    if (ok) {
      exitosas++;
    } else {
      fallidas++;
      if (i === 1) {
        // Vuelca el HTML solo de la primera falla, para depurar sin llenar el log
        console.log('STATUS inesperado en entrada #1:', res.status);
        console.log(res.body.substring(0, 2000));
      }
    }
  }

  console.log(`Entradas exitosas: ${exitosas} / ${N_ENTRADAS}`);
  console.log(`Entradas fallidas: ${fallidas} / ${N_ENTRADAS}`);
  console.log(`Incremento esperado en estoque_atual: ${(CANTIDAD * N_ENTRADAS).toFixed(2)}`);

  sleep(1);
}