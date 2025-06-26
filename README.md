# 🏠 Gas Mais Barato - Dashboard de Preços GLP

Um dashboard web simples desenvolvido em Flask que permite aos usuários consultar preços oficiais de GLP (Gás Liquefeito de Petróleo) de 13kg por cidade, utilizando dados da ANP (Agência Nacional do Petróleo, Gás Natural e Biocombustíveis).

## 📋 Descrição

Este projeto foi desenvolvido para facilitar a consulta de preços de GLP de 13kg em diferentes cidades brasileiras. O dashboard utiliza dados oficiais da ANP e oferece uma interface amigável para que os usuários possam encontrar o melhor preço do gás em sua região.

## ✨ Funcionalidades

- **Busca por Cidade**: Filtro por município para encontrar revendedores locais
- **Consulta de Preços**: Visualização dos preços oficiais de GLP 13kg
- **Informações das Empresas**: Dados das revendedoras incluindo CNPJ e endereço
- **Filtros Avançados**: Busca por estado, bandeira da empresa e período
- **Interface Responsiva**: Design adaptável para diferentes dispositivos
- **API REST**: Endpoints para integração com outros sistemas

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Framework CSS**: Bootstrap 5
- **Processamento de Dados**: Pandas
- **Dados**: CSV com informações oficiais da ANP

## 🏗️ Arquitetura do Projeto

```
webapp_gas_mais_barato/
├── src/                    # Código fonte principal
│   ├── __init__.py        # Pacote Python
│   ├── app.py             # Aplicação Flask principal
│   └── data_processor.py  # Processamento e filtros de dados
├── templates/             # Templates HTML
│   ├── base.html          # Template base
│   ├── index.html         # Página principal
│   ├── about.html         # Página sobre
│   ├── 404.html           # Página de erro 404
│   ├── 500.html           # Página de erro 500
│   └── error.html         # Página de erro genérica
├── static/                # Arquivos estáticos
│   ├── css/
│   │   └── style.css      # Estilos personalizados
│   └── js/
│       └── main.js        # JavaScript principal
├── data/                  # Dados da ANP
│   ├── ultimas-4-semanas-glp.csv
│   └── CAPACIDADE DE TANQUE.pdf
├── main.py                # Script principal de execução
├── config.py              # Configurações da aplicação
├── test_data_processor.py # Script de testes
├── pyproject.toml         # Configurações do projeto
├── uv.lock               # Lock file das dependências
└── README.md             # Este arquivo
```

## 📦 Instalação

### Pré-requisitos

- Python 3.13 ou superior
- Gerenciador de pacotes `uv` (recomendado) ou `pip`

### Passos para Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd webapp_gas_mais_barato
   ```

2. **Instale as dependências**
   ```bash
   # Usando uv (recomendado)
   uv sync
   
   # Ou usando pip
   pip install -r requirements.txt
   ```

3. **Execute os testes**
   ```bash
   python test_data_processor.py
   ```

4. **Execute a aplicação**
   ```bash
   python main.py
   ```

5. **Acesse o dashboard**
   Abra seu navegador e acesse: `http://localhost:5000`

## 🚀 Como Usar

1. **Acesse o Dashboard**: Abra a aplicação no seu navegador
2. **Selecione sua Cidade**: Use o filtro de busca para encontrar sua cidade natal
3. **Visualize os Preços**: Veja os preços de GLP 13kg das diferentes revendedoras
4. **Compare Opções**: Analise preços, bandeiras e localizações das empresas
5. **Filtros Adicionais**: Use filtros por estado, empresa ou período para refinar sua busca

## 🔧 Scripts Disponíveis

### Processamento de Dados (`src/data_processor.py`)

O módulo `data_processor.py` contém a classe `GLPDatabaseProcessor` que oferece:

- **Carregamento de dados**: Leitura do arquivo CSV da ANP
- **Limpeza de dados**: Tratamento de valores nulos e formatação
- **Filtros por data**: Seleção de período mais recente
- **Filtros por localização**: Busca por cidade e estado
- **Estatísticas**: Resumo dos dados processados

### Aplicação Flask (`src/app.py`)

A aplicação Flask oferece:

- **Página principal**: Dashboard com filtros e resultados
- **API REST**: Endpoints para busca de dados
- **Templates**: Interface responsiva com Bootstrap
- **Tratamento de erros**: Páginas de erro personalizadas

### Script de Testes (`test_data_processor.py`)

Execute para verificar se tudo está funcionando:

```bash
python test_data_processor.py
```

## 📊 Estrutura dos Dados

O dashboard utiliza dados da ANP contendo:
- **Informações Geográficas**: Região, Estado, Município
- **Dados das Revendedoras**: Nome, CNPJ, Endereço completo
- **Preços**: Valor de venda do GLP 13kg
- **Metadados**: Data da coleta, bandeira da empresa

## 🔧 Configuração

### Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
SECRET_KEY=sua-chave-secreta-aqui
```

### Configurações (`config.py`)

O arquivo `config.py` contém as configurações da aplicação:

- **Configurações do Flask**: Secret key, debug mode
- **Caminhos de dados**: Localização dos arquivos CSV
- **Parâmetros de processamento**: Dias para trás, limite de resultados
- **Configurações da aplicação**: Nome, versão, descrição

## 🌐 API Endpoints

A aplicação oferece os seguintes endpoints:

- `GET /` - Página principal do dashboard
- `GET /api/search` - Busca de preços com filtros
- `GET /api/cities` - Lista de cidades disponíveis
- `GET /api/states` - Lista de estados disponíveis
- `GET /api/stats` - Estatísticas dos dados
- `GET /about` - Página sobre o projeto

### Exemplo de uso da API:

```bash
# Buscar preços em uma cidade específica
curl "http://localhost:5000/api/search?city=São Paulo&limit=10"

# Obter estatísticas
curl "http://localhost:5000/api/stats"

# Listar cidades
curl "http://localhost:5000/api/cities"
```

## 📈 Funcionalidades Futuras

- [ ] Gráficos de evolução de preços
- [ ] Alertas de preço
- [ ] Comparação entre cidades
- [ ] API REST para integração
- [ ] Aplicativo mobile
- [ ] Histórico de preços
- [ ] Exportação de dados em diferentes formatos
- [ ] Dashboard administrativo

## 🧪 Testes

Para executar os testes:

```bash
# Testar processamento de dados
python test_data_processor.py

# Testar a aplicação Flask
python -m pytest tests/  # Se implementar pytest
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Estrutura para Contribuições

- **Novas funcionalidades**: Adicione em `src/`
- **Templates**: Crie em `templates/`
- **Estilos**: Modifique `static/css/`
- **JavaScript**: Atualize `static/js/`
- **Testes**: Adicione em `tests/`

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas, sugestões ou problemas:

- Abra uma [issue](https://github.com/seu-usuario/webapp_gas_mais_barato/issues)
- Entre em contato através do email: seu-email@exemplo.com

## 🙏 Agradecimentos

- **ANP** - Agência Nacional do Petróleo, Gás Natural e Biocombustíveis pelos dados oficiais
- **Comunidade Flask** - Pelo framework web utilizado
- **Bootstrap** - Pelo framework CSS responsivo
- **Contribuidores** - Todos que ajudaram no desenvolvimento

---

**Desenvolvido com ❤️ para ajudar os brasileiros a encontrar o melhor preço do GLP**
