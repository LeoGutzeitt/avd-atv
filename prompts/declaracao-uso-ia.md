# Declaração de Uso de IA

**Nome:** Leonardo
**Data:** 29/10/2026 - 03/11/2026

## Ferramenta

Google Antigravity / Gemini 3.8 Flash (High)

## Prompt usado

1. "crie meu venv em uma pasta separada"
2. "https://colab.research.google.com/drive/1kFpoWY8vSnh2-8FZUdparPR9kiX7_O-x#scrollTo=SLtr9G2j0mWW preciso exportar esse dataset que preparei para o meu projeto, esse EDA, fazer o clean e o raw dele"
3. "o dataset nao deveria estar no raw?"
4. "Com base na sua EDA, crie uma aplicação no Streamlit com dois dashboards. Dashboard 1: um 'laboratório' de análise de distribuição e correlação. Dashboard 2: KPIs e métricas voltadas a um público alvo determinado individualmente. [...] faça o checklist e liste oq falta"

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito:**
  - Criação do ambiente virtual com Python 3.13 e configuração do interpretador no VS Code.
  - Script automatizado de download do Kaggle (`hugomathien/soccer`) salvando o SQLite original em `data/raw/database.sqlite`.
  - Processamento do EDA do Colab e exportação dos dados limpos para `data/clean/dataset.csv`.
  - Remoção de colunas textuais em XML não utilizadas na EDA (`goal`, `card`, etc.) que inflavam o CSV acima do limite de 100 MB do GitHub.
  - Estruturação do `app.py` em abas (`st.tabs`), com seletores dinâmicos, sliders de exclusão de intervalo, matriz de correlação interativa (Pearson/Spearman), histogramas e os 4 KPIs com 3 visuais no Dashboard 2.
  - Adição do decorador `@st.cache_data` em `src/data_loader.py` para otimizar tempo de carregamento da aplicação.

- **Modificado:**
  - Ajuste nas faixas dos sliders numéricos para arredondar valores e tratar inteiros/floats adequadamente sem quebrar a reatividade do Streamlit.
  - Inclusão de seleção interativa na legenda do gráfico de desfecho por categoria de ligas no Dashboard 2 usando Altair.

- **Rejeitado:**
  - Nenhuma sugestão estrutural foi rejeitada; todo o código foi mantido alinhado com o roteiro das Aulas 21 a 23 da disciplina.
