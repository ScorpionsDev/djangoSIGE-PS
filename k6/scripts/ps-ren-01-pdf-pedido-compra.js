import http from 'k6/http';
import { check, sleep } from 'k6';
import { login, BASE } from './utils/auth.js';

const PEDIDO_ID = 24; // pedido de compra existente, status '4' (Recebido)

export const options = {
  vus: 1,
  iterations: 5,
  thresholds: {
    'http_req_duration{name:GenerarPDFPedidoCompra}': ['p(95)<5000'],
  },
};

export default function () {
  const csrf = login();

  const res = http.get(`${BASE}/compras/gerarpdfpedidocompra/${PEDIDO_ID}/`, {
    headers: { Cookie: `csrftoken=${csrf}` },
    tags: { name: 'GenerarPDFPedidoCompra' },
  });

  check(res, {
    'PDF generado (200)': (r) => r.status === 200,
    'es un PDF': (r) => r.headers['Content-Type'] === 'application/pdf',
    'bajo 5 segundos': (r) => r.timings.duration < 5000,
  });

  sleep(1);
}
