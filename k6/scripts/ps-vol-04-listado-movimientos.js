import http from 'k6/http';
import { check, sleep } from 'k6';
import { login, BASE } from './utils/auth.js';

export const options = {
  vus: 1,
  iterations: 5,
  thresholds: {
    'http_req_duration{name:ListadoMovimientosEstoque}': ['p(95)<3000'],
  },
};

export default function () {
  const csrf = login();

  const res = http.get(`${BASE}/estoque/movimentos/`, {
    headers: { Cookie: `csrftoken=${csrf}` },
    tags: { name: 'ListadoMovimientosEstoque' },
  });

  const bodyLen = res.body ? res.body.length : 0;

  check(res, {
    'listado carga (200)': (r) => r.status === 200,
    'bajo 3 segundos': (r) => r.timings.duration < 3000,
    'respuesta no vacía': () => bodyLen > 0,
  });

  console.log(`STATUS: ${res.status} | duración: ${res.timings.duration.toFixed(2)}ms | tamaño body: ${bodyLen} bytes`);

  sleep(1);
}