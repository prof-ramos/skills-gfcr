#!/usr/bin/env python3
"""
GitHub Repository Manager
Módulo para gerenciar repositórios GitHub via API REST
Requer: GH_TOKEN como variável de ambiente
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Visibility(Enum):
    """Enum para visibilidade de repositórios"""

    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class RepoConfig:
    """Configuração para criação/atualização de repositório"""

    name: str
    description: Optional[str] = None
    homepage: Optional[str] = None
    private: bool = False
    has_issues: bool = True
    has_projects: bool = True
    has_wiki: bool = True
    auto_init: bool = False
    default_branch: str = "main"


class GitHubRepoManager:
    """Gerenciador de repositórios GitHub via API REST"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        """
        Inicializa o gerenciador

        Args:
            token: GitHub Personal Access Token (ou usa GH_TOKEN do ambiente)
        """
        self.token = token or os.getenv("GH_TOKEN")
        if not self.token:
            raise ValueError(
                "GH_TOKEN não encontrado. Configure a variável de ambiente ou passe o token."
            )

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Valida token e obtém usuário autenticado
        self.user = self._get_authenticated_user()

    def _get_authenticated_user(self) -> str:
        """Obtém o usuário autenticado"""
        response = requests.get(
            f"{self.BASE_URL}/user", headers=self.headers, timeout=10
        )
        response.raise_for_status()
        return response.json()["login"]

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Faz requisição à API do GitHub

        Args:
            method: Método HTTP (GET, POST, PATCH, DELETE)
            endpoint: Endpoint da API (ex: /repos/owner/repo)
            data: Dados JSON para enviar
            params: Parâmetros de query string

        Returns:
            Response object
        """
        url = f"{self.BASE_URL}{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data,
            params=params,
            timeout=10,
        )

        return response

    # ==================== OPERAÇÕES DE LEITURA ====================

    def list_repos(
        self,
        username: Optional[str] = None,
        type_filter: str = "all",
        sort: str = "updated",
        per_page: int = 30,
    ) -> List[Dict]:
        """
        Lista repositórios

        Args:
            username: Usuário (None = usuário autenticado)
            type_filter: Filtro (all, owner, public, private, member)
            sort: Ordenação (created, updated, pushed, full_name)
            per_page: Resultados por página

        Returns:
            Lista de repositórios
        """
        if username:
            endpoint = f"/users/{username}/repos"
            params = {"type": type_filter, "sort": sort, "per_page": per_page}
        else:
            endpoint = "/user/repos"
            # Affiliation/Visibility mapping for /user/repos
            if type_filter in ["all", "public", "private"]:
                params = {"visibility": type_filter, "sort": sort, "per_page": per_page}
            else:
                params = {"type": type_filter, "sort": sort, "per_page": per_page}

        response = self._make_request("GET", endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_repo(self, owner: str, repo: str) -> Dict:
        """
        Obtém detalhes de um repositório

        Args:
            owner: Dono do repositório
            repo: Nome do repositório

        Returns:
            Dados do repositório
        """
        response = self._make_request("GET", f"/repos/{owner}/{repo}")
        response.raise_for_status()
        return response.json()

    # ==================== ARQUIVAMENTO ====================

    def archive_repo(self, owner: str, repo: str) -> Dict:
        """
        Arquiva um repositório (torna read-only)

        Args:
            owner: Dono do repositório
            repo: Nome do repositório

        Returns:
            Dados do repositório arquivado
        """
        data = {"archived": True}
        response = self._make_request("PATCH", f"/repos/{owner}/{repo}", data=data)
        response.raise_for_status()
        return response.json()

    def unarchive_repo(self, owner: str, repo: str) -> Dict:
        """
        Desarquiva um repositório

        Args:
            owner: Dono do repositório
            repo: Nome do repositório

        Returns:
            Dados do repositório desarquivado
        """
        data = {"archived": False}
        response = self._make_request("PATCH", f"/repos/{owner}/{repo}", data=data)
        response.raise_for_status()
        return response.json()

    # ==================== EXCLUSÃO ====================

    def delete_repo(self, owner: str, repo: str, confirm: bool = False) -> bool:
        """
        Apaga um repositório (AÇÃO IRREVERSÍVEL!)

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            confirm: Confirmação de exclusão (segurança)

        Returns:
            True se deletado com sucesso

        Raises:
            ValueError: Se confirm=False
        """
        if not confirm:
            raise ValueError(
                f"ATENÇÃO: Esta ação é IRREVERSÍVEL! "
                f"Para deletar {owner}/{repo}, chame delete_repo('{owner}', '{repo}', confirm=True)"
            )

        response = self._make_request("DELETE", f"/repos/{owner}/{repo}")

        if response.status_code == 204:
            return True

        response.raise_for_status()
        return False

    # ==================== ATUALIZAÇÃO ====================

    def update_repo(
        self,
        owner: str,
        repo: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        homepage: Optional[str] = None,
        private: Optional[bool] = None,
        has_issues: Optional[bool] = None,
        has_projects: Optional[bool] = None,
        has_wiki: Optional[bool] = None,
        default_branch: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> Dict:
        """
        Atualiza configurações do repositório

        Args:
            owner: Dono do repositório
            repo: Nome do repositório atual
            name: Novo nome do repositório
            description: Nova descrição
            homepage: Nova URL do site
            private: Tornar privado/público
            has_issues: Habilitar issues
            has_projects: Habilitar projects
            has_wiki: Habilitar wiki
            default_branch: Branch padrão
            archived: Arquivar/desarquivar

        Returns:
            Dados do repositório atualizado
        """
        data = {}

        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if homepage is not None:
            data["homepage"] = homepage
        if private is not None:
            data["private"] = private
        if has_issues is not None:
            data["has_issues"] = has_issues
        if has_projects is not None:
            data["has_projects"] = has_projects
        if has_wiki is not None:
            data["has_wiki"] = has_wiki
        if default_branch is not None:
            data["default_branch"] = default_branch
        if archived is not None:
            data["archived"] = archived

        response = self._make_request("PATCH", f"/repos/{owner}/{repo}", data=data)
        response.raise_for_status()
        return response.json()

    def update_visibility(self, owner: str, repo: str, private: bool) -> Dict:
        """
        Atualiza visibilidade do repositório

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            private: True para privado, False para público

        Returns:
            Dados do repositório atualizado
        """
        return self.update_repo(owner, repo, private=private)

    # ==================== TOPICS (TAGS) ====================

    def get_topics(self, owner: str, repo: str) -> List[str]:
        """
        Obtém topics (tags) do repositório

        Args:
            owner: Dono do repositório
            repo: Nome do repositório

        Returns:
            Lista de topics
        """
        response = self._make_request("GET", f"/repos/{owner}/{repo}/topics")
        response.raise_for_status()
        return response.json()["names"]

    def set_topics(self, owner: str, repo: str, topics: List[str]) -> List[str]:
        """
        Define topics (tags) do repositório

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            topics: Lista de topics (máx 20, lowercase, alphanumeric + hífens)

        Returns:
            Lista de topics atualizada
        """
        # Normaliza topics
        normalized_topics = [t.lower().strip() for t in topics[:20]]

        response = self._make_request(
            "PUT", f"/repos/{owner}/{repo}/topics", data={"names": normalized_topics}
        )
        response.raise_for_status()
        return response.json()["names"]

    def add_topics(self, owner: str, repo: str, topics: List[str]) -> List[str]:
        """
        Adiciona topics ao repositório (mantém existentes)

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            topics: Lista de topics para adicionar

        Returns:
            Lista completa de topics
        """
        current = self.get_topics(owner, repo)
        new_topics = list(set(current + topics))
        return self.set_topics(owner, repo, new_topics)

    # ==================== CRIAÇÃO ====================

    def create_repo(self, config: RepoConfig) -> Dict:
        """
        Cria um novo repositório

        Args:
            config: Configuração do repositório

        Returns:
            Dados do repositório criado
        """
        data = {
            "name": config.name,
            "description": config.description,
            "homepage": config.homepage,
            "private": config.private,
            "has_issues": config.has_issues,
            "has_projects": config.has_projects,
            "has_wiki": config.has_wiki,
            "auto_init": config.auto_init,
        }

        response = self._make_request("POST", "/user/repos", data=data)
        response.raise_for_status()
        repo_data = response.json()

        # Se default_branch for diferente de 'main' ou do default do GitHub, aplica PATCH
        if config.default_branch and config.default_branch != repo_data.get(
            "default_branch"
        ):
            try:
                self.update_repo(
                    self.user, config.name, default_branch=config.default_branch
                )
            except Exception as e:
                print(
                    f"Aviso: Não foi possível alterar branch padrão para {config.default_branch}: {e}"
                )

        return repo_data

    # ==================== OPERAÇÕES EM LOTE ====================

    def archive_multiple(self, repos: List[tuple[str, str]]) -> Dict[str, Any]:
        """
        Arquiva múltiplos repositórios

        Args:
            repos: Lista de tuplas (owner, repo)

        Returns:
            Dict com sucessos e falhas
        """
        results = {"success": [], "failed": []}

        for owner, repo in repos:
            try:
                self.archive_repo(owner, repo)
                results["success"].append(f"{owner}/{repo}")
            except Exception as e:
                results["failed"].append({"repo": f"{owner}/{repo}", "error": str(e)})

        return results

    def unarchive_multiple(self, repos: List[tuple[str, str]]) -> Dict[str, Any]:
        """
        Desarquiva múltiplos repositórios

        Args:
            repos: Lista de tuplas (owner, repo)

        Returns:
            Dict com sucessos e falhas
        """
        results = {"success": [], "failed": []}

        for owner, repo in repos:
            try:
                self.unarchive_repo(owner, repo)
                results["success"].append(f"{owner}/{repo}")
            except Exception as e:
                results["failed"].append({"repo": f"{owner}/{repo}", "error": str(e)})

        return results

    def delete_multiple(
        self, repos: List[tuple[str, str]], confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Deleta múltiplos repositórios

        Args:
            repos: Lista de tuplas (owner, repo)
            confirm: Confirmação de exclusão (segurança)

        Returns:
            Dict com sucessos e falhas
        """
        if not confirm:
            raise ValueError(
                "ATENÇÃO: Esta ação é IRREVERSÍVEL! "
                "Para deletar múltiplos repos, passe confirm=True"
            )

        results = {"success": [], "failed": []}

        for owner, repo in repos:
            try:
                self.delete_repo(owner, repo, confirm=True)
                results["success"].append(f"{owner}/{repo}")
            except Exception as e:
                results["failed"].append({"repo": f"{owner}/{repo}", "error": str(e)})

        return results


def main():
    """Exemplo de uso"""
    try:
        # Inicializa gerenciador
        gh = GitHubRepoManager()
        print(f"✓ Autenticado como: {gh.user}\n")

        # Lista repositórios
        print("Seus repositórios:")
        repos = gh.list_repos(per_page=5)
        for repo in repos:
            status = "🔒 ARQUIVADO" if repo["archived"] else "✓ Ativo"
            visibility = "🔐 Privado" if repo["private"] else "🌐 Público"
            print(f"  {status} {visibility} - {repo['full_name']}")

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
