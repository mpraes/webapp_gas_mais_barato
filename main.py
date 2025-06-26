#!/usr/bin/env python3
"""
Gas Mais Barato - Dashboard de Preços GLP
Aplicação principal para consulta de preços oficiais de GLP da ANP.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.app import create_app

def main():
    """Função principal para executar a aplicação Flask."""
    print("🚀 Iniciando Gas Mais Barato - Dashboard de Preços GLP")
    print("=" * 60)
    
    try:
        # Criar e executar a aplicação Flask
        app = create_app()
        
        print("✅ Aplicação Flask criada com sucesso!")
        print("🌐 Acesse: http://localhost:5000")
        print("📊 Dashboard de preços de GLP da ANP")
        print("=" * 60)
        
        # Executar em modo de desenvolvimento
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
        
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo de dados não encontrado")
        print(f"   Verifique se o arquivo CSV está em: data/ultimas-4-semanas-glp.csv")
        print(f"   Erro detalhado: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar a aplicação: {e}")
        print("   Verifique se todas as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
