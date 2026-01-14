#!/usr/bin/env python3
"""
Gerador de Documentos Oficiais Brasileiros

Gera documentos oficiais (ofícios, memorandos, etc.) a partir de templates LaTeX,
preenchendo placeholders com dados fornecidos e compilando para PDF.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime


class DocumentGenerator:
    """Gera documentos oficiais brasileiros a partir de templates LaTeX."""

    MESES = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro",
    }

    def __init__(self, template_dir: str = None):
        """
        Inicializa o gerador.

        Args:
            template_dir: Diretório contendo templates LaTeX (padrão: ./assets)
        """
        if template_dir is None:
            # Assume que script está em scripts/ e templates em assets/
            script_dir = Path(__file__).parent
            self.template_dir = script_dir.parent / "assets"
        else:
            self.template_dir = Path(template_dir)

        if not self.template_dir.exists():
            raise FileNotFoundError(
                f"Diretório de templates não encontrado: {self.template_dir}"
            )

    @staticmethod
    def escapar_latex(texto: str) -> str:
        """
        Escapa caracteres especiais do LaTeX para evitar injeção.

        Args:
            texto: Texto simples

        Returns:
            Texto escapado para LaTeX
        """
        if not isinstance(texto, str):
            return str(texto)

        # Ordem importa: \ deve ser o primeiro
        mapa = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }

        regex = re.compile("|".join(re.escape(str(key)) for key in mapa.keys()))
        return regex.sub(lambda mo: mapa[mo.group()], texto)

    @staticmethod
    def formatar_data_extenso(data: datetime = None) -> str:
        """
        Formata data por extenso no padrão brasileiro.

        Args:
            data: Data a formatar (padrão: hoje)

        Returns:
            Data formatada (ex: "13 de janeiro de 2025")
        """
        if data is None:
            data = datetime.now()
        return f"{data.day} de {DocumentGenerator.MESES[data.month]} de {data.year}"

    def carregar_template(self, tipo: str) -> str:
        """
        Carrega template LaTeX.

        Args:
            tipo: Tipo do documento ('oficio', 'memorando', etc.)

        Returns:
            Conteúdo do template
        """
        template_file = self.template_dir / f"template_{tipo}.tex"

        if not template_file.exists():
            raise FileNotFoundError(f"Template não encontrado: {template_file}")

        return template_file.read_text(encoding="utf-8")

    def preencher_template(self, template: str, dados: Dict[str, str]) -> str:
        """
        Preenche placeholders do template com dados fornecidos.

        Args:
            template: Conteúdo do template LaTeX
            dados: Dicionário com valores para placeholders

        Returns:
            Template preenchido
        """
        conteudo = template

        for chave, valor in dados.items():
            placeholder = f"{{{{{chave}}}}}"
            # O corpo do texto pode conter \par deliberado, outros campos devem ser escapados
            if chave == "CORPO_TEXTO":
                # Escapamos minimamente se não quisermos permitir LaTeX total
                valor_processado = valor
            else:
                valor_processado = self.escapar_latex(valor)

            conteudo = conteudo.replace(placeholder, valor_processado)

        return conteudo

    def compilar_latex(self, conteudo: str, output_path: str) -> bool:
        """
        Compila LaTeX para PDF.

        Args:
            conteudo: Conteúdo LaTeX
            output_path: Caminho para salvar PDF

        Returns:
            True se compilação bem-sucedida
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if not shutil.which("pdflatex"):
            print("Erro: 'pdflatex' não encontrado no PATH.", file=sys.stderr)
            return False

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Salvar .tex temporário
            tex_file = tmpdir_path / "documento.tex"
            tex_file.write_text(conteudo, encoding="utf-8")

            # Compilar com pdflatex (2 passagens para referências)
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "documento.tex"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                )

            # Verificar se PDF foi gerado
            pdf_file = tmpdir_path / "documento.pdf"
            if not pdf_file.exists():
                # Exibir log de erros
                log_file = tmpdir_path / "documento.log"
                if log_file.exists():
                    print("Erro na compilação LaTeX:", file=sys.stderr)
                    print(
                        log_file.read_text(encoding="utf-8", errors="ignore")[-2000:],
                        file=sys.stderr,
                    )
                return False

            # Copiar PDF para destino
            shutil.copy(pdf_file, output_path)
            return True

    def gerar_oficio(
        self,
        output_path: str,
        numero: str,
        destinatario: Dict[str, str],
        assunto: str,
        corpo_texto: str,
        signatario: Dict[str, str],
        orgao: Dict[str, str],
        data: datetime = None,
        fecho: str = "Atenciosamente",
        vocativo: str = "Senhor",
    ) -> bool:
        """
        Gera um ofício oficial.

        Args:
            output_path: Caminho para salvar PDF
            numero: Número do ofício (ex: "123")
            destinatario: Dict com nome, cargo, endereco, cidade, uf
            assunto: Assunto do ofício
            corpo_texto: Texto do ofício (parágrafos separados por \\par)
            signatario: Dict com nome e cargo
            orgao: Dict com nome, sigla, cidade
            data: Data do documento (padrão: hoje)
            fecho: Fecho oficial (padrão: "Atenciosamente")
            vocativo: Vocativo (padrão: "Senhor")

        Returns:
            True se geração bem-sucedida
        """
        if data is None:
            data = datetime.now()

        # Validar dados obrigatórios
        for dict_name, d, keys in [
            ("destinatario", destinatario, ["nome", "cargo"]),
            ("signatario", signatario, ["nome", "cargo"]),
            ("orgao", orgao, ["sigla", "nome", "cidade"]),
        ]:
            for key in keys:
                if key not in d or not d[key]:
                    raise KeyError(
                        f"Chave '{key}' obrigatória faltando em '{dict_name}'"
                    )

        template = self.carregar_template("oficio")

        dados = {
            "NUMERO": numero,
            "ANO": str(data.year),
            "SIGLA_ORGAO": orgao["sigla"],
            "NOME_ORGAO": orgao["nome"],
            "CIDADE": orgao["cidade"],
            "DATA_EXTENSO": self.formatar_data_extenso(data),
            "NOME_DESTINATARIO": destinatario["nome"],
            "CARGO_DESTINATARIO": destinatario["cargo"],
            "ENDERECO_DESTINATARIO": destinatario.get("endereco", ""),
            "CIDADE_DESTINATARIO": destinatario.get("cidade", ""),
            "UF_DESTINATARIO": destinatario.get("uf", ""),
            "ASSUNTO": assunto,
            "VOCATIVO": vocativo,
            "CORPO_TEXTO": corpo_texto,
            "FECHO": fecho,
            "NOME_SIGNATARIO": signatario["nome"],
            "CARGO_SIGNATARIO": signatario["cargo"],
        }

        conteudo = self.preencher_template(template, dados)
        return self.compilar_latex(conteudo, output_path)

    def gerar_memorando(
        self,
        output_path: str,
        numero: str,
        destinatario_setor: str,
        assunto: str,
        corpo_texto: str,
        signatario: Dict[str, str],
        orgao: Dict[str, str],
        data: datetime = None,
    ) -> bool:
        """
        Gera um memorando oficial.

        Args:
            output_path: Caminho para salvar PDF
            numero: Número do memorando
            destinatario_setor: Setor/órgão destinatário
            assunto: Assunto do memorando
            corpo_texto: Texto do memorando
            signatario: Dict com nome e cargo
            orgao: Dict com nome, sigla, cidade
            data: Data do documento (padrão: hoje)

        Returns:
            True se geração bem-sucedida
        """
        if data is None:
            data = datetime.now()

        template = self.carregar_template("memorando")

        dados = {
            "NUMERO": numero,
            "ANO": str(data.year),
            "SIGLA_ORGAO": orgao["sigla"],
            "NOME_ORGAO": orgao["nome"],
            "CIDADE": orgao["cidade"],
            "DATA_EXTENSO": self.formatar_data_extenso(data),
            "DESTINATARIO_SETOR": destinatario_setor,
            "ASSUNTO": assunto,
            "CORPO_TEXTO": corpo_texto,
            "NOME_SIGNATARIO": signatario["nome"],
            "CARGO_SIGNATARIO": signatario["cargo"],
        }

        conteudo = self.preencher_template(template, dados)
        return self.compilar_latex(conteudo, output_path)


