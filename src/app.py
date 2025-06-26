"""
Aplicação Flask principal para o dashboard de preços de GLP.
"""

from flask import Flask, render_template, request, jsonify
import os
import logging
from pathlib import Path
import unidecode

from .data_processor import process_glp_data, GLPDatabaseProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis globais
DATA_PROCESSOR = None
CSV_FILE_PATH = None


def create_app():
    """Factory function para criar a aplicação Flask."""
    # Configurar caminhos
    project_root = Path(__file__).parent.parent
    template_dir = project_root / "templates"
    static_dir = project_root / "static"
    
    # Criar aplicação Flask com caminhos corretos
    app = Flask(__name__, 
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Inicializar processador de dados
    initialize_data_processor(project_root)
    
    # Registrar rotas
    register_routes(app)
    
    return app


def initialize_data_processor(project_root):
    """Inicializa o processador de dados."""
    global DATA_PROCESSOR, CSV_FILE_PATH
    
    # Caminho para o arquivo CSV
    CSV_FILE_PATH = project_root / "data" / "ultimas-4-semanas-glp.csv"
    
    if not CSV_FILE_PATH.exists():
        logger.error(f"Arquivo CSV não encontrado: {CSV_FILE_PATH}")
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {CSV_FILE_PATH}")
    
    try:
        logger.info("Inicializando processador de dados...")
        DATA_PROCESSOR = process_glp_data(str(CSV_FILE_PATH), days_back=30)
        logger.info("Processador de dados inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar processador de dados: {e}")
        raise


def register_routes(app):
    """Registra as rotas da aplicação."""
    
    @app.route('/')
    def index():
        """Página principal do dashboard."""
        try:
            # Obter estatísticas gerais
            stats = DATA_PROCESSOR.get_summary_stats()
            
            # Obter listas para filtros
            cities = DATA_PROCESSOR.get_cities_list()
            states = DATA_PROCESSOR.get_states_list()
            
            return render_template('index.html', 
                                 stats=stats, 
                                 cities=cities, 
                                 states=states)
        except Exception as e:
            logger.error(f"Erro na página principal: {e}")
            return render_template('error.html', error=str(e))

    @app.route('/api/search')
    def search_prices():
        """API para busca de preços com filtros."""
        try:
            city = request.args.get('city', '').strip()
            state = request.args.get('state', '').strip()
            limit = int(request.args.get('limit', 50))

            filtered_df = DATA_PROCESSOR.processed_df.copy()
            if state:
                filtered_df = filtered_df[filtered_df['Estado - Sigla'] == state.upper()]
            if city:
                city_norm = unidecode.unidecode(city).strip().lower()
                filtered_df = filtered_df[
                    filtered_df['Municipio'].apply(lambda x: unidecode.unidecode(str(x)).strip().lower() == city_norm)
                ]

            # Ordenar por data de coleta (mais recente primeiro)
            if 'Data da Coleta' in filtered_df.columns:
                filtered_df = filtered_df.sort_values('Data da Coleta', ascending=False)

            # Limitar resultados
            if len(filtered_df) > limit:
                filtered_df = filtered_df.head(limit)

            # Converter para formato JSON
            results = []
            for _, row in filtered_df.iterrows():
                results.append({
                    'municipio': row['Municipio'],
                    'estado': row['Estado - Sigla'],
                    'revenda': row['Revenda'],
                    'cnpj': row['CNPJ da Revenda'],
                    'endereco': f"{row['Nome da Rua']}, {row['Numero Rua']} - {row['Bairro']}",
                    'cep': row['Cep'],
                    'preco': float(row['Valor de Venda']),
                    'data_coleta': row['Data da Coleta'].strftime('%d/%m/%Y'),
                    'bandeira': row['Bandeira']
                })

            return jsonify({
                'success': True,
                'data': results,
                'total_results': len(results),
                'filters_applied': {
                    'city': city,
                    'state': state
                }
            })

        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/cities')
    def get_cities():
        """API para obter lista de cidades."""
        try:
            cities = DATA_PROCESSOR.get_cities_list()
            return jsonify({
                'success': True,
                'data': cities
            })
        except Exception as e:
            logger.error(f"Erro ao obter cidades: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/states')
    def get_states():
        """API para obter lista de estados."""
        try:
            states = DATA_PROCESSOR.get_states_list()
            return jsonify({
                'success': True,
                'data': states
            })
        except Exception as e:
            logger.error(f"Erro ao obter estados: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/stats')
    def get_stats():
        """API para obter estatísticas dos dados, com suporte a filtros contextuais."""
        try:
            city = request.args.get('city', '').strip()
            state = request.args.get('state', '').strip()
            df = DATA_PROCESSOR.processed_df.copy()
            if city:
                df = df[df['Municipio'].str.contains(city, case=False, na=False)]
            if state:
                df = df[df['Estado - Sigla'] == state.upper()]
            temp_processor = GLPDatabaseProcessor(DATA_PROCESSOR.csv_file_path)
            temp_processor.df = df.copy()
            temp_processor.processed_df = df.copy()
            stats = temp_processor.get_summary_stats()
            # KPIs contextuais
            if city:
                # KPIs para cidade
                kpis = {
                    'kpi_type': 'city',
                    'avg_price': stats['kpis']['avg_price'],
                    'variation': stats['kpis']['avg_price']['variation'],
                    'total_companies': stats['kpis']['total_companies'],
                    'min_price': df['Valor de Venda'].min() if not df.empty else None,
                    'max_price': df['Valor de Venda'].max() if not df.empty else None,
                }
            elif state:
                # KPIs para estado
                kpis = {
                    'kpi_type': 'state',
                    'avg_price': stats['kpis']['avg_price'],
                    'variation': stats['kpis']['avg_price']['variation'],
                    'total_cities': stats['kpis']['total_cities'],
                    'total_companies': stats['kpis']['total_companies'],
                }
            else:
                # KPIs globais
                kpis = {
                    'kpi_type': 'global',
                    'avg_price': stats['kpis']['avg_price'],
                    'variation': stats['kpis']['avg_price']['variation'],
                    'total_cities': stats['kpis']['total_cities'],
                    'total_companies': stats['kpis']['total_companies'],
                }
            kpis['dates'] = stats['kpis']['dates']
            return jsonify({
                'success': True,
                'data': kpis
            })
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/about')
    def about():
        """Página sobre o projeto."""
        return render_template('about.html')

    @app.errorhandler(404)
    def not_found(error):
        """Página 404 personalizada."""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Página 500 personalizada."""
        return render_template('500.html'), 500


if __name__ == '__main__':
    # Criar e executar a aplicação
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
