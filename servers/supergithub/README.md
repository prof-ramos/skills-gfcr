# GitHub Repository Manager

Ferramenta Python completa para gerenciar repositórios GitHub via API REST. Permite apagar, arquivar, atualizar e manipular repositórios usando GitHub Personal Access Token.

## 🚀 Funcionalidades

### ✅ Operações Principais
- ✓ **Listar** repositórios com filtros avançados
- ✓ **Arquivar/Desarquivar** repositórios
- ✓ **Deletar** repositórios (com confirmação de segurança)
- ✓ **Criar** novos repositórios
- ✓ **Atualizar** configurações (nome, descrição, visibilidade, etc.)
- ✓ **Gerenciar topics** (tags/categorias)
- ✓ **Operações em lote** (múltiplos repos de uma vez)

### 🔐 Segurança
- Confirmação obrigatória para deleções
- Validação de token GitHub
- Proteção contra ações acidentais
- Suporte a variáveis de ambiente

## 📋 Pré-requisitos

### 1. Python 3.7+
```bash
python --version
```

### 2. GitHub Personal Access Token

Crie um token em: https://github.com/settings/tokens

**Permissões necessárias:**
- `repo` (acesso completo a repositórios)
- `delete_repo` (para deletar repositórios)

**Configure o token:**
```bash
export GH_TOKEN='ghp_seu_token_aqui'
```

## 📦 Instalação

### Opção 1: Instalação de dependências
```bash
pip install requests --break-system-packages
```

### Opção 2: Usar requirements.txt
```bash
pip install -r requirements.txt --break-system-packages
```

## 🛠️ Uso

### CLI Interativo

#### Listar repositórios
```bash
# Listar seus repositórios
python gh_cli.py list

# Listar com detalhes
python gh_cli.py list --details

# Apenas arquivados
python gh_cli.py list --archived-only

# Apenas privados
python gh_cli.py list --private-only

# Limitar resultados
python gh_cli.py list --limit 10

# Ordenar por criação
python gh_cli.py list --sort created
```

#### Informações detalhadas
```bash
python gh_cli.py info seu-usuario nome-do-repo
```

#### Arquivar repositórios
```bash
# Arquivar um repositório
python gh_cli.py archive seu-usuario nome-do-repo

# Arquivar múltiplos (modo lote)
python gh_cli.py archive seu-usuario "repo1,repo2,repo3" --batch

# Desarquivar
python gh_cli.py unarchive seu-usuario nome-do-repo
```

#### Deletar repositórios
```bash
# Deletar com confirmação interativa
python gh_cli.py delete seu-usuario nome-do-repo

# Deletar com confirmação automática
python gh_cli.py delete seu-usuario nome-do-repo --yes

# Deletar múltiplos
python gh_cli.py delete seu-usuario "repo1,repo2" --batch --yes
```

#### Atualizar repositórios
```bash
# Atualizar descrição
python gh_cli.py update seu-usuario nome-do-repo \
  --description "Nova descrição"

# Renomear repositório
python gh_cli.py update seu-usuario nome-antigo \
  --name nome-novo

# Tornar privado
python gh_cli.py update seu-usuario nome-do-repo \
  --private true

# Desabilitar wiki e projects
python gh_cli.py update seu-usuario nome-do-repo \
  --has-wiki false --has-projects false
```

#### Gerenciar topics
```bash
# Listar topics
python gh_cli.py topics list seu-usuario nome-do-repo

# Definir topics (substitui todos)
python gh_cli.py topics set seu-usuario nome-do-repo \
  --topics "python,automation,cli"

# Adicionar topics (mantém existentes)
python gh_cli.py topics add seu-usuario nome-do-repo \
  --topics "devtools,github-api"
```

#### Criar repositório
```bash
# Criar repositório público
python gh_cli.py create meu-novo-repo \
  --description "Descrição do projeto" \
  --auto-init

# Criar repositório privado com topics
python gh_cli.py create projeto-secreto \
  --private \
  --description "Projeto privado" \
  --topics "python,private" \
  --auto-init
```

### Uso como Biblioteca Python

```python
from github_repo_manager import GitHubRepoManager, RepoConfig

# Inicializar (usa GH_TOKEN do ambiente)
gh = GitHubRepoManager()

# Ou passar token diretamente
gh = GitHubRepoManager(token="ghp_seu_token")

# Listar repositórios
repos = gh.list_repos(per_page=10)
for repo in repos:
    print(f"{repo['name']} - {'Arquivado' if repo['archived'] else 'Ativo'}")

# Arquivar repositório
gh.archive_repo("seu-usuario", "repo-antigo")

# Deletar repositório (requer confirm=True)
gh.delete_repo("seu-usuario", "repo-teste", confirm=True)

# Atualizar descrição
gh.update_repo(
    owner="seu-usuario",
    repo="meu-projeto",
    description="Nova descrição",
    homepage="https://exemplo.com"
)

# Gerenciar topics
gh.set_topics("seu-usuario", "meu-repo", ["python", "automation"])

# Criar novo repositório
config = RepoConfig(
    name="novo-projeto",
    description="Descrição",
    private=False,
    auto_init=True
)
repo = gh.create_repo(config)
```

