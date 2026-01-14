#!/usr/bin/env python3
"""
Exemplos de uso do GitHub Repository Manager
"""

from github_repo_manager import GitHubRepoManager, RepoConfig


def example_basic_usage():
    """Uso básico - listar e obter informações"""
    gh = GitHubRepoManager()  # Usa GH_TOKEN do ambiente
    
    # Lista seus repositórios
    repos = gh.list_repos(per_page=10, sort="updated")
    print(f"Total de repositórios: {len(repos)}\n")
    
    # Detalhes de um repositório específico
    repo = gh.get_repo("seu-usuario", "seu-repo")
    print(f"Nome: {repo['name']}")
    print(f"Descrição: {repo['description']}")
    print(f"Stars: {repo['stargazers_count']}")
    print(f"Forks: {repo['forks_count']}")
    print(f"Arquivado: {repo['archived']}")


def example_archive_operations():
    """Operações de arquivamento"""
    gh = GitHubRepoManager()
    
    # Arquivar um repositório
    result = gh.archive_repo("seu-usuario", "repo-antigo")
    print(f"✓ Repositório arquivado: {result['full_name']}")
    
    # Desarquivar um repositório
    result = gh.unarchive_repo("seu-usuario", "repo-antigo")
    print(f"✓ Repositório desarquivado: {result['full_name']}")
    
    # Arquivar múltiplos repositórios
    repos_to_archive = [
        ("seu-usuario", "projeto-1"),
        ("seu-usuario", "projeto-2"),
        ("seu-usuario", "projeto-3"),
    ]
    results = gh.archive_multiple(repos_to_archive)
    print(f"✓ Arquivados: {len(results['success'])}")
    print(f"✗ Falhas: {len(results['failed'])}")


def example_delete_operations():
    """Operações de exclusão (CUIDADO!)"""
    gh = GitHubRepoManager()
    
    # Deletar um único repositório
    # ATENÇÃO: Ação irreversível!
    try:
        gh.delete_repo("seu-usuario", "repo-teste", confirm=True)
        print("✓ Repositório deletado")
    except ValueError as e:
        print(f"Confirmação necessária: {e}")
    
    # Deletar múltiplos repositórios
    repos_to_delete = [
        ("seu-usuario", "temp-1"),
        ("seu-usuario", "temp-2"),
    ]
    results = gh.delete_multiple(repos_to_delete, confirm=True)
    print(f"✓ Deletados: {len(results['success'])}")
    print(f"✗ Falhas: {len(results['failed'])}")


def example_update_operations():
    """Operações de atualização"""
    gh = GitHubRepoManager()
    
    # Atualizar descrição e homepage
    gh.update_repo(
        owner="seu-usuario",
        repo="meu-projeto",
        description="Nova descrição do projeto",
        homepage="https://meu-site.com"
    )
    print("✓ Repositório atualizado")
    
    # Renomear repositório
    gh.update_repo(
        owner="seu-usuario",
        repo="nome-antigo",
        name="nome-novo"
    )
    print("✓ Repositório renomeado")
    
    # Alterar visibilidade
    gh.update_visibility("seu-usuario", "meu-repo", private=True)
    print("✓ Repositório tornado privado")
    
    # Desabilitar wiki e projects
    gh.update_repo(
        owner="seu-usuario",
        repo="meu-projeto",
        has_wiki=False,
        has_projects=False
    )
    print("✓ Wiki e Projects desabilitados")


def example_topics_operations():
    """Operações com topics (tags)"""
    gh = GitHubRepoManager()
    
    # Obter topics atuais
    topics = gh.get_topics("seu-usuario", "meu-repo")
    print(f"Topics atuais: {topics}")
    
    # Definir novos topics (substitui todos)
    new_topics = ["python", "automation", "github-api", "devtools"]
    gh.set_topics("seu-usuario", "meu-repo", new_topics)
    print(f"✓ Topics definidos: {new_topics}")
    
    # Adicionar topics (mantém existentes)
    additional_topics = ["cli", "rest-api"]
    all_topics = gh.add_topics("seu-usuario", "meu-repo", additional_topics)
    print(f"✓ Topics atualizados: {all_topics}")


