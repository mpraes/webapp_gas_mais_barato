"""
Configurações da aplicação Gas Mais Barato.
"""

import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Configurações do Flask
class Config:
    """Configuração base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Configurações de dados
    DATA_DIR = BASE_DIR / "data"
    CSV_FILE_PATH = DATA_DIR / "ultimas-4-semanas-glp.csv"
    
    # Configurações de processamento
    DEFAULT_DAYS_BACK = 30
    MAX_RESULTS_LIMIT = 1000
    
    # Configurações da aplicação
    APP_NAME = "Gas Mais Barato"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Dashboard de Preços GLP da ANP"


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True
    SECRET_KEY = 'dev-secret-key'


class ProductionConfig(Config):
    """Configuração para produção."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False


class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 