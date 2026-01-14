# Quick Start Guide - GitHub Repository Manager

## 🚀 Início Rápido (5 minutos)

### 1. Setup Automático
```bash
# Execute o script de setup
./setup.sh
```

O script vai:
- ✓ Verificar Python
- ✓ Instalar dependências
- ✓ Configurar seu token GitHub
- ✓ Testar a conexão

### 2. Comandos Básicos

#### Listar seus repositórios
```bash
python3 gh_cli.py list
```

#### Ver detalhes de um repo
```bash
python3 gh_cli.py info seu-usuario nome-do-repo
```

#### Arquivar um repo antigo
```bash
python3 gh_cli.py archive seu-usuario repo-antigo
```

### 3. Workflow Automático

Execute análise sem fazer mudanças (dry-run):
```bash
python3 workflow_organizer.py
```

Execute com ações reais:
```bash
python3 workflow_organizer.py --execute
```

---

## 📋 Casos de Uso Comuns

### Arquivar múltiplos repos
```bash
python3 gh_cli.py archive seu-usuario "repo1,repo2,repo3" --batch
```

### Deletar repos temporários
```bash
python3 gh_cli.py delete seu-usuario "temp-1,temp-2" --batch --yes
```

### Atualizar descrição
```bash
python3 gh_cli.py update seu-usuario meu-repo \
  --description "Nova descrição"
```

### Tornar repo privado
```bash
python3 gh_cli.py update seu-usuario meu-repo --private true
```

### Adicionar topics
```bash
python3 gh_cli.py topics add seu-usuario meu-repo \
  --topics "python,automation"
```

### Criar novo repo
```bash
python3 gh_cli.py create novo-projeto \
  --description "Meu novo projeto" \
  --auto-init \
  --topics "python,cli"
```

---

## 🐍 Uso como Biblioteca

```python
from github_repo_manager import GitHubRepoManager

# Inicializar
gh = GitHubRepoManager()

# Listar repos
repos = gh.list_repos(per_page=10)

# Arquivar repo
gh.archive_repo("usuario", "repo-antigo")

# Deletar repo (com confirmação)
gh.delete_repo("usuario", "repo-temp", confirm=True)

# Atualizar repo
gh.update_repo(
    owner="usuario",
    repo="meu-projeto",
    description="Nova descrição",
    private=True
)
```

---

## ⚠️ Segurança

### SEMPRE faça backup antes de deletar
```bash
# Arquive ao invés de deletar quando possível
python3 gh_cli.py archive usuario repo-importante
```

### Use dry-run primeiro
```bash
# Teste antes de executar
python3 workflow_organizer.py  # dry-run
python3 workflow_organizer.py --execute  # execução real
```

### Confirmação de deleção
```bash
# CLI sempre pede confirmação
python3 gh_cli.py delete usuario repo

# Para pular confirmação (cuidado!)
python3 gh_cli.py delete usuario repo --yes
```

---

## 🔧 Troubleshooting

### Token inválido
```bash
# Verificar se token está configurado
echo $GH_TOKEN

# Reconfigurar
export GH_TOKEN='novo_token'
```

### Permissões insuficientes
- Verifique se token tem permissões: `repo` e `delete_repo`
- Recrie o token em: https://github.com/settings/tokens

### Teste sua configuração
```bash
python3 test_github_manager.py
```

---

## 📚 Mais Informações

- README completo: `README.md`
- Exemplos de código: `examples_github_manager.py`
- Workflow completo: `workflow_organizer.py`
- CLI help: `python3 gh_cli.py --help`

---

## ✅ Checklist de Primeiro Uso

- [ ] Executei `./setup.sh`
- [ ] Configurei `GH_TOKEN`
- [ ] Testei com `python3 gh_cli.py list`
- [ ] Executei dry-run do workflow
- [ ] Li o README completo
- [ ] Entendi os riscos de deleção

**Pronto para usar! 🎉**
