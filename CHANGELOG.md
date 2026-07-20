# Changelog

## 2026-07-20 - Documentação e revisão técnica

- Reescrito o README para refletir o pipeline e os requisitos atuais.
- Criados guias de usuário, arquitetura, desenvolvimento e verificações.
- Registrados riscos, inconsistências e lacunas de teste encontrados na revisão estática.
- Atualizado `config.example.json` com segmento e histórico de contratos.
- Centralizados modelos, endpoints e parâmetros do LM Studio em `scripts/configuracao.py`.
- Unificados configuração persistente e cancelamento cooperativo entre os módulos.
- Corrigidos os contratos de perguntas e ART e evitada mutação entre PDFs.
- Declaradas dependências diretas e criada a suíte inicial de testes unitários.
- Removidos o check duplicado `checks/estudos/ART.py` e o módulo de QR Code.
- Atualizada a documentação e criados o Manual do Usuário e a Nota Técnica.

## 2026-06-17

### Reorganização inicial

- Inicializado repositorio Git em `C:\AmbienteDeTeste\CPDv3`.
- Criado `funcs/rag_engine.py` para centralizar extração de PDF, limpeza de texto, criação de embeddings, recuperação e consulta ao LLM.
- Criado `funcs/check_runner.py` para padronizar execução das verificações, cálculo de conformidade e geração dos RACs.
- Substituidos scripts longos de `checks/estudos` e `checks/projetos` por wrappers declarativos com `CheckConfig`.
- Mantido `scripts/perguntas_ia.py` como wrapper de compatibilidade para chamadas antigas.
- Corrigido versionamento de nomes em `funcs/common_functions.py` para considerar o código real da disciplina.
- Atualizado `requirements.txt` para conter apenas dependências usadas pelo projeto reorganizado.
- Atualizado `.gitignore` para ignorar `*.pyc`, `vectorstores/` e `config.json`.
- Ajustado `Template_pdf_projeto.py` para aceitar a etapa de relacao de documentos gerais como opcional.
- Criado `config.example.json` sem caminhos locais para documentar a estrutura esperada de configuração.

### Validação e limpeza

- Removidos `__pycache__` e arquivos `.pyc` gerados.
- Rodada verificação de sintaxe com `python -m py_compile` em todos os scripts Python.
- Preparado commit inicial após validação.

## 2026-06-17 - Padronização de scripts e templates

- Renomeados os scripts de `checks/estudos` para o padrão `estudo_<disciplina>.py`.
- Renomeados os scripts de `checks/projetos` para o padrão `projeto_<disciplina>.py`.
- Padronizada a estrutura interna dos scripts com `CHECK_CONFIG` e `main() -> None`.
- Criado `templates/pdf_report.py` como template central dos RACs.
- Criados `templates/relatorio_estudo.py` e `templates/relatorio_projeto.py` como wrappers de tipo de relatório.
- Removidos os templates antigos `Template_pdf_estudo.py` e `Template_pdf_projeto.py`.
- Corrigida a resolução de caminhos para usar a raiz real do projeto, em vez do diretório corrente do terminal.
- Removidas as imagens não utilizadas `figs/icone.png` e `figs/logo_icone.jpeg`.
- Atualizados `README.md` e `requirements.txt` para refletir a estrutura atual.
