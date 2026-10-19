# loja-crud-python

Sistema de **CRUD com autenticação (login/cadastro) e carrinho de compras**, desenvolvido utilizando **FastAPI**, **AWS** e **PostgreSQL**.

---

##  Requisitos e Instalação do Banco de Dados

### 1. Cliente PostgreSQL (Servidor Linux)
Para gerenciar ou se conectar ao banco de dados remoto a partir de um servidor Linux, instale o cliente do PostgreSQL:
```bash
sudo apt update && sudo apt install -y postgresql-client
```

### 2. Conexão com o Banco de Dados
Utilize o comando abaixo para se conectar à sua instância do PostgreSQL. Substitua os valores entre colchetes `[...]` pelos seus dados reais:
```bash
psql -h [ENDEREÇO_DO_HOST] -U [NOME_DO_USUÁRIO] -d [NOME_DO_BANCO]
```

### 3. Configuração do Banco de Dados (SQL)
Após se conectar ao servidor do banco de dados, execute os comandos abaixo para criar a estrutura inicial:

```sql
-- Cria o banco de dados definindo o usuário proprietário
CREATE DATABASE projeto_tarefas OWNER app_projeto_tarefas;
```
---
