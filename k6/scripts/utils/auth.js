import http from 'k6/http';

const BASE_URL = 'http://127.0.0.1:8000';
const USERNAME = 'eduardo';
const PASSWORD = '123';

export function login() {
  const jar = http.cookieJar();

  const loginPage = http.get(`${BASE_URL}/login/`);
  const csrfCookie = jar.cookiesForURL(loginPage.url)['csrftoken'][0];

  const res = http.post(`${BASE_URL}/login/`, {
    csrfmiddlewaretoken: csrfCookie,
    username: USERNAME,
    password: PASSWORD,
  }, {
    headers: { 'Referer': `${BASE_URL}/login/` },
  });

  if (res.status !== 200 && res.status !== 302) {
    throw new Error(`Login falló: ${res.status}`);
  }

  return jar.cookiesForURL(loginPage.url)['csrftoken'][0];
}

export const BASE = BASE_URL;
