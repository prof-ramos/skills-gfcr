#!/usr/bin/env python3
"""
GitHub Repository Manager - CLI Interativo
Interface de linha de comando para gerenciar repositórios GitHub
"""

import os
import sys
import argparse
import sys
from typing import List, Optional, Any
from github_repo_manager import GitHubRepoManager, RepoConfig


def safe_date_slice(date_str: Optional[str]) -> str:
    """Fatiamento seguro de string de data"""
    if not date_str:
        return "N/A"
    return date_str[:10]


def parse_bool(val: Any) -> bool:
    """Parser robusto para booleanos"""
    if isinstance(val, bool):
        return val
    normalized = str(val).lower().strip()
    if normalized in ("true", "1", "t", "y", "yes", "sim", "s"):
        return True
    if normalized in ("false", "0", "f", "n", "no", "não", "nao"):
        return False
    return False


def print_repo_list(repos: List[dict], show_details: bool = False):
    """Formata e exibe lista de repositórios"""
    if not repos:
        print("Nenhum repositório encontrado.")
        return

    for i, repo in enumerate(repos, 1):
        # Status e visibilidade
        status = "🔒" if repo["archived"] else "✓"
        visibility = "🔐" if repo["private"] else "🌐"

        # Nome e descrição
        name = repo["full_name"]
        desc = repo["description"] or "Sem descrição"

        print(f"{i}. {status} {visibility} {name}")

        if show_details:
            print(f"   📝 {desc}")
            print(
                f"   ⭐ {repo['stargazers_count']} stars  "
                f"🍴 {repo['forks_count']} forks  "
                f"📅 Atualizado: {safe_date_slice(repo['updated_at'])}"
            )
            print(f"   🔗 {repo['html_url']}\n")


def cmd_list(args):
    """Lista repositórios"""
    gh = GitHubRepoManager()

    repos = gh.list_repos(
        username=args.user, type_filter=args.type, sort=args.sort, per_page=args.limit
    )

    # Filtros adicionais
    if args.archived_only:
        repos = [r for r in repos if r["archived"]]
    if args.active_only:
        repos = [r for r in repos if not r["archived"]]
    if args.private_only:
        repos = [r for r in repos if r["private"]]
    if args.public_only:
        repos = [r for r in repos if not r["private"]]

    print(f"\n{'=' * 60}")
    print(f"Repositórios de {args.user or gh.user} ({len(repos)} encontrados)")
    print(f"{'=' * 60}\n")

    print_repo_list(repos, show_details=args.details)


