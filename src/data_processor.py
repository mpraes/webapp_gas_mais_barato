"""
Módulo para processamento e filtragem dos dados de preços de GLP da ANP.
"""

import pandas as pd
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GLPDatabaseProcessor:
    """Classe para processar dados de preços de GLP da ANP."""
    
    def __init__(self, csv_file_path: str):
        """
        Inicializa o processador de dados.
        
        Args:
            csv_file_path (str): Caminho para o arquivo CSV com dados da ANP
        """
        self.csv_file_path = csv_file_path
        self.df = None
        self.processed_df = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Carrega os dados do arquivo CSV.
        
        Returns:
            pd.DataFrame: DataFrame com os dados carregados
        """
        try:
            logger.info(f"Carregando dados de: {self.csv_file_path}")
            self.df = pd.read_csv(self.csv_file_path, sep=';', encoding='utf-8')
            logger.info(f"Dados carregados com sucesso. Shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            raise
    
    def clean_data(self) -> pd.DataFrame:
        """
        Limpa e prepara os dados para análise.
        
        Returns:
            pd.DataFrame: DataFrame limpo
        """
        if self.df is None:
            self.load_data()
        
        logger.info("Iniciando limpeza dos dados...")
        
        # Converter coluna de data
        self.df['Data da Coleta'] = pd.to_datetime(self.df['Data da Coleta'], format='%d/%m/%Y', errors='coerce')
        
        # Converter coluna de preço para numérico
        self.df['Valor de Venda'] = pd.to_numeric(
            self.df['Valor de Venda'].str.replace(',', '.'), 
            errors='coerce'
        )
        
        # Remover linhas com dados inválidos
        initial_rows = len(self.df)
        self.df = self.df.dropna(subset=['Data da Coleta', 'Valor de Venda', 'Municipio'])
        
        # Filtrar apenas GLP 13kg
        self.df = self.df[self.df['Produto'] == 'GLP']
        
        # Remover duplicatas
        self.df = self.df.drop_duplicates()
        
        logger.info(f"Limpeza concluída. Linhas removidas: {initial_rows - len(self.df)}")
        return self.df
    
    def filter_by_date_range(self, days_back: int = 30) -> pd.DataFrame:
        """
        Filtra dados por período mais recente.
        
        Args:
            days_back (int): Número de dias para trás a partir da data mais recente
            
        Returns:
            pd.DataFrame: DataFrame filtrado por data
        """
        if self.df is None:
            self.clean_data()
        
        # Encontrar a data mais recente
        max_date = self.df['Data da Coleta'].max()
        min_date = max_date - timedelta(days=days_back)
        
        logger.info(f"Filtrando dados de {min_date.strftime('%d/%m/%Y')} até {max_date.strftime('%d/%m/%Y')}")
        
        # Filtrar por período
        self.processed_df = self.df[
            (self.df['Data da Coleta'] >= min_date) & 
            (self.df['Data da Coleta'] <= max_date)
        ].copy()
        
        logger.info(f"Filtro por data aplicado. Registros restantes: {len(self.processed_df)}")
        return self.processed_df
    
    def get_latest_prices_by_city(self) -> pd.DataFrame:
        """
        Obtém os preços mais recentes por cidade.
        
        Returns:
            pd.DataFrame: DataFrame com preços mais recentes por cidade
        """
        if self.processed_df is None:
            self.filter_by_date_range()
        
        # Agrupar por cidade e obter o registro mais recente
        latest_prices = self.processed_df.sort_values('Data da Coleta').groupby(
            ['Municipio', 'Estado - Sigla', 'Revenda']
        ).tail(1).reset_index(drop=True)
        
        logger.info(f"Preços mais recentes obtidos para {len(latest_prices)} registros")
        return latest_prices
    
    def get_cities_list(self) -> list:
        """
        Obtém lista de cidades disponíveis.
        
        Returns:
            list: Lista de cidades únicas
        """
        if self.processed_df is None:
            self.get_latest_prices_by_city()
        
        cities = self.processed_df['Municipio'].unique().tolist()
        cities.sort()
        return cities
    
    def get_states_list(self) -> list:
        """
        Obtém lista de estados disponíveis.
        
        Returns:
            list: Lista de estados únicos
        """
        if self.processed_df is None:
            self.get_latest_prices_by_city()
        
        states = self.processed_df['Estado - Sigla'].unique().tolist()
        states.sort()
        return states
    
    def filter_by_city(self, city: str) -> pd.DataFrame:
        """
        Filtra dados por cidade específica.
        
        Args:
            city (str): Nome da cidade
            
        Returns:
            pd.DataFrame: DataFrame filtrado por cidade
        """
        if self.processed_df is None:
            self.get_latest_prices_by_city()
        
        filtered_df = self.processed_df[
            self.processed_df['Municipio'].str.contains(city, case=False, na=False)
        ].copy()
        
        logger.info(f"Filtro por cidade '{city}' aplicado. Registros encontrados: {len(filtered_df)}")
        return filtered_df
    
    def filter_by_state(self, state: str) -> pd.DataFrame:
        """
        Filtra dados por estado específico.
        
        Args:
            state (str): Sigla do estado
            
        Returns:
            pd.DataFrame: DataFrame filtrado por estado
        """
        if self.processed_df is None:
            self.get_latest_prices_by_city()
        
        filtered_df = self.processed_df[
            self.processed_df['Estado - Sigla'] == state.upper()
        ].copy()
        
        logger.info(f"Filtro por estado '{state}' aplicado. Registros encontrados: {len(filtered_df)}")
        return filtered_df
    
    def get_weekly_kpi_history(self, weeks: int = 4):
        """
        Retorna a série histórica semanal dos principais KPIs para as últimas N semanas.
        Returns:
            dict: { 'dates': [...], 'avg_price': [...], 'total_cities': [...], 'total_companies': [...], 'total_states': [...] }
        """
        if self.processed_df is None:
            self.get_latest_prices_by_city()
        df = self.processed_df.copy()
        df['week'] = df['Data da Coleta'].dt.to_period('W').apply(lambda r: r.start_time)
        # Ordenar por semana
        week_groups = df.groupby('week')
        # Pegar as últimas N semanas
        last_weeks = sorted(df['week'].unique())[-weeks:]
        history = {
            'dates': [],
            'avg_price': [],
            'total_cities': [],
            'total_companies': [],
            'total_states': []
        }
        for week in last_weeks:
            week_df = week_groups.get_group(week)
            history['dates'].append(week.strftime('%d/%m'))
            history['avg_price'].append(week_df['Valor de Venda'].mean())
            history['total_cities'].append(week_df['Municipio'].nunique())
            history['total_companies'].append(week_df['Revenda'].nunique())
            history['total_states'].append(week_df['Estado - Sigla'].nunique())
        return history

    def get_kpi_variations(self, history):
        """
        Calcula a variação percentual e absoluta entre as duas últimas semanas para cada KPI.
        Args:
            history (dict): saída de get_weekly_kpi_history
        Returns:
            dict: { 'avg_price': { 'abs': x, 'pct': y }, ... }
        """
        variations = {}
        for kpi in ['avg_price', 'total_cities', 'total_companies', 'total_states']:
            values = history[kpi]
            if len(values) >= 2 and values[-2] and values[-1] is not None:
                abs_var = values[-1] - values[-2]
                pct_var = ((values[-1] - values[-2]) / values[-2]) * 100 if values[-2] != 0 else None
            else:
                abs_var = None
                pct_var = None
            variations[kpi] = {'abs': abs_var, 'pct': pct_var}
        return variations

    def get_summary_stats(self):
        """
        Obtém estatísticas resumidas dos dados, incluindo histórico e variações para KPIs.
        Returns:
            dict: Dicionário com estatísticas e séries históricas
        """
        if self.processed_df is None:
            self.get_latest_prices_by_city()
        if self.processed_df.empty:
            return {
                'total_records': 0,
                'min_price': None,
                'max_price': None,
                'latest_date': None,
                'oldest_date': None,
                'kpis': {
                    'avg_price': {'current': None, 'history': [], 'variation': None},
                    'total_cities': {'current': None, 'history': [], 'variation': None},
                    'total_companies': {'current': None, 'history': [], 'variation': None},
                    'total_states': {'current': None, 'history': [], 'variation': None},
                    'dates': []
                }
            }
        latest_date = self.processed_df['Data da Coleta'].max()
        oldest_date = self.processed_df['Data da Coleta'].min()
        stats = {
            'total_records': len(self.processed_df),
            'min_price': self.processed_df['Valor de Venda'].min(),
            'max_price': self.processed_df['Valor de Venda'].max(),
            'latest_date': latest_date.strftime('%d/%m/%Y') if pd.notnull(latest_date) else None,
            'oldest_date': oldest_date.strftime('%d/%m/%Y') if pd.notnull(oldest_date) else None,
        }
        # Histórico semanal
        history = self.get_weekly_kpi_history(weeks=4)
        variations = self.get_kpi_variations(history)
        # Valor atual de cada KPI é o último da série
        stats['kpis'] = {
            'avg_price': {
                'current': history['avg_price'][-1] if history['avg_price'] else None,
                'history': history['avg_price'],
                'variation': variations['avg_price']
            },
            'total_cities': {
                'current': history['total_cities'][-1] if history['total_cities'] else None,
                'history': history['total_cities'],
                'variation': variations['total_cities']
            },
            'total_companies': {
                'current': history['total_companies'][-1] if history['total_companies'] else None,
                'history': history['total_companies'],
                'variation': variations['total_companies']
            },
            'total_states': {
                'current': history['total_states'][-1] if history['total_states'] else None,
                'history': history['total_states'],
                'variation': variations['total_states']
            },
            'dates': history['dates']
        }
        return stats


def process_glp_data(csv_file_path: str, days_back: int = 30) -> GLPDatabaseProcessor:
    """
    Função conveniente para processar dados de GLP.
    
    Args:
        csv_file_path (str): Caminho para o arquivo CSV
        days_back (int): Número de dias para trás
        
    Returns:
        GLPDatabaseProcessor: Processador com dados carregados e processados
    """
    processor = GLPDatabaseProcessor(csv_file_path)
    processor.load_data()
    processor.clean_data()
    processor.filter_by_date_range(days_back)
    processor.get_latest_prices_by_city()
    
    return processor


if __name__ == "__main__":
    # Teste do processador
    csv_path = "../data/ultimas-4-semanas-glp.csv"
    processor = process_glp_data(csv_path, days_back=30)
    
    print("=== Estatísticas dos Dados ===")
    stats = processor.get_summary_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print(f"\n=== Cidades Disponíveis ({len(processor.get_cities_list())}) ===")
    cities = processor.get_cities_list()
    print(f"Primeiras 10 cidades: {cities[:10]}")
    
    print(f"\n=== Estados Disponíveis ({len(processor.get_states_list())}) ===")
    states = processor.get_states_list()
    print(f"Estados: {states}") 