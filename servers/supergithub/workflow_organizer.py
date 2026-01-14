#!/usr/bin/env python3
"""
Workflow Completo de Gerenciamento de Repositórios GitHub
Exemplo de uso real: limpeza e organização de repositórios
"""

import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from github_repo_manager import GitHubRepoManager


class RepoOrganizer:
    """Organizador automático de repositórios"""

    def __init__(self, dry_run: bool = True, force: bool = False):
        """
        Inicializa organizador

        Args:
            dry_run: Se True, apenas simula as ações sem executar
            force: Se True, ignora confirmações interativas
        """
        self.gh = GitHubRepoManager()
        self.dry_run = dry_run
        self.force = force
        self.stats = {
            "total": 0,
            "archived": 0,
            "deleted": 0,
            "updated": 0,
            "skipped": 0,
        }

    def log(self, message: str, level: str = "INFO"):
        """Log formatado"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✓",
            "WARNING": "⚠️",
            "ERROR": "✗",
            "DRY_RUN": "🔍",
        }.get(level, "•")

        print(f"{prefix} {message}")

    def get_all_repos(self) -> List[Dict]:
        """Obtém todos os repositórios do usuário com paginação"""
        self.log("Carregando repositórios...")
        all_repos = []
        page = 1

        while True:
            repos = self.gh.list_repos(per_page=100, sort="updated")
            if not repos:
                break
            all_repos.extend(repos)
            if len(repos) < 100:
                break
            page += 1
            # Para evitar loops infinitos acidentais
            if page > 50:
                break

        self.stats["total"] = len(all_repos)
        self.log(f"Encontrados {len(all_repos)} repositórios", "SUCCESS")
        return all_repos

    def analyze_repo_age(self, repo: Dict) -> int:
        """Calcula idade do repositório em dias (UTC aware)"""
        # Formato ISO 8601 do GitHub: 2024-01-14T05:25:19Z
        updated_str = repo["updated_at"].replace("Z", "+00:00")
        updated = datetime.fromisoformat(updated_str)
        now = datetime.now(timezone.utc)
        return (now - updated).days

    def should_archive(self, repo: Dict) -> bool:
        """Determina se repositório deve ser arquivado"""
        # Já arquivado
        if repo["archived"]:
            return False

        # Idade maior que 1 ano
        age = self.analyze_repo_age(repo)
        if age > 365:
            # Sem stars ou forks
            if repo["stargazers_count"] == 0 and repo["forks_count"] == 0:
                return True

        return False

    def should_delete(self, repo: Dict) -> bool:
        """Determina se repositório deve ser deletado"""
        # Repositórios temporários ou de teste
        temp_keywords = ["temp-", "test-", "demo-", "experiment-"]

        for keyword in temp_keywords:
            if repo["name"].lower().startswith(keyword):
                # Sem atividade há mais de 3 meses
                age = self.analyze_repo_age(repo)
                if age > 90:
                    return True

        return False

    def categorize_repos(self, repos: List[Dict]) -> Dict[str, List[Dict]]:
        """Categoriza repositórios por ação recomendada"""
        categories = {"to_archive": [], "to_delete": [], "to_update": [], "active": []}

        for repo in repos:
            if self.should_delete(repo):
                categories["to_delete"].append(repo)
            elif self.should_archive(repo):
                categories["to_archive"].append(repo)
            elif not repo.get("description"):
                categories["to_update"].append(repo)
            else:
                categories["active"].append(repo)

        return categories

    def archive_old_repos(self, repos: List[Dict]):
        """Arquiva repositórios antigos"""
        if not repos:
            self.log("Nenhum repositório para arquivar", "INFO")
            return

        self.log(f"Repositórios para arquivar: {len(repos)}", "WARNING")

        for repo in repos:
            age = self.analyze_repo_age(repo)
            self.log(
                f"  {repo['name']} - {age} dias sem atualização",
                "DRY_RUN" if self.dry_run else "INFO",
            )

        if self.dry_run:
            self.log("DRY RUN: Arquivamento não executado", "DRY_RUN")
            return

        # Executar arquivamento
        repo_tuples = [(self.gh.user, r["name"]) for r in repos]
        results = self.gh.archive_multiple(repo_tuples)

        self.stats["archived"] = len(results["success"])
        self.log(f"Arquivados: {len(results['success'])}", "SUCCESS")

        if results["failed"]:
            self.log(f"Falhas: {len(results['failed'])}", "ERROR")

    def delete_temp_repos(self, repos: List[Dict]):
        """Deleta repositórios temporários"""
        if not repos:
            self.log("Nenhum repositório para deletar", "INFO")
            return

        self.log(f"Repositórios para deletar: {len(repos)}", "WARNING")

        for repo in repos:
            self.log(
                f"  {repo['name']} - temporário/teste",
                "DRY_RUN" if self.dry_run else "INFO",
            )

        if self.dry_run:
            self.log("DRY RUN: Deleção não executada", "DRY_RUN")
            return

        # Confirmação adicional
        if not self.force:
            print("\n⚠️  ATENÇÃO: Você está prestes a DELETAR repositórios!")
            print("Esta ação é IRREVERSÍVEL!")
            response = input("Digite 'DELETE ALL' para confirmar: ")

            if response != "DELETE ALL":
                self.log("Deleção cancelada pelo usuário", "WARNING")
                return

        # Executar deleção
        repo_tuples = [(self.gh.user, r["name"]) for r in repos]
        results = self.gh.delete_multiple(repo_tuples, confirm=True)

        self.stats["deleted"] = len(results["success"])
        self.log(f"Deletados: {len(results['success'])}", "SUCCESS")

        if results["failed"]:
            self.log(f"Falhas: {len(results['failed'])}", "ERROR")

    def update_descriptions(self, repos: List[Dict]):
        """Adiciona descrição padrão em repos sem descrição"""
        if not repos:
            self.log("Nenhum repositório para atualizar", "INFO")
            return

        self.log(f"Repositórios sem descrição: {len(repos)}", "WARNING")

        for repo in repos:
            # Gera descrição baseada no nome
            name = repo["name"].replace("-", " ").replace("_", " ").title()
            description = f"Projeto: {name}"

            self.log(
                f"  {repo['name']} -> '{description}'",
                "DRY_RUN" if self.dry_run else "INFO",
            )

            if not self.dry_run:
                try:
                    self.gh.update_repo(
                        owner=self.gh.user, repo=repo["name"], description=description
                    )
                    self.stats["updated"] += 1
                except Exception as e:
                    self.log(f"Erro ao atualizar {repo['name']}: {e}", "ERROR")

        if self.dry_run:
            self.log("DRY RUN: Atualização não executada", "DRY_RUN")
        else:
            self.log(f"Atualizados: {self.stats['updated']}", "SUCCESS")

    def organize_by_topics(self, repos: List[Dict]):
        """Organiza repositórios por linguagem usando topics"""
        self.log("Organizando por topics...")

        for repo in repos:
            if repo["archived"]:
                continue

            language = repo.get("language", "").lower()
            if not language:
                continue

            # No modo DRY_RUN, assumimos que precisamos adicionar se a linguagem
            # não for um tópico óbvio (simplificação para evitar chamadas de API)
            if self.dry_run:
                self.log(f"  {repo['name']} -> adicionar topic '{language}'", "DRY_RUN")
                continue

            # Adiciona topic da linguagem se não existir
            try:
                current_topics = self.gh.get_topics(self.gh.user, repo["name"])

                if language not in current_topics:
                    self.log(
                        f"  {repo['name']} -> adicionando topic '{language}'", "INFO"
                    )
                    self.gh.add_topics(
                        owner=self.gh.user, repo=repo["name"], topics=[language]
                    )
            except Exception as e:
                self.log(f"Erro ao adicionar topic em {repo['name']}: {e}", "ERROR")

    def print_report(self, categories: Dict[str, List[Dict]]):
        """Imprime relatório detalhado"""
        print("\n" + "=" * 60)
        print("RELATÓRIO DE ORGANIZAÇÃO DE REPOSITÓRIOS")
        print("=" * 60 + "\n")

        print(f"Total de repositórios: {self.stats['total']}\n")

        print(f"📊 Categorias:")
        print(f"  🔒 Para arquivar: {len(categories['to_archive'])}")
        print(f"  🗑️  Para deletar: {len(categories['to_delete'])}")
        print(f"  📝 Sem descrição: {len(categories['to_update'])}")
        print(f"  ✅ Ativos e organizados: {len(categories['active'])}\n")

        if not self.dry_run:
            print(f"📈 Ações executadas:")
            print(f"  Arquivados: {self.stats['archived']}")
            print(f"  Deletados: {self.stats['deleted']}")
            print(f"  Atualizados: {self.stats['updated']}\n")

        print("=" * 60)

    def run(
        self,
        archive: bool = True,
        delete: bool = False,
        update: bool = True,
        organize_topics: bool = True,
    ):
        """
        Executa workflow completo

        Args:
            archive: Arquivar repos antigos
            delete: Deletar repos temporários
            update: Atualizar descrições
            organize_topics: Organizar por topics
        """
        print("\n" + "=" * 60)
        print(f"WORKFLOW DE ORGANIZAÇÃO - {'DRY RUN' if self.dry_run else 'MODO REAL'}")
        print("=" * 60 + "\n")

        if self.dry_run:
            self.log("Modo DRY RUN ativo - nenhuma mudança será feita", "WARNING")

        # 1. Carregar repositórios
        repos = self.get_all_repos()

        # 2. Categorizar
        self.log("Categorizando repositórios...")
        categories = self.categorize_repos(repos)

        # 3. Arquivar
        if archive:
            print("\n📦 ARQUIVAMENTO")
            print("-" * 60)
            self.archive_old_repos(categories["to_archive"])

        # 4. Deletar
        if delete:
            print("\n🗑️  DELEÇÃO")
            print("-" * 60)
            self.delete_temp_repos(categories["to_delete"])

        # 5. Atualizar
        if update:
            print("\n📝 ATUALIZAÇÃO")
            print("-" * 60)
            self.update_descriptions(categories["to_update"])

        # 6. Organizar por topics
        if organize_topics:
            print("\n🏷️  ORGANIZAÇÃO POR TOPICS")
            print("-" * 60)
            self.organize_by_topics(repos)

        # 7. Relatório final
        self.print_report(categories)


def main():
    """Ponto de entrada"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Workflow de organização de repositórios GitHub"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Executar ações (padrão: dry-run)"
    )
    parser.add_argument(
        "--no-archive", action="store_true", help="Não arquivar repos antigos"
    )
    parser.add_argument(
        "--delete", action="store_true", help="Deletar repos temporários"
    )
    parser.add_argument(
        "--no-update", action="store_true", help="Não atualizar descrições"
    )
    parser.add_argument(
        "--force", action="store_true", help="Ignorar confirmações extras (perigoso)"
    )

    args = parser.parse_args()

    # Inicializar organizador
    organizer = RepoOrganizer(dry_run=not args.execute, force=args.force)

    try:
        # Executar workflow
        organizer.run(
            archive=not args.no_archive,
            delete=args.delete,
            update=not args.no_update,
            organize_topics=not args.no_topics,
        )

        print("\n✓ Workflow concluído com sucesso!")

        if not args.execute:
            print("\nPara executar as ações, rode com --execute")

    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
