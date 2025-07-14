#!/usr/bin/env python3
"""
Script de teste para verificar o processamento de dados do GLP.
"""

import sys
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.data_processor import process_glp_data, GLPDatabaseProcessor

def test_data_processor():
    """Testa o processador de dados."""
    print("🧪 Testando processador de dados...")
    print("=" * 50)
    
    # Caminho para o arquivo CSV
    csv_path = Path("data/ultimas-4-semanas-glp.csv")
    
    if not csv_path.exists():
        print(f"❌ Arquivo CSV não encontrado: {csv_path}")
        return False
    
    try:
        # Processar dados
        print("📊 Processando dados...")
        processor = process_glp_data(str(csv_path), days_back=30)
        
        # Obter estatísticas
        print("\n📈 Estatísticas dos dados:")
        stats = processor.get_summary_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Testar filtros
        print("\n🔍 Testando filtros...")
        
        # Lista de cidades
        cities = processor.get_cities_list()
        print(f"   Total de cidades: {len(cities)}")
        print(f"   Primeiras 5 cidades: {cities[:5]}")
        
        # Lista de estados
        states = processor.get_states_list()
        print(f"   Total de estados: {len(states)}")
        print(f"   Estados: {states}")
        
        # Testar filtro por cidade
        if cities:
            test_city = cities[0]
            print(f"\n🏙️  Testando filtro por cidade: {test_city}")
            city_data = processor.filter_by_city(test_city)
            print(f"   Registros encontrados: {len(city_data)}")
            if len(city_data) > 0:
                print(f"   Primeiro registro: {city_data.iloc[0]['Revenda']} - R$ {city_data.iloc[0]['Valor de Venda']}")
        
        # Testar filtro por estado
        if states:
            test_state = states[0]
            print(f"\n🏛️  Testando filtro por estado: {test_state}")
            state_data = processor.filter_by_state(test_state)
            print(f"   Registros encontrados: {len(state_data)}")
            if len(state_data) > 0:
                print(f"   Primeiro registro: {state_data.iloc[0]['Municipio']} - R$ {state_data.iloc[0]['Valor de Venda']}")
        
        print("\n✅ Todos os testes passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Testa os endpoints da API."""
    print("\n🌐 Testando endpoints da API...")
    print("=" * 50)
    
    try:
        # Importar app
        from src.app import create_app
        
        # Criar app de teste
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Testar endpoint principal
            response = client.get('/')
            print(f"   GET / - Status: {response.status_code}")
            
            # Testar endpoint de busca
            response = client.get('/api/search?limit=5')
            print(f"   GET /api/search - Status: {response.status_code}")
            
            # Testar endpoint de cidades
            response = client.get('/api/cities')
            print(f"   GET /api/cities - Status: {response.status_code}")
            
            # Testar endpoint de estados
            response = client.get('/api/states')
            print(f"   GET /api/states - Status: {response.status_code}")
            
            # Testar endpoint de estatísticas
            response = client.get('/api/stats')
            print(f"   GET /api/stats - Status: {response.status_code}")
            
            # Testar endpoint about
            response = client.get('/about')
            print(f"   GET /about - Status: {response.status_code}")
        
        print("✅ Testes da API concluídos!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos testes da API: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_files():
    """Testa se os arquivos de template existem."""
    print("\n📄 Testando arquivos de template...")
    print("=" * 50)
    
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/about.html',
        'templates/404.html',
        'templates/500.html',
        'templates/error.html'
    ]
    
    all_exist = True
    for template_file in template_files:
        if Path(template_file).exists():
            print(f"   ✅ {template_file}")
        else:
            print(f"   ❌ {template_file} - NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist

def test_static_files():
    """Testa se os arquivos estáticos existem."""
    print("\n🎨 Testando arquivos estáticos...")
    print("=" * 50)
    
    static_files = [
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    all_exist = True
    for static_file in static_files:
        if Path(static_file).exists():
            print(f"   ✅ {static_file}")
        else:
            print(f"   ❌ {static_file} - NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist

def main():
    """Função principal de teste."""
    print("🚀 Iniciando testes do Gas Mais Barato")
    print("=" * 60)
    
    # Testar arquivos de template
    template_test_passed = test_template_files()
    
    # Testar arquivos estáticos
    static_test_passed = test_static_files()
    
    # Testar processador de dados
    data_test_passed = test_data_processor()
    
    # Testar API
    api_test_passed = test_api_endpoints()
    
    # Resultado final
    print("\n" + "=" * 60)
    if all([template_test_passed, static_test_passed, data_test_passed, api_test_passed]):
        print("🎉 Todos os testes passaram! A aplicação está pronta para uso.")
        return 0
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 