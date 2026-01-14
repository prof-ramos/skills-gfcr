#!/bin/bash

# Configuração de erro e pipefail para segurança
set -euo pipefail

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Configurando GitHub Repository Manager ===${NC}"

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 não encontrado. Por favor, instale o Python 3.${NC}"
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Creating virtual environment (.venv)...${NC}"
    python3 -m venv .venv
fi

# Ativar ambiente virtual
# shellcheck source=/dev/null
source .venv/bin/activate

# Instalar/Atualizar pip
echo -e "${BLUE}Atualizando pip...${NC}"
python3 -m pip install --upgrade pip

# Instalar dependências
echo -e "${BLUE}Instalando dependências...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
else
    echo -e "${YELLOW}Aviso: requirements.txt não encontrado. Instalando requests padrão...${NC}"
    python3 -m pip install requests
fi

# Configurar TOKEN
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Configuração do GitHub Token${NC}"
    echo "Crie um token em: https://github.com/settings/tokens"
    echo "Permissões recomendadas: repo"
    echo -n "Digite seu GH_TOKEN: "
    read -rs token
    echo ""

    # Salvar com permissões restritas
    touch .env
    chmod 600 .env
    echo "GH_TOKEN=$token" > .env
    echo -e "${GREEN}✓ Token salvo em .env (permissão 600)${NC}"

    # Garantir que .env está no .gitignore
    if ! grep -q ".env" .gitignore 2>/dev/null; then
        echo ".env" >> .gitignore
        echo -e "${GREEN}✓ .env adicionado ao .gitignore${NC}"
    fi
else
    echo -e "${GREEN}✓ Arquivo .env já existe.${NC}"
fi

# Verificar token usando script Python temporário
echo -e "${BLUE}Validando token...${NC}"
python3 << END
import os
import requests
import sys

# Tentar carregar token do .env manualmente se python-dotenv não estiver disponível ainda
token = os.environ.get("GH_TOKEN")
if not token and os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if line.startswith("GH_TOKEN="):
                token = line.strip().split("=")[1]
                break

if not token:
    print("${RED}Erro: GH_TOKEN não encontrado.${NC}")
    sys.exit(1)

headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
try:
    r = requests.get("https://api.github.com/user", headers=headers, timeout=10)
    if r.status_code == 200:
        user = r.json().get("login")
        print(f"${GREEN}✓ Autenticado com sucesso como: {user}${NC}")
    else:
        print(f"${RED}Erro: Falha na autenticação (Status {r.status_code})${NC}")
        print(f"Detalhes: {r.text}")
        sys.exit(1)
except Exception as e:
    print(f"${RED}Erro na conexão: {e}${NC}")
    sys.exit(1)
END

echo -e "\n${GREEN}=== Instalação concluída com sucesso! ===${NC}"
echo -e "Para usar o CLI, ative o ambiente virtual:"
echo -e "  ${BLUE}source .venv/bin/activate${NC}"
echo -e "  ${BLUE}python gh_cli.py list${NC}"