def cmd_info(args):
    """Mostra informações detalhadas de um repositório"""
    gh = GitHubRepoManager()

    try:
        repo = gh.get_repo(args.owner, args.repo)

        print(f"\n{'=' * 60}")
        print(f"📦 {repo['full_name']}")
        print(f"{'=' * 60}\n")

        print(f"📝 Descrição: {repo['description'] or 'Sem descrição'}")
        print(f"🌐 Homepage: {repo['homepage'] or 'N/A'}")
        print(f"🔗 URL: {repo['html_url']}")
        print(f"\n📊 Estatísticas:")
        print(f"   ⭐ Stars: {repo['stargazers_count']}")
        print(f"   👀 Watchers: {repo['watchers_count']}")
        print(f"   🍴 Forks: {repo['forks_count']}")
        print(f"   📂 Tamanho: {repo['size']} KB")
        print(f"   🌿 Branch padrão: {repo['default_branch']}")
        print(f"\n⚙️ Configurações:")
        print(f"   {'🔐 Privado' if repo['private'] else '🌐 Público'}")
        print(f"   {'🔒 Arquivado' if repo['archived'] else '✓ Ativo'}")
        print(f"   Issues: {'✓' if repo['has_issues'] else '✗'}")
        print(f"   Projects: {'✓' if repo['has_projects'] else '✗'}")
        print(f"   Wiki: {'✓' if repo['has_wiki'] else '✗'}")
        print(f"\n📅 Datas:")
        print(f"   Criado: {safe_date_slice(repo['created_at'])}")
        print(f"   Atualizado: {safe_date_slice(repo['updated_at'])}")
        print(f"   Push: {safe_date_slice(repo['pushed_at'])}")

        # Topics
        topics = gh.get_topics(args.owner, args.repo)
        if topics:
            print(f"\n🏷️ Topics: {', '.join(topics)}")

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_archive(args):
    """Arquiva repositório(s)"""
    gh = GitHubRepoManager()

    if args.batch:
        # Modo lote
        repos = [(args.owner, repo.strip()) for repo in args.repo.split(",")]

        print(f"Arquivando {len(repos)} repositórios...")
        results = gh.archive_multiple(repos)

        print(f"\n✓ Sucesso: {len(results['success'])}")
        for repo in results["success"]:
            print(f"  - {repo}")

        if results["failed"]:
            print(f"\n✗ Falhas: {len(results['failed'])}")
            for fail in results["failed"]:
                print(f"  - {fail['repo']}: {fail['error']}")
    else:
        # Modo único
        try:
            result = gh.archive_repo(args.owner, args.repo)
            print(f"✓ Repositório arquivado: {result['full_name']}")
        except Exception as e:
            print(f"❌ Erro: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_unarchive(args):
    """Desarquiva repositório(s)"""
    gh = GitHubRepoManager()

    if args.batch:
        # Modo lote
        repos = [(args.owner, repo.strip()) for repo in args.repo.split(",")]

        print(f"Desarquivando {len(repos)} repositórios...")
        results = gh.unarchive_multiple(repos)

        print(f"\n✓ Sucesso: {len(results['success'])}")
        for repo in results["success"]:
            print(f"  - {repo}")

        if results["failed"]:
            print(f"\n✗ Falhas: {len(results['failed'])}")
            for fail in results["failed"]:
                print(f"  - {fail['repo']}: {fail['error']}")
    else:
        # Modo único
        try:
            result = gh.unarchive_repo(args.owner, args.repo)
            print(f"✓ Repositório desarquivado: {result['full_name']}")
        except Exception as e:
            print(f"❌ Erro: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_delete(args):
    """Deleta repositório(s)"""
    gh = GitHubRepoManager()

    # Confirmação de segurança
    if not args.force and not args.yes:
        print(f"⚠️  ATENÇÃO: Esta ação é IRREVERSÍVEL!")
        print(f"Você está prestes a deletar: {args.owner}/{args.repo}")
        response = input("Digite 'DELETE' para confirmar: ")

        if response != "DELETE":
            print("Operação cancelada.")
            return

    if args.batch:
        # Modo lote
        repos = [(args.owner, repo.strip()) for repo in args.repo.split(",")]

        print(f"Deletando {len(repos)} repositórios...")
        results = gh.delete_multiple(repos, confirm=True)

        print(f"\n✓ Sucesso: {len(results['success'])}")
        for repo in results["success"]:
            print(f"  - {repo}")

        if results["failed"]:
            print(f"\n✗ Falhas: {len(results['failed'])}")
            for fail in results["failed"]:
                print(f"  - {fail['repo']}: {fail['error']}")
    else:
        # Modo único
        try:
            gh.delete_repo(args.owner, args.repo, confirm=True)
            print(f"✓ Repositório deletado: {args.owner}/{args.repo}")
        except Exception as e:
            print(f"❌ Erro: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_update(args):
    """Atualiza configurações do repositório"""
    gh = GitHubRepoManager()

    # Prepara dados de atualização
    updates = {}

    if args.name:
        updates["name"] = args.name
    if args.description is not None:
        updates["description"] = args.description
    if args.homepage is not None:
        updates["homepage"] = args.homepage
    if args.private is not None:
        updates["private"] = parse_bool(args.private)
    if args.archived is not None:
        updates["archived"] = parse_bool(args.archived)
    if args.has_issues is not None:
        updates["has_issues"] = parse_bool(args.has_issues)
    if args.has_projects is not None:
        updates["has_projects"] = parse_bool(args.has_projects)
    if args.has_wiki is not None:
        updates["has_wiki"] = parse_bool(args.has_wiki)

    if not updates:
        print("❌ Nenhuma atualização especificada. Use --help para ver opções.")
        sys.exit(1)

    try:
        result = gh.update_repo(args.owner, args.repo, **updates)
        print(f"✓ Repositório atualizado: {result['full_name']}")

        # Mostra mudanças
        print("\nMudanças aplicadas:")
        for key, value in updates.items():
            print(f"  - {key}: {value}")

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_topics(args):
    """Gerencia topics do repositório"""
    gh = GitHubRepoManager()

    try:
        if args.action == "list":
            # Listar topics
            topics = gh.get_topics(args.owner, args.repo)
            if topics:
                print(f"Topics de {args.owner}/{args.repo}:")
                for topic in topics:
                    print(f"  - {topic}")
            else:
                print("Nenhum topic definido.")

        elif args.action in ["set", "add"]:
            # Definir ou adicionar topics
            if not args.topics:
                print("❌ Erro: Use --topics 'tag1,tag2' para definir tópicos.")
                sys.exit(1)

            topics = [t.strip() for t in args.topics.split(",")]
            if args.action == "set":
                result = gh.set_topics(args.owner, args.repo, topics)
            else:
                result = gh.add_topics(args.owner, args.repo, topics)
            print(f"✓ Topics atualizados: {', '.join(result)}")

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_create(args):
    """Cria novo repositório"""
    gh = GitHubRepoManager()

    config = RepoConfig(
        name=args.name,
        description=args.description,
        homepage=args.homepage,
        private=args.private,
        has_issues=not args.no_issues,
        has_projects=not args.no_projects,
        has_wiki=not args.no_wiki,
        auto_init=args.auto_init,
        default_branch=args.default_branch,
    )

    try:
        repo = gh.create_repo(config)
        print(f"✓ Repositório criado: {repo['html_url']}")

        # Adicionar topics se especificado
        if args.topics:
            topics = [t.strip() for t in args.topics.split(",")]
            gh.set_topics(gh.user, args.name, topics)
            print(f"✓ Topics adicionados: {', '.join(topics)}")

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Ponto de entrada do CLI"""
    parser = argparse.ArgumentParser(
        description="GitHub Repository Manager - Gerenciador de repositórios GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: list
    parser_list = subparsers.add_parser("list", help="Listar repositórios")
    parser_list.add_argument("--user", "-u", help="Usuário (padrão: autenticado)")
    parser_list.add_argument(
        "--type",
        "-t",
        default="all",
        choices=["all", "owner", "public", "private", "member"],
        help="Tipo de repositório",
    )
    parser_list.add_argument(
        "--sort",
        "-s",
        default="updated",
        choices=["created", "updated", "pushed", "full_name"],
        help="Ordenação",
    )
    parser_list.add_argument(
        "--limit", "-l", type=int, default=30, help="Limite de resultados"
    )
    parser_list.add_argument(
        "--details", "-d", action="store_true", help="Mostrar detalhes"
    )
    parser_list.add_argument(
        "--archived-only", action="store_true", help="Apenas arquivados"
    )
    parser_list.add_argument("--active-only", action="store_true", help="Apenas ativos")
    parser_list.add_argument(
        "--private-only", action="store_true", help="Apenas privados"
    )
    parser_list.add_argument(
        "--public-only", action="store_true", help="Apenas públicos"
    )
    parser_list.set_defaults(func=cmd_list)

    # Comando: info
    parser_info = subparsers.add_parser("info", help="Informações detalhadas")
    parser_info.add_argument("owner", help="Dono do repositório")
    parser_info.add_argument("repo", help="Nome do repositório")
    parser_info.set_defaults(func=cmd_info)

    # Comando: archive
    parser_archive = subparsers.add_parser("archive", help="Arquivar repositório")
    parser_archive.add_argument("owner", help="Dono do repositório")
    parser_archive.add_argument("repo", help="Nome(s) do(s) repositório(s)")
    parser_archive.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Modo lote (repos separados por vírgula)",
    )
    parser_archive.set_defaults(func=cmd_archive)

    # Comando: unarchive
    parser_unarchive = subparsers.add_parser(
        "unarchive", help="Desarquivar repositório"
    )
    parser_unarchive.add_argument("owner", help="Dono do repositório")
    parser_unarchive.add_argument("repo", help="Nome(s) do(s) repositório(s)")
    parser_unarchive.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Modo lote (repos separados por vírgula)",
    )
    parser_unarchive.set_defaults(func=cmd_unarchive)

    # Comando: delete
    parser_delete = subparsers.add_parser("delete", help="Deletar repositório")
    parser_delete.add_argument("owner", help="Dono do repositório")
    parser_delete.add_argument("repo", help="Nome(s) do(s) repositório(s)")
    parser_delete.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Modo lote (repos separados por vírgula)",
    )
    parser_delete.add_argument(
        "--yes", "-y", action="store_true", help="Confirmar automaticamente"
    )
    parser_delete.add_argument(
        "--force", "-f", action="store_true", help="Forçar sem confirmação (PERIGOSO!)"
    )
    parser_delete.set_defaults(func=cmd_delete)

    # Comando: update
    parser_update = subparsers.add_parser("update", help="Atualizar repositório")
    parser_update.add_argument("owner", help="Dono do repositório")
    parser_update.add_argument("repo", help="Nome do repositório")
    parser_update.add_argument("--name", help="Novo nome")
    parser_update.add_argument("--description", help="Nova descrição")
    parser_update.add_argument("--homepage", help="Nova homepage")
    parser_update.add_argument("--private", type=str, help="Privado (true/false)")
    parser_update.add_argument("--archived", type=str, help="Arquivado (true/false)")
    parser_update.add_argument("--has-issues", type=str, help="Issues (true/false)")
    parser_update.add_argument("--has-projects", type=str, help="Projects (true/false)")
    parser_update.add_argument("--has-wiki", type=str, help="Wiki (true/false)")
    parser_update.set_defaults(func=cmd_update)

    # Comando: topics
    parser_topics = subparsers.add_parser("topics", help="Gerenciar topics")
    parser_topics.add_argument(
        "action", choices=["list", "set", "add"], help="Ação a executar"
    )
    parser_topics.add_argument("owner", help="Dono do repositório")
    parser_topics.add_argument("repo", help="Nome do repositório")
    parser_topics.add_argument("--topics", help="Topics separados por vírgula")
    parser_topics.set_defaults(func=cmd_topics)

    # Comando: create
    parser_create = subparsers.add_parser("create", help="Criar repositório")
    parser_create.add_argument("name", help="Nome do repositório")
    parser_create.add_argument("--description", help="Descrição")
    parser_create.add_argument("--homepage", help="Homepage")
    parser_create.add_argument(
        "--private", action="store_true", help="Criar como privado"
    )
    parser_create.add_argument(
        "--no-issues", action="store_true", help="Desabilitar issues"
    )
    parser_create.add_argument(
        "--no-projects", action="store_true", help="Desabilitar projects"
    )
    parser_create.add_argument(
        "--no-wiki", action="store_true", help="Desabilitar wiki"
    )
    parser_create.add_argument(
        "--auto-init", action="store_true", help="Criar com README.md"
    )
    parser_create.add_argument(
        "--default-branch", default="main", help="Branch padrão (padrão: main)"
    )
    parser_create.add_argument("--topics", help="Topics separados por vírgula")
    parser_create.set_defaults(func=cmd_create)

    # Parse argumentos
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Verifica GH_TOKEN
    if not os.getenv("GH_TOKEN"):
        print("❌ Erro: GH_TOKEN não encontrado no ambiente.", file=sys.stderr)
        print("Configure com: export GH_TOKEN='ghp_seu_token_aqui'")
        sys.exit(1)

    # Executa comando
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
