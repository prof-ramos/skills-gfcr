#!/usr/bin/env python3
"""
Validador de Documentos Oficiais Brasileiros

Valida se documentos oficiais seguem as normas do Manual de Redação da Presidência
e outras diretrizes aplicáveis.
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path


class ValidadorDocumento:
    """Valida documentos oficiais brasileiros quanto a normas e padrões."""

    # Pronomes de tratamento válidos
    PRONOMES_TRATAMENTO = {
        "vossa excelência",
        "v. ex.ª",
        "v.ex.ª",
        "v.exa.",
        "vossa senhoria",
        "v. s.ª",
        "v.s.ª",
        "v.sa.",
        "vossa magnificência",
        "v. mag.ª",
    }

    # Fechos válidos
    FECHOS_VALIDOS = {"atenciosamente", "respeitosamente"}

    # Padrões de numeração válidos
    PADRAO_NUMERO_DOC = re.compile(
        r"(Ofício|Memorando|Parecer|NT|EM)\s+n[°º]\s*\d+/\d{4}-[A-Z]+", re.IGNORECASE
    )

    def __init__(self):
        """Inicializa validador."""
        self.avisos: List[Dict[str, str]] = []
        self.erros: List[Dict[str, str]] = []

    def limpar_resultados(self):
        """Limpa avisos e erros acumulados."""
        self.avisos = []
        self.erros = []

    def adicionar_aviso(self, tipo: str, mensagem: str, linha: int = None):
        """Adiciona aviso de validação."""
        aviso = {"tipo": tipo, "mensagem": mensagem}
        if linha is not None:
            aviso["linha"] = linha
        self.avisos.append(aviso)

    def adicionar_erro(self, tipo: str, mensagem: str, linha: int = None):
        """Adiciona erro de validação."""
        erro = {"tipo": tipo, "mensagem": mensagem}
        if linha is not None:
            erro["linha"] = linha
        self.erros.append(erro)

    def validar_numeracao(self, texto: str) -> bool:
        """
        Valida formato de numeração do documento.

        Args:
            texto: Texto do documento

        Returns:
            True se numeração válida
        """
        match = self.PADRAO_NUMERO_DOC.search(texto)

        if not match:
            self.adicionar_erro(
                "numeracao",
                "Numeração de documento não encontrada ou em formato inválido. "
                "Use: [Tipo] nº XXX/AAAA-SIGLA",
            )
            return False

        return True

    def validar_pronomes_tratamento(self, texto: str) -> bool:
        """
        Valida uso de pronomes de tratamento.

        Args:
            texto: Texto do documento

        Returns:
            True se pronomes válidos
        """
        texto_lower = texto.lower()

        # Verificar concordância verbal (3ª pessoa)
        problemas_concordancia = [
            (
                r"vossa\s+excelência\s+\w*stes\b",
                'Usar 3ª pessoa: "solicitou" não "solicitastes"',
            ),
            (
                r"vossa\s+senhoria\s+\w*stes\b",
                'Usar 3ª pessoa: "enviou" não "enviastes"',
            ),
            (r"vossa\s+excelência\s+podeis\b", 'Usar 3ª pessoa: "pode" não "podeis"'),
        ]

        for padrao, msg in problemas_concordancia:
            if re.search(padrao, texto_lower):
                self.adicionar_erro("concordancia", msg)
                return False

        return True

    def validar_fecho(self, texto: str) -> bool:
        """
        Valida fecho do documento.

        Args:
            texto: Texto do documento

        Returns:
            True se fecho válido
        """
        # Buscar fecho (geralmente perto do final)
        linhas = texto.split("\n")
        ultimas_linhas = "\n".join(linhas[-20:]).lower()

        fecho_encontrado = any(fecho in ultimas_linhas for fecho in self.FECHOS_VALIDOS)

        if not fecho_encontrado:
            self.adicionar_aviso(
                "fecho",
                'Fecho não encontrado ou inválido. Use "Atenciosamente," ou "Respeitosamente,"',
            )
            return False

        return True

    def validar_paragrafos(self, texto: str) -> bool:
        """
        Valida estrutura de parágrafos.

        Args:
            texto: Texto do documento

        Returns:
            True se parágrafos adequados
        """
        paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]

        # Parágrafos muito longos (>8 linhas)
        for i, paragrafo in enumerate(paragrafos, 1):
            linhas = paragrafo.count("\n") + 1
            if linhas > 8:
                self.adicionar_aviso(
                    "paragrafo",
                    f"Parágrafo {i} muito longo ({linhas} linhas). "
                    "Recomendação: 2-6 linhas por parágrafo",
                    linha=i,
                )

        return True

    def validar_citacoes_legais(self, texto: str) -> bool:
        """
        Valida citações legais.

        Args:
            texto: Texto do documento

        Returns:
            True se citações válidas
        """
        # Padrões incorretos comuns
        padroes_incorretos = [
            (r"art\.\s+\d+º", 'Usar "art. X" sem símbolo de grau'),
            (
                r"lei\s+\d+/\d{4}",
                'Usar "Lei nº X/AAAA" ou "Lei nº X, de DD de MMMM de AAAA"',
            ),
            (r"CF/\d{2}(?!\d)", 'Usar "CF/88" ou "Constituição Federal de 1988"'),
        ]

        for padrao, msg in padroes_incorretos:
            if re.search(padrao, texto, re.IGNORECASE):
                self.adicionar_aviso("citacao_legal", msg)

        return True

    def validar_datas(self, texto: str) -> bool:
        """
        Valida formato de datas.

        Args:
            texto: Texto do documento

        Returns:
            True se datas válidas
        """
        # Datas com hífen (incorreto em documentos oficiais)
        if re.search(r"\d{2}-\d{2}-\d{4}", texto):
            self.adicionar_erro("data", 'Usar "/" ou "." para separar datas, não "-"')
            return False

        return True

    def validar_formatacao_geral(self, texto: str) -> bool:
        """
        Valida formatação geral do documento.

        Args:
            texto: Texto do documento

        Returns:
            True se formatação adequada
        """
        # Múltiplas linhas em branco consecutivas
        if re.search(r"\n{4,}", texto):
            self.adicionar_aviso(
                "formatacao", "Evitar mais de 2 linhas em branco consecutivas"
            )

        # Espaços múltiplos
        if re.search(r" {3,}", texto):
            self.adicionar_aviso("formatacao", "Evitar múltiplos espaços consecutivos")

        return True

    def validar_linguagem(self, texto: str) -> bool:
        """
        Valida linguagem utilizada.

        Args:
            texto: Texto do documento

        Returns:
            True se linguagem adequada
        """
        # Primeira pessoa (a evitar em documentos oficiais)
        primeira_pessoa = [
            r"\beu\b",
            r"\bmeu\b",
            r"\bminha\b",
            r"\bmeus\b",
            r"\bminhas\b",
            r"\bme\b",
            r"\bcomigo\b",
        ]

        for padrao in primeira_pessoa:
            if re.search(padrao, texto, re.IGNORECASE):
                self.adicionar_aviso(
                    "linguagem", "Evitar primeira pessoa. Usar linguagem impessoal"
                )
                break

        # Expressões coloquiais
        coloquialismos = [
            (r"\btipo assim\b", "tipo assim"),
            (r"\bmeio que\b", "meio que"),
            (r"\btipo\b", "tipo"),
            (r"\btipo um\b", "tipo um"),
        ]
        for padrao, exp in coloquialismos:
            if re.search(padrao, texto, re.IGNORECASE):
                self.adicionar_aviso(
                    "linguagem",
                    f'Expressão coloquial detectada: "{exp}". Usar linguagem formal',
                )

        return True

    def validar_documento(self, texto: str, tipo_doc: str = None) -> Tuple[bool, Dict]:
        """
        Executa validação completa do documento.

        Args:
            texto: Texto do documento
            tipo_doc: Tipo do documento (opcional)

        Returns:
            Tupla (sucesso, resultados) onde resultados contém avisos e erros
        """
        self.limpar_resultados()

        # Executar validações
        self.validar_numeracao(texto)
        self.validar_pronomes_tratamento(texto)
        self.validar_fecho(texto)
        self.validar_paragrafos(texto)
        self.validar_citacoes_legais(texto)
        self.validar_datas(texto)
        self.validar_formatacao_geral(texto)
        self.validar_linguagem(texto)

        # Resultado
        sucesso = len(self.erros) == 0

        return sucesso, {
            "erros": self.erros,
            "avisos": self.avisos,
            "total_erros": len(self.erros),
            "total_avisos": len(self.avisos),
        }

    def imprimir_resultados(self, resultados: Dict):
        """
        Imprime resultados de validação.

        Args:
            resultados: Resultados da validação
        """
        print("\n" + "=" * 70)
        print("RESULTADOS DA VALIDAÇÃO")
        print("=" * 70)

        if resultados["total_erros"] == 0 and resultados["total_avisos"] == 0:
            print("\n✓ Documento validado com sucesso! Nenhum erro ou aviso.")
            return

        if resultados["erros"]:
            print(f"\n❌ ERROS ({resultados['total_erros']}):\n")
            for i, erro in enumerate(resultados["erros"], 1):
                print(f"{i}. [{erro['tipo'].upper()}] {erro['mensagem']}")
                if "linha" in erro:
                    print(f"   Linha: {erro['linha']}")

        if resultados["avisos"]:
            print(f"\n⚠️  AVISOS ({resultados['total_avisos']}):\n")
            for i, aviso in enumerate(resultados["avisos"], 1):
                print(f"{i}. [{aviso['tipo'].upper()}] {aviso['mensagem']}")
                if "linha" in aviso:
                    print(f"   Linha: {aviso['linha']}")

        print("\n" + "=" * 70)


def validar_arquivo(caminho: str) -> int:
    """
    Valida arquivo de documento.

    Args:
        caminho: Caminho do arquivo

    Returns:
        0 se sucesso, 1 se erro
    """
    arquivo = Path(caminho)

    if not arquivo.exists():
        print(f"Erro: Arquivo não encontrado: {caminho}", file=sys.stderr)
        return 1

    try:
        texto = arquivo.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}", file=sys.stderr)
        return 1

    validador = ValidadorDocumento()
    sucesso, resultados = validador.validar_documento(texto)

    validador.imprimir_resultados(resultados)

    return 0 if sucesso else 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: validar_documento.py <arquivo>")
        print("\nExemplo:")
        print("  validar_documento.py oficio_123.txt")
        sys.exit(1)

    sys.exit(validar_arquivo(sys.argv[1]))
