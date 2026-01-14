# Refatoração e Melhorias de Segurança (Review CodeRabbit)

Este plano detalha as correções e melhorias sugeridas pelo CodeRabbit para garantir a segurança,
robustez e aderência às melhores práticas de desenvolvimento no repositório.

## User Review Required

- **Segurança LaTeX**: Implementação de um helper para escapar caracteres especiais do LaTeX em
  `gerar_documento.py` para evitar ataques de injeção.
- **Segurança de Token**: Atualização do `.env.example` e `setup.sh` para recomendar escopos mínimos
  (`repo` ao invés de `delete_repo` por padrão) e proteger o arquivo `.env` com permissões
  restritivas.
- **Ambiente Virtual**: Mudança recomendada no `setup.sh` para utilizar `venv`, evitando o uso de
  `--break-system-packages`.

## Proposed Changes

### 1. Segurança e Infraestrutura

#### [MODIFY] [.env.example](file:///Users/gabrielramos/skills-gfcr/servers/supergithub/.env.example)

- Remover recomendação de permissão `delete_repo` como padrão; adicionar aviso sobre riscos de
  segurança.

#### [MODIFY] [.gitignore](file:///Users/gabrielramos/skills-gfcr/.gitignore)

- Substituir `*.skill` e `*.zip` por regras mais específicas (ex: `**/*.zip` exceto `/skills/`) ou
  mover para diretórios de build para evitar ignorar arquivos de distribuição válidos.

#### [MODIFY] [setup.sh](file:///Users/gabrielramos/skills-gfcr/servers/supergithub/setup.sh)

- Adicionar headers de segurança shell (`set -euo pipefail`).
- Implementar criação automática de ambiente virtual (`.venv`).
- Garantir permissões `600` no `.env` e adicionar automaticamente ao `.gitignore`.
- Extrair validação do token para um script Python dedicado.

### 2. Melhorias nos Servidores (SuperGitHub)

#### [MODIFY] [github_repo_manager.py](file:///Users/gabrielramos/skills-gfcr/servers/supergithub/github_repo_manager.py)

- Corrigir parâmetro `visibility` para `type` em `list_repos`.
- Atualizar headers de `get_topics` para o padrão atual (`application/vnd.github+json`).
- Garantir que `create_repo` respeite o `default_branch` através de uma chamada PATCH subsequente.

#### [MODIFY] [gh_cli.py](file:///Users/gabrielramos/skills-gfcr/servers/supergithub/gh_cli.py)

- Adicionar validação de `None` antes de fatiar strings de data (`repo['updated_at'][:10]`).
- Implementar parser robusto para booleanos (`true/false`, `1/0`, `sim/não`).
- Adicionar suporte a processamento em lote para o comando `unarchive`.
- Validar entrada de tópicos para evitar `AttributeError`.

#### [MODIFY] [workflow_organizer.py](file:///Users/gabrielramos/skills-gfcr/servers/supergithub/workflow_organizer.py)

- Implementar paginação completa em `get_all_repos`.
- Tornar todas as comparações de data conscientes de fuso horário (UTC).
- Otimizar `organize_by_topics` para não chamar a API em modo `dry_run`.
- Adicionar suporte a modo não-interativo (`--force`) para deleção.

### 3. Melhorias nas Skills

#### [MODIFY] [SKILL.md (Template)](file:///Users/gabrielramos/skills-gfcr/docs/reference/official-skills/template/SKILL.md)

- Adicionar campos `author`, `version`, `tags` e `examples` ao frontmatter.

#### [MODIFY] [gerar_documento.py](file:///Users/gabrielramos/skills-gfcr/skills/brazilian-official-docs/scripts/gerar_documento.py)

- Implementar função `escapar_latex(texto)`.
- Validar chaves obrigatórias em dicionários de dados.
- Adicionar verificação de erros e timeouts em `subprocess.run`.
- Garantir criação de diretórios de destino antes de copiar arquivos.

#### [MODIFY] [validar_documento.py](file:///Users/gabrielramos/skills-gfcr/skills/brazilian-official-docs/scripts/validar_documento.py)

- Corrigir regex de detecção de múltiplos espaços (`r' {3,}'`).
- Tornar detecção de coloquialismos mais precisa usando limites de palavra (`\b`).
- Padronizar uso de f-strings no lugar de `.format()`.
- Refatorar loops simples para o padrão funcional `any()`.

#### [MODIFY] [core.py (UI/UX)](file:///Users/gabrielramos/skills-gfcr/skills/ui-ux-pro-max/scripts/core.py)

- Adicionar tratamento de erro em `_load_csv`.
- Otimizar `BM25` pré-computando frequências de termos no `fit()`.
- Corrigir lógica de fatiamento de resultados em `_search_csv` para aplicar o limite APÓS o filtro
  de score.

## Verification Plan

### Automated Tests

- Executar `uv run pytest servers/supergithub/test_github_manager.py` (após refatoração para usar
  fixtures).
- Validar scripts das skills com inputs conhecidos para testar o escaping de LaTeX e regex de
  validação.

### Manual Verification

1. Instalar dependências via novo `setup.sh` e verificar se o `.venv` foi criado e o `.env` está
   protegido.
2. Testar comandos CLI do `supergithub` com flags conflitantes (ex: `--private` e `--public`) para
   validar erro precoce.
3. Verificar renderização do `README.md` com a nova seção de instalação expandida.
