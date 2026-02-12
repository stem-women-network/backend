# STEM Women Network - Backend (FastAPI)

O STEM Women Network é um programa que conecta mentoras mulheres da área de STEM (Ciência, Tecnologia, Engenharia e Matemática) com alunas universitárias que querem seguir carreira nessas áreas.
A ideia principal é criar rede, apoio, orientação e oportunidade, fortalecendo a presença feminina em STEM.

## Como executar

1. Criar e ativar ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Instalar dependências

```bash
pip install -r requirements.txt
```

3. Definir `DATABASE_URL` no arquivo `.env` (ex.: SQLite `sqlite:///./db.sqlite3` ou PostgreSQL)

4. Inicializar banco (opcional, cria tabelas):

```python
from src.database import create_db_and_tables
create_db_and_tables()
```

5. Rodar o servidor

```bash
fastapi run main.py

python -m uvicorn main:app --reload
```

## Rotas (documentação completa)

Observação: todas as rotas usam prefixos conforme `main.py`:
- `/mentors` - rotas de mentoras
- `/users` - rotas de usuários
- `/match` - rotas de matchmaking / pedidos de mentoria
- `/auth` - autenticação e cadastro
- `/certificates` - certificados
- `/universities` - universidades
- `/mentoradas` - mentoradas
- `/mentoring` - troca de mensagens / arquivos de mentoring
- `/meetings` - encontros e próximos encontros
- `/admin` - endpoints administrativos

Para endpoints que requerem autenticação, envie header:
`Authorization: Bearer <token>`

---

**/auth**
- POST `/auth/login` — login com credenciais (`LoginModel`)
- POST `/auth/signup-mentor` — cadastro de mentora
- POST `/auth/signup-mentee` — cadastro de mentorada

**/users**
- GET `/users/` — listar usuários
- GET `/users/{id_usuario}` — obter usuário por ID
- POST `/users/` — criar usuário
- PUT `/users/{id_usuario}` — atualizar usuário
- DELETE `/users/{id_usuario}` — deletar usuário

**/mentors**
- GET `/mentors/` — listar mentoras.
- GET `/mentors/get-current-mentee` — obter mentee atual (usa token do mentor)
- GET `/mentors/get-all-mentee` — obter todas as mentees associadas ao mentor
- GET `/mentors/{id_mentora}` — obter mentora por ID
- POST `/mentors/` — criar mentora
- PUT `/mentors/{id_mentora}` — atualizar mentora
- DELETE `/mentors/{id_mentora}` — deletar mentora
- GET `/mentors/{id_mentora}/disponibilidade` — obter disponibilidade
- PUT `/mentors/{id_mentora}/disponibilidade` — atualizar disponibilidade

**/mentoradas**
- GET `/mentoradas/` — listar mentoradas
- GET `/mentoradas/{id_mentorada}` — obter mentorada por ID
- POST `/mentoradas/` — criar mentorada
- PUT `/mentoradas/{id_mentorada}` — atualizar mentorada
- DELETE `/mentoradas/{id_mentorada}` — deletar mentorada

**/meetings**
- GET `/meetings/` — listar encontros
- GET `/meetings/{id_encontro}` — obter encontro por ID
- POST `/meetings/` — criar encontro
- PUT `/meetings/{id_encontro}` — atualizar encontro
- DELETE `/meetings/{id_encontro}` — deletar encontro
- GET `/meetings/upcoming` — listar próximos encontros
- GET `/meetings/upcoming/{id_proximo_encontro}` — obter próximo encontro
- POST `/meetings/upcoming` — criar próximo encontro
- PUT `/meetings/upcoming/{id_proximo_encontro}` — atualizar próximo encontro
- DELETE `/meetings/upcoming/{id_proximo_encontro}` — deletar próximo encontro

**/match**
- POST `/match/` — criar match/pedido de mentoria (requer token)
- GET `/match/pedidos/` — listar pedidos de mentoria do usuário (requer token)
- GET `/match/pedidos/{id_pedidos_mentoria}` — obter pedido por ID
- PUT `/match/pedidos/{id_pedidos_mentoria}` — atualizar estado do pedido (requer token)
- DELETE `/match/pedidos/{id_pedidos_mentoria}` — deletar pedido (requer token)

**/certificates**
- GET `/certificates/` — listar certificados
- GET `/certificates/{id_certificado}` — obter certificado por ID
- POST `/certificates/` — criar certificado
- DELETE `/certificates/{id_certificado}` — deletar certificado
- GET `/certificates/mentorada/{id_mentorada}` — listar certificados de uma mentorada

**/mentoring**
- POST `/mentoring/get-messages` — obter mensagens entre mentor/mentee (requere token e body com `other_id`)
- POST `/mentoring/send-file` — enviar arquivo (multipart/form-data: `file`, `title`, `file_type`, `mentee_id`, `Authorization` header)
- GET `/mentoring/get-files/?mentee_id=...` — listar arquivos trocados
- GET `/mentoring/download-file?file_id=...` — baixar arquivo (retorna base64)
- DELETE `/mentoring/delete-file/{file_id}` — deletar arquivo

**/admin**
- GET `/admin/get-approvals` — listar aprovações pendentes (requer token de admin)
- POST `/admin/update-approval` — aprovar/reprovar mentoras (requer token de admin)
- GET `/admin/get-approvals-mentee` — listar aprovações de mentoradas
- POST `/admin/update-approval-mentee` — aprovar/reprovar mentoradas

**/universities**
- GET `/universities/` — listar universidades com contagem de matches (requer token de admin). Retorno: lista de objetos com `id`, `name`, `coord`, `matches`
- GET `/universities/count` — retornar contagem total de universidades (requer token de admin)
- GET `/universities/search/{nome}` — buscar universidades por nome (case-insensitive)
- GET `/universities/{id_universidade_instituicao}` — obter universidade por ID (UUID)
- POST `/universities/` — criar nova universidade. Body: `{ "nome_instituicao": "Nome" }`
- PUT `/universities/{id_universidade_instituicao}` — atualizar nome da universidade. Body: `{ "nome_instituicao": "Novo Nome" }`
- DELETE `/universities/{id_universidade_instituicao}` — deletar universidade por ID