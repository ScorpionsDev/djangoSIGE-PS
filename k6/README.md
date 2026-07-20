# k6/README.md

## Pruebas de rendimiento y volumen — djangoSIGE (Pruebas de Sistema)

Scripts k6 usados para ejecutar los casos PS-REN (Rendimiento) y PS-VOL (Volumen)
del Informe de Ejecución de Pruebas de Sistema. Ver el informe completo para el
detalle de cada caso, resultado esperado/obtenido y evidencia.

## Requisitos previos

### 1. Instalar k6
```bash
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
    sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### 2. Poblar la base de datos base del proyecto (solo en un entorno nuevo)

⚠️ **`--clear` borra en cascada** `Produto`, `Fornecedor` y `Cliente`, y con
ellos **todo** lo que dependa de esas tablas por FK con `on_delete=CASCADE`:
pedidos de compra (`Compra`, `ItensCompra`), pedidos de venta (`Venda`,
`ItensVenda`) y movimientos de estoque (`ItensMovimento`). **Nunca correr
`--clear` sobre un entorno que ya tenga pedidos o movimientos de prueba
cargados** — se pierde todo sin advertencia adicional del comando.

En un entorno nuevo (base de datos recién migrada, sin datos de negocio aún):
```bash
cd ~/Pruebas_Software/djangoSIGE-PS
python manage.py create_data --clear --seed 1 \
    --clientes 30 --fornecedores 16 --produtos 50
```
Esto genera de forma reproducible: 30 clientes, 16 fornecedores, 50 productos
(además de los defaults fijos de empresas/transportadoras/categorías/marcas/
unidades). Confirmar el resultado con:
```bash
python manage.py shell -c "
from djangosige.apps.cadastro.models import Fornecedor, Produto, Cliente
print('Fornecedores:', Fornecedor.objects.count())
print('Productos:', Produto.objects.count())
print('Clientes:', Cliente.objects.count())
"
```

**Nota sobre el entorno usado en este informe:** la base de datos de este
ciclo de pruebas se generó corriendo `create_data` (defaults) **dos veces sin
`--clear`**, de forma no intencional, lo cual duplicó fornecedores y clientes
(8→16, 15→30) y productos (25→50). Además tiene 2 productos creados
manualmente (id=51 "Producto de prueba", id=52 "prueba"), sin relevancia
funcional. El `--seed` usado no quedó registrado, por lo que **este entorno
específico no es reproducible byte a byte** — el comando `--clear --seed 1`
de arriba es la vía recomendada para nuevos entornos, no una reconstrucción
exacta del entorno original.

### 3. Cargar el fixture de local de estoque por defecto
```bash
python manage.py loaddata djangosige/fixtures/estoque_initial_data.json
```
Esto crea únicamente `LocalEstoque` id=1 ("Estoque Padrão").

### 4. Crear locales de estoque adicionales (manual)
Las pruebas de este informe (ej. PS-INT-03, transferencias entre locales)
requieren al menos 2 locales adicionales, creados manualmente vía UI o shell:
```bash
python manage.py shell -c "
from djangosige.apps.estoque.models import LocalEstoque
LocalEstoque.objects.get_or_create(descricao='Local A')
LocalEstoque.objects.get_or_create(descricao='Local B')
"
```

### 5. Generar el fixture de volumen (pedidos y movimientos de estoque)
Comando propio agregado para este ciclo de pruebas (no viene con el proyecto base):
```bash
python manage.py generar_fixtures_volumen --pedidos 100 --movimientos 200
```
Requiere que ya existan productos, fornecedores y al menos 1 local de estoque
(pasos 2-4). Ver `djangosige/apps/estoque/management/commands/generar_fixtures_volumen.py`.

⚠️ No es idempotente respecto al total pedido: el comando **agrega** hasta
alcanzar el total indicado, partiendo de lo que ya exista. Correrlo varias
veces con el mismo número no duplica de más, pero si ya hay más registros
que el total pedido, no elimina el excedente.

### 6. Confirmar credenciales de usuario en los scripts
Los scripts autentican contra un usuario existente, hardcodeado en
`scripts/utils/auth.js` (`eduardo` / `123` en este entorno). Ajustar antes
de correr contra otro entorno.

## Ejecutar un script individual
```bash
cd ~/Pruebas_Software/djangoSIGE-PS/k6
k6 run scripts/ps-ren-01-pdf-pedido-compra.js
```

## Scripts disponibles

| Script | Caso de prueba | Descripción |
| :--- | :--- | :--- |
| `00-smoke-test.js` | — | Sanity check: login + carga de home |
| `ps-ren-01-pdf-pedido-compra.js` | PS-REN-01 | Generación de PDF de pedido de compra |
| `ps-ren-02-consulta-estoque.js` | PS-REN-02 | Carga de `consultaestoque` (usuario único) |
| `carga-consulta-estoque.js` | PS-REN-02 (complemento) | Carga de `consultaestoque` con rampa de 1-10 VUs |
| `ps-ren-03-listado-pedidos.js` | PS-REN-03 | Listado de pedidos de compra |
| `ps-ren-04-guardar-pedido-venta.js` | PS-REN-04 | Guardado de pedido de venta con 20 ítems |
| `ps-vol-01-pedido-compra-30-items.js` | PS-VOL-01 | Pedido de compra con 30 ítems |
| `ps-vol-02-pedido-venta-30-items.js` | PS-VOL-02 | Pedido de venta con 30 ítems |
| `ps-vol-03-50-entradas-mismo-producto.js` | PS-VOL-03 | 50 entradas sobre el mismo producto (ver DEF-004 en el informe) |
| `ps-vol-04-listado-movimientos.js` | PS-VOL-04 | Listado de movimientos de estoque |

## Notas importantes

- **DEF-004** (condición de carrera en `estoque_atual`, ver Sección 8 del
  informe) fue descubierto ejecutando `ps-vol-03-50-entradas-mismo-producto.js`
  sin pausas entre peticiones. El script incluye por defecto el escenario
  que reproduce el defecto (sin `sleep` entre POSTs).
- `ps-vol-01` y `ps-vol-02` crean registros nuevos cada vez que se ejecutan
  (pedidos de compra/venta reales); no son idempotentes.
- Los scripts asumen IDs específicos de la base de datos de prueba usada en
  este ciclo (ej. `FORNECEDOR_ID = 18`, `CLIENTE_ID = 3`, `PRODUCTO_ID = 1`).
  Ajustar las constantes al inicio de cada script si se corre contra otro entorno.