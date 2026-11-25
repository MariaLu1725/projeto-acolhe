# 🏥 Projeto Acolhe — Cidadania, Saúde e Tecnologia

## 📌 Visão Geral do Sistema
O **Sistema Web do Projeto Acolhe** é uma solução de tecnologia social desenvolvida para apoiar a triagem e o atendimento interdisciplinar (Direito, Enfermagem e Análise e Desenvolvimento de Sistemas - ADS) na **Unidade de Saúde da Família (USF) Irmã Terezinha**, localizada no bairro de Peixinhos, Recife–PE.

---

## 🛠️ Arquitetura do Sistema

1. **Frontend / Interface do Usuário**: Desenvolvido em **Python 3.12** utilizando a biblioteca **Streamlit**, com estilização CSS customizada para visualização responsiva em computadores, tablets e smartphones.
2. **Banco de Dados Relacional**: **SQLite3** (`acolhe_sistema.db`), estruturado com chave estrangeira (`FOREIGN KEY`) entre moradores (`participantes`) e triagens (`atendimentos`).
3. **Backend API RESTful**: Servidor HTTP nativo em Python rodando em *thread* paralela na porta `8050`, disponibilizando endpoints JSON (`/api/v1/health`, `/api/v1/metricas`, `/api/v1/atendimentos`).

---

## 📂 Estrutura de Arquivos

```text
projeto-acolhe/
├── sistema_acolhe_completo.py   # Código-fonte principal da aplicação Web e API
├── requirements.txt             # Dependências Python para execução e deploy
├── Dockerfile                   # Configuração do contêiner Docker
├── .gitignore                   # Arquivos ignorados no repositório Git
└── README.md                    # Documentação técnica do projeto
```

---

## 🚀 Passo a Passo para Deploy na Nuvem (Streamlit Community Cloud / Render)

### Etapa 1: Enviar para o GitHub
1. Crie um repositório público no **GitHub** (ex: `projeto-acolhe`).
2. Envie os arquivos do projeto para a branch principal (`main`).

### Etapa 2: Conectar e Publicar no Streamlit Cloud
1. Acesse **[share.streamlit.io](https://share.streamlit.io)** e faça login com sua conta do GitHub.
2. Clique no botão **New app**.
3. Selecione o repositório `seu-usuario/projeto-acolhe` e a branch `main`.
4. No campo **Main file path**, digite: `sistema_acolhe_completo.py`.
5. Clique em **Deploy!**. Em cerca de 2 minutos seu sistema estará no ar com HTTPS gratuito!
