#  Input Security & Persistence Auditor

Ferramenta defensiva (**Blue Team**) desenvolvida em **Python puro** para auditar mecanismos de proteção de entrada do Windows e identificar possíveis vetores de persistência utilizados por softwares de monitoramento não autorizados.

> **Nota Ética:** Este projeto tem finalidade estritamente educacional e defensiva, focado em auditoria de segurança do sistema operacional e boas práticas de proteção de credenciais.

---

##  Objetivo do Projeto

Compreender na prática como sistemas operacionais protegem a entrada de dados (como senhas e credenciais) e como ferramentas defensivas monitoram alterações suspeitas no ambiente, verificando:
1. **Isolamento de Área de Trabalho Segura (`Secure Desktop` e `UAC`)**;
2. **Chaves de Persistência na Inicialização do Sistema (`Registro do Windows`)**;
3. **Integridade de Processos em Execução (`Baseline Comparison`)**.

---

##  Estrutura do Projeto

```text
input-security-auditor/
├── src/
│   ├── __init__.py
│   ├── auditor.py      # Módulo com funções de auditoria (UAC, Registro e Processos)
│   └── main.py         # Orquestração, geração de relatório JSON e logs
├── baseline/
│   └── processos_conhecidos.json
├── logs/
│   └── auditoria.log
├── reports/
│   └── relatorio_seguranca.json
└── README.md