def exemplo_uso():
    """Demonstra uso do gerador."""
    generator = DocumentGenerator()

    # Exemplo: Gerar ofício
    print("Gerando ofício...")
    sucesso = generator.gerar_oficio(
        output_path="oficio_exemplo.pdf",
        numero="123",
        destinatario={
            "nome": "João da Silva",
            "cargo": "Diretor do Departamento de Administração",
            "endereco": "Esplanada dos Ministérios, Bloco A",
            "cidade": "Brasília",
            "uf": "DF",
        },
        assunto="Solicitação de informações sobre processo administrativo",
        corpo_texto=r"""
Solicito a Vossa Senhoria informações detalhadas sobre o processo administrativo nº 12345/2025,
conforme previsto no art. 5º da Lei nº 9.784/99.

\par

As informações são necessárias para subsidiar análise técnica em andamento nesta Coordenação,
com prazo de conclusão previsto para o dia 31 de janeiro de 2025.

\par

Agradeço antecipadamente pela atenção dispensada ao presente pedido.
        """.strip(),
        signatario={
            "nome": "Maria Oliveira",
            "cargo": "Coordenadora-Geral de Planejamento",
        },
        orgao={
            "nome": "MINISTÉRIO DA ADMINISTRAÇÃO",
            "sigla": "MA",
            "cidade": "Brasília",
        },
        fecho="Atenciosamente",
        vocativo="Senhor Diretor",
    )

    if sucesso:
        print("✓ Ofício gerado com sucesso: oficio_exemplo.pdf")
    else:
        print("✗ Erro ao gerar ofício", file=sys.stderr)
        return 1

    # Exemplo: Gerar memorando
    print("\nGerando memorando...")
    sucesso = generator.gerar_memorando(
        output_path="memorando_exemplo.pdf",
        numero="045",
        destinatario_setor="Coordenação de Recursos Humanos",
        assunto="Encaminhamento de documentação",
        corpo_texto=r"""
Encaminho a documentação solicitada pelo Memorando nº 234/2025-CRH,
referente à concessão de férias do servidor Pedro Santos, matrícula 98765.

\par

Os documentos anexos já foram devidamente autuados e seguem para análise dessa Coordenação.
        """.strip(),
        signatario={"nome": "Carlos Pereira", "cargo": "Chefe de Divisão"},
        orgao={
            "nome": "DEPARTAMENTO DE GESTÃO DE PESSOAS",
            "sigla": "DGP",
            "cidade": "Brasília",
        },
    )

    if sucesso:
        print("✓ Memorando gerado com sucesso: memorando_exemplo.pdf")
    else:
        print("✗ Erro ao gerar memorando", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(exemplo_uso())
