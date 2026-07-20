import http from 'k6/http';
import { check } from 'k6';
import { login, BASE } from './utils/auth.js';

export const options = { vus: 1, iterations: 1 };

export default function () {
  const csrf = login();
  console.log('Login OK, csrf:', csrf);

  const res = http.get(`${BASE}/`, {
    headers: { Cookie: `csrftoken=${csrf}` },
  });

  check(res, { 'home carga (200)': (r) => r.status === 200 });
}