## 📚 Exemplos Práticos

### Arquivar todos os repositórios antigos
```python
from github_repo_manager import GitHubRepoManager
import datetime

gh = GitHubRepoManager()

# Listar todos os repos
repos = gh.list_repos(per_page=100)

# Filtrar repos sem atualização há mais de 1 ano
cutoff = datetime.datetime.now() - datetime.timedelta(days=365)
old_repos = []

for repo in repos:
    updated = datetime.datetime.strptime(
        repo["updated_at"], 
        "%Y-%m-%dT%H:%M:%SZ"
    )
    if updated < cutoff and not repo["archived"]:
        old_repos.append((gh.user, repo["name"]))

# Arquivar em lote
if old_repos:
    results = gh.archive_multiple(old_repos)
    print(f"Arquivados: {len(results['success'])}")
```

### Cleanup de repositórios temporários
```python
gh = GitHubRepoManager()

# Deletar todos os repos que começam com "temp-"
repos = gh.list_repos(per_page=100)
temp_repos = [
    (gh.user, r["name"]) 
    for r in repos 
    if r["name"].startswith("temp-")
]

if temp_repos:
    results = gh.delete_multiple(temp_repos, confirm=True)
    print(f"Deletados: {len(results['success'])}")
```

### Padronizar topics em todos os projetos Python
```python
gh = GitHubRepoManager()

# Listar todos os repos
repos = gh.list_repos(per_page=100)

# Adicionar topic "python" em todos que têm arquivo .py
for repo in repos:
    if repo["language"] == "Python":
        gh.add_topics(gh.user, repo["name"], ["python"])
        print(f"✓ {repo['name']}")
```

## ⚠️ Avisos Importantes

### Deleções são Irreversíveis
- **NUNCA** há como recuperar um repositório deletado
- Sempre faça backup antes de deletar
- Use `--yes` com extremo cuidado
- Considere arquivar ao invés de deletar

### Rate Limiting
- GitHub API tem limites de requisições
- Autenticado: 5000 req/hora
- Operações em lote respeitam os limites
- Se atingir o limite, espere 1 hora

### Permissões do Token
- Token precisa ter acesso ao repositório
- Para deletar: permissão `delete_repo`
- Para repositórios de org: permissão adequada na org
- Tokens expiram - renove periodicamente

## 🔧 Troubleshooting

### Erro: "GH_TOKEN não encontrado"
```bash
export GH_TOKEN='ghp_seu_token_aqui'
```

### Erro: "403 Forbidden"
- Verifique se o token tem as permissões necessárias
- Certifique-se que o token não expirou
- Para orgs, verifique se tem acesso ao repositório

### Erro: "404 Not Found"
- Verifique se o nome do repositório está correto
- Verifique se o owner está correto
- Para repos privados, certifique-se que tem acesso

### Erro: "422 Unprocessable Entity"
- Geralmente erro de validação
- Verifique se os dados estão no formato correto
- Topics devem ser lowercase e alphanumeric

## 📖 Documentação da API

Para mais detalhes sobre a API do GitHub:
https://docs.github.com/en/rest/repos/repos

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests
- Melhorar a documentação

## 📝 Licença

Este projeto é de código aberto. Use com responsabilidade.

## ⚡ Performance

### Benchmarks Aproximados
- Listar 100 repos: ~1s
- Arquivar 1 repo: ~0.5s
- Deletar 1 repo: ~0.5s
- Operações em lote de 10 repos: ~5s

### Otimizações
- Use operações em lote quando possível
- Cache de resultados quando apropriado
- Respeite rate limiting

## 🎯 Roadmap

- [ ] Suporte a GitHub CLI nativo
- [ ] Interface web (Streamlit/Flask)
- [ ] Backup automático antes de deletar
- [ ] Modo dry-run (simulação)
- [ ] Logs detalhados
- [ ] Restauração de repos arquivados
- [ ] Suporte a GitHub Organizations
- [ ] Webhook management
- [ ] Branch protection rules
- [ ] Colaboradores e permissões

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Procure em issues existentes
3. Crie uma nova issue com detalhes

---

**Desenvolvido com ❤️ para automação GitHub**
