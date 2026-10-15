# API de Biblioteca — Django

API REST para gerenciamento de **livros** e **empréstimos** de uma biblioteca, desenvolvida em Python com Django e Django REST Framework para a disciplina de Transição de Software.

A aplicação funciona exclusivamente como API: não há interface gráfica, templates, HTML, CSS ou JavaScript. Todas as respostas são em JSON.

## Tecnologias

- Python 3.11+
- Django 5.2
- Django REST Framework 3.18
- SQLite (banco padrão do Django)

## Como executar

```bash
# 1. Clonar o repositório
git clone https://github.com/lucasstibbe/AtividadeAPI_Django.git
cd AtividadeAPI_Django

# 2. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Criar o banco de dados (SQLite)
python manage.py migrate

# 5. Subir o servidor
python manage.py runserver
```

A API fica disponível em `http://127.0.0.1:8000`.

## Estrutura

```
biblioteca/           Configurações do projeto (settings, URLs raiz)
library/
├── models.py         Models Book e Loan
├── serializers.py    Conversão JSON <-> model e regras de negócio
├── views.py          ViewSets com o CRUD e a rota de livros disponíveis
├── urls.py           Rotas /books e /loans
└── migrations/       Migrations do banco
postman_collection.json   Coleção com todas as requisições de teste
```

## Rotas

### Livros

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| GET | `/books` | Lista todos os livros | 200 |
| GET | `/books/{id}` | Retorna um livro | 200 |
| POST | `/books` | Cadastra um livro | 201 |
| PUT | `/books/{id}` | Atualiza um livro | 200 |
| DELETE | `/books/{id}` | Remove um livro | 204 |
| GET | `/books/available` | Lista só os livros disponíveis (desafio adicional) | 200 |

Exemplo de corpo (POST/PUT):

```json
{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "year": 2008,
    "available": true
}
```

### Empréstimos

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| GET | `/loans` | Lista todos os empréstimos | 200 |
| GET | `/loans/{id}` | Retorna um empréstimo | 200 |
| POST | `/loans` | Registra um empréstimo | 201 |
| PUT | `/loans/{id}` | Atualiza um empréstimo / registra devolução | 200 |
| DELETE | `/loans/{id}` | Remove um empréstimo | 204 |

Registrar empréstimo (POST):

```json
{
    "book_id": 1,
    "person_name": "João da Silva",
    "loan_date": "2026-10-07"
}
```

Registrar devolução (PUT):

```json
{
    "book_id": 1,
    "person_name": "João da Silva",
    "loan_date": "2026-10-07",
    "return_date": "2026-10-15"
}
```

## Regras de negócio

- Não é permitido emprestar um livro com `available = false` → **400**
- Não é permitido emprestar um livro inexistente → **400**
- Ao registrar um empréstimo, o livro fica automaticamente `available = false`
- Ao registrar a devolução (`return_date` preenchido), o livro volta a `available = true`
- `return_date` fica `null` enquanto o livro não for devolvido

Regras adicionais, para manter os dados consistentes:

- `return_date` não pode ser anterior a `loan_date` → **400**
- Não é possível trocar o livro de um empréstimo existente → **400**
- Não é possível remover um livro que possui empréstimos registrados → **400**
- Remover um empréstimo ainda em aberto libera o livro
- Rotas inexistentes retornam **404** em JSON

## Códigos HTTP

| Código | Significado |
|---|---|
| 200 | Operação realizada com sucesso |
| 201 | Recurso criado |
| 204 | Recurso removido |
| 400 | Dados inválidos |
| 404 | Recurso não encontrado |

## Testando com o Postman

1. No Postman, clique em **Import** e selecione o arquivo `postman_collection.json`.
2. Com o servidor rodando e o banco vazio, execute as requisições **na ordem**. A coleção segue um roteiro: cadastra livros, faz um empréstimo, testa as regras de negócio, registra a devolução e remove os registros.
3. O nome de cada requisição indica o status esperado.

Para recomeçar com o banco vazio, apague o arquivo `db.sqlite3` e rode `python manage.py migrate` novamente.
