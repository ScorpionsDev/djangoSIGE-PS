# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Changed

- **Menu lateral reorganizado (#109).** Bloco `.user-info` compactado
  (avatar 36px à esquerda + nome/email à direita, no lugar dos 135px
  fixos com avatar grande); rodapé `.legal` centralizado; `.menu`
  passa a usar `flex: 1 1 auto` em vez de altura fixa de 450px que
  sobrava ou estourava conforme a tela. Chevron do dropdown do
  usuário reposicionado no canto direito da linha (sem sobrepor o
  nome) e elevado para `z-index: 9999` para abrir acima dos itens
  do menu. Todas as mudanças vivem num bloco isolado no final de
  `djangosige/static/css/style.css`; o HTML do `base.html` continua
  intacto.
- **Geração de PDF migrada de `geraldo` para [WeasyPrint](https://weasyprint.org/)
  (#142).** Reports do `geraldo` (`report_vendas.py`, `report_compras.py`,
  baseados em `ReportBand`/`SubReport` posicionados em centímetros) foram
  substituídos por um único template HTML/CSS reaproveitável em
  `djangosige/apps/base/templates/base/pdf/relatorio_documento.html`. As
  views `GerarPDFVenda`/`GerarPDFCompra` agora renderizam o template via
  `render_to_string()` e geram o PDF com `weasyprint.HTML(...).write_pdf()`.
  Dependências de sistema do WeasyPrint (`libpango-1.0-0`, `libpangoft2-1.0-0`,
  `libcairo2`, `libgdk-pixbuf-2.0-0`, `libharfbuzz0b`, `libfontconfig1`)
  adicionadas ao `Dockerfile`. Os 4 testes que estavam marcados como
  `@unittest.skip` por causa do geraldo foram reabilitados.
- Bumps de dependências:
  - `dj-database-url` 0.5.0 → 3.1.2 (cinco anos de bumps acumulados).
  - `python-decouple` 3.1 → 3.8 (API do `Csv()` mantida).
  - `flake8` (dev) 3.6.0 → 7.3.0, com `pyflakes`, `pycodestyle` e
    `mccabe` correspondentes.
  - `asgiref`, `sqlparse`, `pillow` já estavam no patch mais recente
    compatível.
- `requirements.txt` agora é gerado via `uv export` (sincronizado com
  `uv.lock`).
- `pyproject.toml` reorganizado em três grupos comentados: stack de
  NFe (pinada em versões antigas, ver nota abaixo), PDF (WeasyPrint) e
  runtime geral. Pins explícitos de `future`, `six`, `eight` e `pytz`
  removidos — continuam disponíveis como deps transitivas.
- `mock` removido das deps de dev (não havia uso nos testes — Python 3
  traz `unittest.mock` builtin).
- Afrouxa constraints de `lxml` (`>=4.9,<5` — teto necessário porque
  `signxml==2.5.2` exige `lxml<5`) e `reportlab` (`>=4.5`). Sem efeito
  em versões instaladas no momento; permite patches futuros sem
  alteração no `pyproject`.
- Constraint do `Django` afrouxada para `>=5.2,<5.3` (linha LTS).
  Versão instalada continua `5.2.14`. Bump para 6.x fica para rodada
  separada após validação.
- Python atualizado de 3.10 para 3.12 (`.python-version`, `pyproject`
  e `Dockerfile`). Bump para 3.13 ficou bloqueado pelo conflito entre
  `lxml<5` (exigido por `signxml==2.5.2`, parte do stack pinado de
  NFe) e o fato de `lxml 4.x` não compilar com a API do CPython 3.13.
  Stack validado em container Docker (rebuild da imagem com
  `python:3.12-slim`, smoke test em `/login/`, `/` e `/static/*`
  retornando OK).
- README atualizado: seção "Dependências" reflete Python 3.12, Django
  5.2 LTS, uv como gerenciador recomendado, PostgreSQL 18 (Docker),
  WeasyPrint como gerador de PDF e nota sobre o pin do stack de NFe.
- Substituído `locale.format()` (removido no Python 3.12) por
  `locale.format_string()` em 68 ocorrências (apps de vendas, compras,
  estoque, financeiro e testes). Assinatura idêntica, sem mudança de
  comportamento.
- `requirements.txt` passa a ser gerado via `uv export`, sincronizado
  com `uv.lock`.
- `djangosige.__init__.__version__` passa a `'2.0'` (estava em `'0.0.1'`,
  desalinhado com a release v2.0.0). Template `base.html` volta a usar
  `{{versao}}` (context processor `sige_version` já existente).

### Fixed

- **Segurança: 8 views AJAX `Info*` passavam pelo Django sem checagem
  de permissão (#143, HIGH).** `InfoCliente`, `InfoFornecedor`,
  `InfoEmpresa`, `InfoTransportadora`, `InfoProduto`, `InfoVenda`,
  `InfoCompra` e `InfoCondicaoPagamento` herdavam de
  `django.views.generic.View` em vez de `CustomView`, bypassando o
  `CheckPermissionMixin`. Qualquer usuário autenticado conseguia ler
  dados sensíveis (CPF, CNPJ, RG, endereços, preços, condições de
  pagamento) só com o id do registro. Cada view agora herda de
  `CustomView` e exige a permissão `view_<modelo>` correspondente.
  Regressão coberta por `djangosige/tests/test_security_ajax_views.py`
  (8 testes). Demais achados da issue (state-changing via GET,
  bulk-delete sem ownership check) seguem em aberto.
- **Importação de NF-e v4.0 quebrava com `NOT NULL constraint failed:
  fiscal_notafiscal.dhemi` (#122).** Quando o XML não trazia `<dhEmi>`
  legível, o `pysignfe` devolvia `None` para `nfe.infNFe.ide.dhEmi.valor`
  e o `save()` da `NotaFiscalSaida`/`NotaFiscalEntrada` violava o NOT
  NULL. Em `processador_nf.py`, ambos `importar_xml_cliente` e
  `importar_xml_fornecedor` agora caem para `datetime.now()` quando o
  valor do XML for ausente — mesmo fallback que já era usado no caminho
  de criação manual da nota. Testes de regressão em
  `djangosige/tests/fiscal/test_processador_nf.py`.
  {% raw %}
- Templates de listagem usavam `{% ifequal %}` / `{% endifequal %}`,
  tags removidas no Django 4.0. As 5 ocorrências
  (`cliente_list_table.html`, `fornecedor_list_table.html`,
  `transportadora_list_table.html`, `empresa_list_table.html` e
  `estoque/consulta/consulta_estoque.html` — 2 vezes) foram substituídas
  por `{% if A == B %}…{% endif %}`.
  {% endraw %}
- Login retornava `403 Forbidden (Origin checking failed)` sob proxy
  reverso (`nginx` em `8000:80` → `gunicorn`). Adicionado
  `CSRF_TRUSTED_ORIGINS` no `settings.py` (lido via `decouple`) e a env
  `CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000` no
  `docker-compose.yml`.
- Rodapé do template `base/base.html`: ano `2017` → `2026` e versão
  (antes era o placeholder `{{versao}}` que renderizava vazio por falta
  de context processor) → `2.0`.

### Changed

- README ganhou seção "Comandos úteis" do Docker com exemplos de
  `docker exec -it`, `docker compose logs -f --tail=N` e atalhos
  (`ps`, `restart`, `down`). Inclui nota explícita sobre a ordem das
  flags `-it` (precisam vir antes do nome do container).

### Added

- `database/` adicionado ao `.gitignore`. O volume do postgres é criado
  como `root` pelo container e fazia `git status` emitir `Permissão
  negada` em todo comando.

## [2.0.0] - 2026-05-23

Modernização da infraestrutura de build e execução. A aplicação em si não
mudou — esta release foca em como instalar, rodar e empacotar o projeto.

### Added

- `uv` como gerenciador de dependências (`pyproject.toml`, `uv.lock`,
  `.python-version`), mantendo `requirements.txt` em paralelo para quem
  preferir `pip`.
- `.dockerignore` excluindo `.git`, `.venv`, `database/` e configs locais
  de ferramentas (`.claude/`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`).
- Rede dedicada `sige_net` no `docker-compose.yml`.
- Healthcheck do Postgres com `depends_on: service_healthy` no serviço
  `gunicorn`, garantindo ordem correta de inicialização.

### Changed

- Imagem Docker migrada de `alpine:3.7` para `python:3.10-slim`, com
  dependências instaladas via `uv` em `/opt/venv` (evita ser mascarado
  pelo bind mount do `docker-compose`).
- Postgres atualizado para `postgres:18-alpine`. Ponto de mount ajustado
  para `/var/lib/postgresql` (novo padrão com subdirs versionados).
- Serviço `gunicorn` agora usa `build: .` em vez de imagem pré-existente.
- `ALLOWED_HOSTS` expandido para incluir `nginx`, `localhost` e
  `127.0.0.1`.
- `nginx` exposto em `8000:80` (em vez de `80:80`) para evitar conflito
  com portas privilegiadas.
- `MAINTAINER` (deprecado) substituído por `LABEL maintainer`.
- `.gitignore` passa a ignorar configs locais de assistentes de código
  (`CLAUDE.md`, `.claude/`, `AGENTS.md`, `GEMINI.md`, `.cursor*`,
  `.aider*`, `docs/superpowers/`).

### Removed

- Atributos legados do `docker-compose.yml`: chave `version:` (obsoleta no
  Compose v2) e `links:` (substituídos por rede dedicada).

## [1.1.0] - 2026-05-22

Baseline pré-modernização. Esta entrada consolida o estado do djangoSIGE
acumulado em 164 commits anteriores até o ajuste de compatibilidade com
Django 5.x.

### Funcionalidades principais

- Cadastros: clientes, fornecedores, transportadoras, produtos e
  empresas.
- Autenticação: login/logout, perfil por usuário, controle de
  permissões.
- Orçamentos e pedidos de compra/venda com geração de PDF
  ([geraldo](https://github.com/thiagopena/geraldo)).
- Módulo financeiro: plano de contas, fluxo de caixa e lançamentos.
- Módulo de estoque.
- Módulo fiscal: emissão de NF-e/NFC-e versão 4.0, validação de XML,
  download, consulta, cancelamento e manifestação do destinatário;
  comunicação com a SEFAZ via [PySIGNFe](https://github.com/thiagopena/PySIGNFe).
- Interface em português.

### Stack

- Python 3.10+
- Django 5.2.14
- Suporte a SQLite (dev) e Postgres (produção).

[Unreleased]: https://github.com/thiagopena/djangoSIGE/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/thiagopena/djangoSIGE/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/thiagopena/djangoSIGE/releases/tag/v1.1.0
