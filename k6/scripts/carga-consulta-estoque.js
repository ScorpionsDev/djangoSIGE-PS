import http from 'k6/http';
import { check, sleep } from 'k6';
import { login, BASE } from './utils/auth.js';

export const options = {
  scenarios: {
    carga_gradual: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 5 },   // sube a 5 usuarios concurrentes
        { duration: '20s', target: 10 },  // sube a 10
        { duration: '20s', target: 10 },  // sostiene 10
        { duration: '10s', target: 0 },   // baja a 0
      ],
    },
  },
  thresholds: {
    'http_req_duration{name:ConsultaEstoqueCarga}': ['p(95)<3000'],
    'http_req_failed': ['rate<0.01'], // menos de 1% de errores
  },
};

export default function () {
  const csrf = login();

  const res = http.get(`${BASE}/estoque/consultaestoque/`, {
    headers: { Cookie: `csrftoken=${csrf}` },
    tags: { name: 'ConsultaEstoqueCarga' },
  });

  check(res, {
    'pantalla carga (200)': (r) => r.status === 200,
    'sin timeout ni 500': (r) => r.status < 500,
  });

  sleep(Math.random() * 2 + 1); // simula "pensar" entre 1-3s, más realista
}
