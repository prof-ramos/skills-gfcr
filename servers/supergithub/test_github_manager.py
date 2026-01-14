#!/usr/bin/env python3
"""
Testes básicos para GitHub Repository Manager
Execute com: python3 test_github_manager.py
"""

import os
import sys
from github_repo_manager import GitHubRepoManager, RepoConfig


def test_authentication():
    """Teste 1: Autenticação"""
    print("Teste 1: Autenticação...")
    
    try:
        gh = GitHubRepoManager()
        print(f"  ✓ Autenticado como: {gh.user}")
        return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def test_list_repos():
    """Teste 2: Listar repositórios"""
    print("\nTeste 2: Listar repositórios...")
    
    try:
        gh = GitHubRepoManager()
        repos = gh.list_repos(per_page=5)
        
        if repos:
            print(f"  ✓ Encontrados {len(repos)} repositórios")
            print(f"  Exemplo: {repos[0]['full_name']}")
            return True
        else:
            print("  ⚠ Nenhum repositório encontrado")
            return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def test_get_repo_info():
    """Teste 3: Obter informações de repositório"""
    print("\nTeste 3: Obter informações de repositório...")
    
    try:
        gh = GitHubRepoManager()
        repos = gh.list_repos(per_page=1)
        
        if not repos:
            print("  ⚠ Nenhum repositório para testar")
            return True
        
        owner = repos[0]["owner"]["login"]
        repo = repos[0]["name"]
        
        info = gh.get_repo(owner, repo)
        print(f"  ✓ Informações obtidas de: {info['full_name']}")
        print(f"    - Descrição: {info['description'] or 'N/A'}")
        print(f"    - Stars: {info['stargazers_count']}")
        print(f"    - Arquivado: {info['archived']}")
        return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def test_get_topics():
    """Teste 4: Obter topics"""
    print("\nTeste 4: Obter topics...")
    
    try:
        gh = GitHubRepoManager()
        repos = gh.list_repos(per_page=1)
        
        if not repos:
            print("  ⚠ Nenhum repositório para testar")
            return True
        
        owner = repos[0]["owner"]["login"]
        repo = repos[0]["name"]
        
        topics = gh.get_topics(owner, repo)
        print(f"  ✓ Topics de {owner}/{repo}: {topics if topics else 'nenhum'}")
        return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def test_repo_config():
    """Teste 5: Configuração de repositório"""
    print("\nTeste 5: Configuração de repositório...")
    
    try:
        config = RepoConfig(
            name="test-repo",
            description="Test repository",
            private=True,
            auto_init=True
        )
        
        print(f"  ✓ Configuração criada:")
        print(f"    - Nome: {config.name}")
        print(f"    - Descrição: {config.description}")
        print(f"    - Privado: {config.private}")
        print(f"    - Auto-init: {config.auto_init}")
        return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def test_filters():
    """Teste 6: Filtros de repositórios"""
    print("\nTeste 6: Filtros de repositórios...")
    
    try:
        gh = GitHubRepoManager()
        
        # Todos os repos
        all_repos = gh.list_repos(per_page=100)
        
        # Filtrar arquivados
        archived = [r for r in all_repos if r["archived"]]
        
        # Filtrar privados
        private = [r for r in all_repos if r["private"]]
        
        # Filtrar públicos
        public = [r for r in all_repos if not r["private"]]
        
        print(f"  ✓ Estatísticas:")
        print(f"    - Total: {len(all_repos)}")
        print(f"    - Arquivados: {len(archived)}")
        print(f"    - Privados: {len(private)}")
        print(f"    - Públicos: {len(public)}")
        return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("="*60)
    print("TESTES DO GITHUB REPOSITORY MANAGER")
    print("="*60)
    
    # Verificar token
    if not os.getenv("GH_TOKEN"):
        print("\n❌ GH_TOKEN não encontrado!")
        print("Configure com: export GH_TOKEN='seu_token'")
        sys.exit(1)
    
    # Lista de testes
    tests = [
        test_authentication,
        test_list_repos,
        test_get_repo_info,
        test_get_topics,
        test_repo_config,
        test_filters
    ]
    
    # Executar testes
    results = []
    for test in tests:
        results.append(test())
    
    # Relatório final
    print("\n" + "="*60)
    print("RESULTADO DOS TESTES")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✓ Passou: {passed}/{total}")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print(f"⚠️  {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
