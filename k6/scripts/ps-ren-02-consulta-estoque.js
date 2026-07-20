import http from 'k6/http';
import { check, sleep } from 'k6';
import { login, BASE } from './utils/auth.js';

export const options = {
  vus: 1,
  iterations: 5,
  thresholds: {
    'http_req_duration{name:ConsultaEstoque}': ['p(95)<3000'],
  },
};

export default function () {
  const csrf = login();

  const res = http.get(`${BASE}/estoque/consultaestoque/`, {
    headers: { Cookie: `csrftoken=${csrf}` },
    tags: { name: 'ConsultaEstoque' },
  });

  check(res, {
    'pantalla carga (200)': (r) => r.status === 200,
    'bajo 3 segundos': (r) => r.timings.duration < 3000,
  });

  sleep(1);
}
