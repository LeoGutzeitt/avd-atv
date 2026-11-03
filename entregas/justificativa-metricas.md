# Justificativa das Métricas — Dashboard 2

## Contexto e Público-Alvo
- **Público-alvo:** Apostadores Esportivos, Analistas de Desempenho e Traders de Futebol.
- **Objetivo do Dashboard 2:** Avaliar a prevalência do fator campo (*home advantage*), medir a ofensividade das ligas para mercados de Over/Under e analisar a calibragem de risco das odds da Bet365 frente aos desfechos reais.

---

## Métrica 1: Taxa de Vitória Mandante (%)
- **Variável:** `home_team_outcome` (derivada de `home_team_goal > away_team_goal`).
- **O que mede:** A proporção percentual de jogos em que o time da casa saiu vencedor.
- **Por que foi escolhida:** É a métrica fundamental do futebol para quantificar o "fator casa" (*home advantage*). Historicamente no futebol europeu essa taxa gira em torno de 45.8%.
- **Público-alvo:** Apostadores nos mercados de resultado final (1X2) e analistas táticos.
- **Qual decisão pode ser apoiada por essa métrica?** Decisão de entrada a favor do mandante ou em handicap, além de identificar ligas/temporadas com viés mandante anômalo.
- **O que comunica ao público-alvo:** A intensidade do domínio dos times jogando em seu estádio no recorte selecionado em relação à média histórica.

---

## Métrica 2: Média de Gols por Jogo
- **Variável:** `total_goals` (`home_team_goal + away_team_goal`).
- **O que mede:** O número médio de gols marcados por partida.
- **Por que foi escolhida:** Serve como indicador primário para mercados de apostas em gols (*Over/Under 2.5 gols*). No futebol europeu, a linha de referência usual é de 2.70 gols/jogo.
- **Público-alvo:** Apostadores em mercados de gols e analistas ofensivos.
- **Qual decisão pode ser apoiada por essa métrica?** Seleção de partidas para estratégias de Over 2.5 (quando a média supera 2.70) ou Under (quando a liga é truncada).
- **O que comunica ao público-alvo:** Se o campeonato ou temporada analisada tem perfil dinâmico/ofensivo ou defensivo e com poucos gols.

---

## Métrica 3: Odd Média Mandante (B365H)
- **Variável:** `B365H` (Cotação Bet365 para vitória do time mandante).
- **O que mede:** A média aritmética das odds oferecidas pela Bet365 para o time da casa.
- **Por que foi escolhida:** Representa o favoritismo médio precificado pelo mercado (a probabilidade implícita do mercado é $1/\text{Odd}$). Odds médias menores indicam ligas com favoritos muito dominantes.
- **Público-alvo:** Apostadores de valor (*value bettors*) e gestores de risco.
- **Qual decisão pode ser apoiada por essa métrica?** Avaliar se as cotações médias dos mandantes estão muito esmagadas (pouco retorno) ou se oferecem margem atrativa de risco/retorno.
- **O que comunica ao público-alvo:** O patamar médio de precificação e exigência de retorno exigido pelas casas de apostas.

---

## Métrica 4: Ocorrência de "Zebras" (%)
- **Variável:** Partidas onde `away_team_goal > home_team_goal` e `B365A >= 3.50`.
- **O que mede:** A porcentagem de jogos em que o time visitante venceu a partida mesmo com cotação alta ($\ge 3.50$, probabilidade implícita $\le 28.5\%$).
- **Por que foi escolhida:** Mede a frequência empírica de resultados improváveis, essencial para calibrar a tolerância ao risco e estratégias contra o favorito.
- **Público-alvo:** Apostadores de alto risco/alto retorno e analistas de volatilidade.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir quando adotar estratégias de proteção (dupla hipótese) ou explorar valor em azarões em ligas de alta imprevisibilidade.
- **O que comunica ao público-alvo:** O nível real de imprevisibilidade esportiva na base analisada.