def example_create_repo():
    """Criar novo repositório"""
    gh = GitHubRepoManager()
    
    # Configuração do repositório
    config = RepoConfig(
        name="novo-projeto",
        description="Descrição do novo projeto",
        homepage="https://exemplo.com",
        private=False,
        has_issues=True,
        has_projects=True,
        has_wiki=False,
        auto_init=True,  # Cria com README.md
        default_branch="main"
    )
    
    # Criar repositório
    repo = gh.create_repo(config)
    print(f"✓ Repositório criado: {repo['html_url']}")
    
    # Adicionar topics ao novo repositório
    gh.set_topics(gh.user, "novo-projeto", ["python", "projeto-novo"])


def example_batch_operations():
    """Operações em lote"""
    gh = GitHubRepoManager()
    
    # Listar todos os repositórios arquivados
    all_repos = gh.list_repos(per_page=100)
    archived = [r for r in all_repos if r["archived"]]
    print(f"Repositórios arquivados: {len(archived)}")
    
    # Listar repositórios privados
    private = [r for r in all_repos if r["private"]]
    print(f"Repositórios privados: {len(private)}")
    
    # Arquivar todos os repos com nome começando em "temp-"
    temp_repos = [(gh.user, r["name"]) for r in all_repos if r["name"].startswith("temp-")]
    if temp_repos:
        results = gh.archive_multiple(temp_repos)
        print(f"✓ Arquivados {len(results['success'])} repositórios temporários")


def example_workflow_cleanup():
    """Workflow de limpeza completo"""
    gh = GitHubRepoManager()
    
    # 1. Listar todos os repositórios
    all_repos = gh.list_repos(per_page=100)
    
    # 2. Filtrar repositórios antigos sem atividade
    import datetime
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=365)
    
    old_repos = []
    for repo in all_repos:
        updated = datetime.datetime.strptime(
            repo["updated_at"], 
            "%Y-%m-%dT%H:%M:%SZ"
        )
        if updated < cutoff_date:
            old_repos.append((gh.user, repo["name"]))
    
    print(f"Encontrados {len(old_repos)} repositórios sem atualização há mais de 1 ano")
    
    # 3. Arquivar repositórios antigos
    if old_repos:
        print("Arquivando repositórios antigos...")
        results = gh.archive_multiple(old_repos)
        print(f"✓ Arquivados: {len(results['success'])}")
        
        if results['failed']:
            print("Falhas:")
            for fail in results['failed']:
                print(f"  - {fail['repo']}: {fail['error']}")


def example_security_best_practices():
    """Melhores práticas de segurança"""
    
    # 1. Usar variável de ambiente (recomendado)
    gh = GitHubRepoManager()  # Lê GH_TOKEN do ambiente
    
    # 2. Ou passar token diretamente (menos seguro)
    # gh = GitHubRepoManager(token="ghp_seu_token_aqui")
    
    # 3. Sempre confirmar deleções
    try:
        # Isso vai falhar sem confirm=True (proteção)
        gh.delete_repo("user", "repo")
    except ValueError as e:
        print(f"Proteção ativada: {e}")
    
    # 4. Verificar antes de deletar
    repo = gh.get_repo("seu-usuario", "repo-teste")
    print(f"Repositório: {repo['name']}")
    print(f"Stars: {repo['stargazers_count']}")
    print(f"Última atualização: {repo['updated_at']}")
    
    # Agora sim, deletar com confirmação
    # gh.delete_repo("seu-usuario", "repo-teste", confirm=True)


if __name__ == "__main__":
    print("=== Exemplos de uso do GitHub Repository Manager ===\n")
    print("Descomente a função que deseja executar:\n")
    
    # Descomente para executar
    # example_basic_usage()
    # example_archive_operations()
    # example_delete_operations()
    # example_update_operations()
    # example_topics_operations()
    # example_create_repo()
    # example_batch_operations()
    # example_workflow_cleanup()
    # example_security_best_practices()
    
    print("\nPara usar, defina GH_TOKEN no ambiente:")
    print("  export GH_TOKEN='ghp_seu_token_aqui'")
    print("  python examples.py")
