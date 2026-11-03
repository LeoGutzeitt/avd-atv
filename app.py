import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="European Soccer Analytics & Betting Insights",
    page_icon="⚽",
    layout="wide",
)

# Carregamento com cache
df = load_data()

# Dicionário de rótulos amigáveis para as variáveis quantitativas
VAR_LABELS = {
    "home_team_goal": "Gols do Mandante",
    "away_team_goal": "Gols do Visitante",
    "total_goals": "Total de Gols na Partida",
    "B365H": "Odd Mandante (Bet365)",
    "B365D": "Odd Empate (Bet365)",
    "B365A": "Odd Visitante (Bet365)",
    "B365H_log": "Log(1 + Odd Mandante)",
}

VARS_QUANT = list(VAR_LABELS.keys())
VARS_PADRAO = ["home_team_goal", "away_team_goal", "B365H", "B365A"]

todas_temporadas = sorted(df["season"].dropna().unique().tolist())
todos_grupos_ligas = sorted(df["league_bin"].dropna().unique().tolist())

# ==============================================================================
# DEFINIÇÃO DA PALETA DE CORES (VERDE = MANDANTE, VERMELHO = VISITANTE)
# ==============================================================================
COR_VERDE_MANDANTE = "#16a34a"   # Verde esmeralda vibrante (Vitória Mandante)
COR_VERMELHO_VISITANTE = "#dc2626" # Vermelho intenso (Vitória Visitante)
COR_CINZA_EMPATE = "#64748b"     # Cinza ardósia neutro (Empate)

CORES_RESULTADO_3 = alt.Scale(
    domain=["Vitória Mandante", "Empate", "Vitória Visitante"],
    range=[COR_VERDE_MANDANTE, COR_CINZA_EMPATE, COR_VERMELHO_VISITANTE],
)

CORES_RESULTADO_BIN = alt.Scale(
    domain=["Home Win", "Other Outcome"],
    range=[COR_VERDE_MANDANTE, COR_VERMELHO_VISITANTE],
)

# ==============================================================================
# GERENCIAMENTO DE ESTADO DOS FILTROS (APLICAR E REMOVER DE FORMA AGRADÁVEL)
# ==============================================================================
if "filtro_versao" not in st.session_state:
    st.session_state["filtro_versao"] = 0

def resetar_filtros():
    st.session_state["filtro_versao"] += 1
    st.rerun()

# ==============================================================================
# SIDEBAR: INTERFACE AGRADÁVEL DE FILTROS
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Painel de Filtros")
    st.caption("Filtre temporadas, grupos de ligas e ajuste faixas das variáveis.")

    # Botão de restauração rápida
    if st.button("🔄 Restaurar Todos os Filtros", use_container_width=True, help="Restaura todos os filtros para os valores padrão"):
        resetar_filtros()

    st.markdown("---")

    # 1. Seleção de Variáveis Quantitativas
    st.markdown("**1. Variáveis Quantitativas**")
    variaveis_selecionadas = st.multiselect(
        "Selecione as variáveis para análise:",
        options=VARS_QUANT,
        default=VARS_PADRAO,
        format_func=lambda x: VAR_LABELS.get(x, x),
        key=f"vars_{st.session_state['filtro_versao']}",
        help="Escolha quais variáveis quantitativas alimentarão a correlação e distribuição no Dashboard 1.",
    )

    # 2. Filtros Categóricos Gerais
    st.markdown("**2. Recorte de Campeonatos**")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        marcar_todas_temp = st.checkbox("Todas Temporadas", value=True, key=f"chk_temp_{st.session_state['filtro_versao']}")
    with col_btn2:
        marcar_todas_ligas = st.checkbox("Todas as Ligas", value=True, key=f"chk_ligas_{st.session_state['filtro_versao']}")

    temporadas_selecionadas = st.multiselect(
        "Temporadas:",
        options=todas_temporadas,
        default=todas_temporadas if marcar_todas_temp else todas_temporadas[:3],
        key=f"temp_{st.session_state['filtro_versao']}",
    )

    ligas_selecionadas = st.multiselect(
        "Grupos de Ligas:",
        options=todos_grupos_ligas,
        default=todos_grupos_ligas if marcar_todas_ligas else todos_grupos_ligas[:1],
        key=f"ligas_{st.session_state['filtro_versao']}",
    )

    st.markdown("---")

    # 3. Opções de Cores e Destaques
    st.markdown("**3. Cores dos Gráficos**")
    modo_cor = st.radio(
        "Distinguir distribuição por:",
        options=["Resultado Completo (3 desfechos)", "Mandante vs Outros (Binário)", "Sem separação (Monocromático)"],
        index=0,
        key=f"modo_cor_{st.session_state['filtro_versao']}",
        help="Verde = Vitória Mandante | Vermelho = Vitória Visitante | Cinza = Empate",
    )

    st.markdown(
        """
        <div style="background-color: #f1f5f9; padding: 10px; border-radius: 8px; border-left: 4px solid #16a34a; margin-top: 5px;">
            <span style="color:#16a34a; font-weight:bold;">🟢 Vitória Mandante</span><br>
            <span style="color:#dc2626; font-weight:bold;">🔴 Vitória Visitante</span><br>
            <span style="color:#64748b; font-weight:bold;">⚪ Empate</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 4. Sliders de Intervalo com Expander agradável
    with st.expander("🔍 Sliders de Intervalo (Excluir Outliers)", expanded=True):
        st.caption("Ajuste as réguas para limitar faixas ou excluir valores extremos.")
        intervalos = {}
        for var in variaveis_selecionadas:
            serie = df[var].dropna()
            if not serie.empty:
                min_val = float(serie.min())
                max_val = float(serie.max())
                is_int = pd.api.types.is_integer_dtype(df[var]) or (df[var] % 1 == 0).all()
                passo = 1 if is_int else 0.1

                intervalos[var] = st.slider(
                    f"{VAR_LABELS.get(var, var)}",
                    min_value=int(min_val) if is_int else round(min_val, 2),
                    max_value=int(max_val) if is_int else round(max_val, 2),
                    value=(int(min_val) if is_int else round(min_val, 2), int(max_val) if is_int else round(max_val, 2)),
                    step=passo,
                    key=f"slider_{var}_{st.session_state['filtro_versao']}",
                )

# ==============================================================================
# FILTRAGEM DO DATAFRAME
# ==============================================================================
df_filtrado = df.copy()

if temporadas_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["season"].isin(temporadas_selecionadas)]

if ligas_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["league_bin"].isin(ligas_selecionadas)]

for var, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[(df_filtrado[var] >= inicio) & (df_filtrado[var] <= fim)]

# ==============================================================================
# CABEÇALHO PRINCIPAL
# ==============================================================================
st.title("⚽ Análise Estatística de Futebol Europeu & Mercados de Apostas")

# Barra de status dos filtros ativos
col_stat1, col_stat2 = st.columns([3, 1])
with col_stat1:
    st.markdown(
        f"Exibindo **{len(df_filtrado):,}** de **{len(df):,}** partidas avaliadas "
        f"({(len(df_filtrado)/len(df)*100):.1f}% da base total). "
        f"Filtros ativos: **{len(temporadas_selecionadas)}** temporadas, **{len(ligas_selecionadas)}** grupos de ligas."
    )
with col_stat2:
    if len(df_filtrado) < len(df):
        st.info("⚡ Dados filtrados ativos")

# ==============================================================================
# NAVEGAÇÃO POR ABAS
# ==============================================================================
tab1, tab2 = st.tabs([
    "📊 Dashboard 1: Laboratório de Distribuição e Correlação",
    "🎯 Dashboard 2: KPIs & Estratégia de Apostas",
])

# ==============================================================================
# DASHBOARD 1: DISTRIBUIÇÃO E CORRELAÇÃO
# ==============================================================================
with tab1:
    st.subheader("Laboratório Exploratório: Relação entre Gols e Precificação de Odds")
    st.markdown(
        "Analise a relação entre o volume de gols e a precificação das odds pela Bet365. "
        "As partidas estão mapeadas com cores temáticas: **Verde para Vitórias do Mandante** e "
        "**Vermelho para Vitórias do Visitante**."
    )

    if df_filtrado.empty:
        st.warning("⚠️ Nenhuma partida encontrada para a combinação de filtros selecionada. Amplie os intervalos ou restaure os filtros no painel lateral.")
    elif not variaveis_selecionadas:
        st.warning("⚠️ Selecione pelo menos uma variável quantitativa no painel lateral para visualizar os gráficos.")
    else:
        col_corr, col_dist = st.columns([1, 1.3], gap="large")

        # --- COLUNA DA ESQUERDA: HEATMAP DE CORRELAÇÃO ---
        with col_corr:
            st.markdown("#### Matriz de Correlação")
            col_m1, col_m2 = st.columns([1.2, 1])
            with col_m1:
                metodo_corr = st.radio(
                    "Método estatístico:",
                    options=["pearson", "spearman"],
                    format_func=lambda x: "Pearson (Linear)" if x == "pearson" else "Spearman (Não-Linear)",
                    horizontal=True,
                    help="Pearson analisa correlação linear clássica; Spearman é robusto a assimetrias e outliers.",
                )
            with col_m2:
                paleta_escolhida = st.selectbox(
                    "Paleta de Cores:",
                    options=["Vermelho ↔ Branco ↔ Azul", "Laranja ↔ Branco ↔ Roxo", "Vermelho ↔ Amarelo ↔ Verde"],
                    index=0,
                    help="Escolha o esquema de contraste divergente para a matriz.",
                )

            # Mapeamento da paleta divergente centrada em 0
            if paleta_escolhida == "Vermelho ↔ Branco ↔ Azul":
                cores_divergentes = ["#dc2626", "#ffffff", "#1d4ed8"] # Vermelho (-) / Branco (0) / Azul (+)
            elif paleta_escolhida == "Laranja ↔ Branco ↔ Roxo":
                cores_divergentes = ["#ea580c", "#ffffff", "#7c3aed"] # Laranja (-) / Branco (0) / Roxo (+)
            else:
                cores_divergentes = ["#dc2626", "#fef08a", "#16a34a"] # Vermelho (-) / Amarelo (0) / Verde (+)

            if len(variaveis_selecionadas) < 2:
                st.info("ℹ️ Selecione ao menos 2 variáveis quantitativas para calcular a matriz de correlação.")
            else:
                df_sub = df_filtrado[variaveis_selecionadas].dropna()
                if len(df_sub) < 3:
                    st.warning("Dados insuficientes para correlação com os filtros atuais.")
                else:
                    corr_df = df_sub.corr(method=metodo_corr).reset_index()
                    corr_melted = corr_df.melt(id_vars="index")
                    corr_melted.columns = ["Variável 1", "Variável 2", "Correlação"]
                    corr_melted["Rótulo 1"] = corr_melted["Variável 1"].map(lambda x: VAR_LABELS.get(x, x))
                    corr_melted["Rótulo 2"] = corr_melted["Variável 2"].map(lambda x: VAR_LABELS.get(x, x))
                    corr_melted["Texto"] = corr_melted["Correlação"].apply(lambda v: f"{v:.2f}")

                    # Heatmap no Altair com escala divergente de alto contraste
                    heatmap_base = alt.Chart(corr_melted).encode(
                        x=alt.X("Rótulo 1:O", title=None, axis=alt.Axis(labelAngle=-35)),
                        y=alt.Y("Rótulo 2:O", title=None),
                    )

                    heatmap_retangulos = heatmap_base.mark_rect(
                        stroke="#e2e8f0",
                        strokeWidth=2,
                    ).encode(
                        color=alt.Color(
                            "Correlação:Q",
                            scale=alt.Scale(domain=[-1, 0, 1], range=cores_divergentes),
                            legend=alt.Legend(
                                title="Correlação (r)",
                                gradientLength=200,
                                values=[-1, -0.5, 0, 0.5, 1],
                            ),
                        ),
                        tooltip=[
                            alt.Tooltip("Rótulo 1:O", title="Variável 1"),
                            alt.Tooltip("Rótulo 2:O", title="Variável 2"),
                            alt.Tooltip("Correlação:Q", format=".3f"),
                        ],
                    )

                    heatmap_textos = heatmap_base.mark_text(
                        baseline="middle",
                        fontSize=13,
                        fontWeight="bold",
                    ).encode(
                        text="Texto:N",
                        color=alt.condition(
                            "abs(datum.Correlação) >= 0.38",
                            alt.value("white"),
                            alt.value("#0f172a"),
                        ),
                    )

                    grafico_heatmap = (heatmap_retangulos + heatmap_textos).properties(
                        title=f"Matriz de Correlação ({metodo_corr.title()})",
                        height=390,
                    )

                    st.altair_chart(grafico_heatmap, width="stretch")

        # --- COLUNA DA DIREITA: HISTOGRAMAS DE DISTRIBUIÇÃO ---
        with col_dist:
            st.markdown("#### Distribuição das Variáveis")
            st.caption("Passe o cursor sobre as barras para inspecionar contagens exatas.")

            for var in variaveis_selecionadas:
                titulo_var = VAR_LABELS.get(var, var)
                chart_data = df_filtrado[[var, "match_result", "home_team_outcome"]].dropna()

                if chart_data.empty:
                    continue

                if modo_cor == "Resultado Completo (3 desfechos)":
                    hist_chart = (
                        alt.Chart(chart_data)
                        .mark_bar(opacity=0.8, binSpacing=1)
                        .encode(
                            x=alt.X(f"{var}:Q", bin=alt.Bin(maxbins=25), title=titulo_var),
                            y=alt.Y("count()", title="Partidas", stack=None),
                            color=alt.Color("match_result:N", scale=CORES_RESULTADO_3, title="Resultado"),
                            tooltip=[
                                alt.Tooltip(f"{var}:Q", bin=alt.Bin(maxbins=25), title="Faixa"),
                                alt.Tooltip("match_result:N", title="Resultado"),
                                alt.Tooltip("count()", title="Total"),
                            ],
                        )
                        .properties(height=210, title=f"Distribuição: {titulo_var}")
                    )
                elif modo_cor == "Mandante vs Outros (Binário)":
                    hist_chart = (
                        alt.Chart(chart_data)
                        .mark_bar(opacity=0.8, binSpacing=1)
                        .encode(
                            x=alt.X(f"{var}:Q", bin=alt.Bin(maxbins=25), title=titulo_var),
                            y=alt.Y("count()", title="Partidas", stack=None),
                            color=alt.Color("home_team_outcome:N", scale=CORES_RESULTADO_BIN, title="Resultado"),
                            tooltip=[
                                alt.Tooltip(f"{var}:Q", bin=alt.Bin(maxbins=25), title="Faixa"),
                                alt.Tooltip("home_team_outcome:N", title="Resultado"),
                                alt.Tooltip("count()", title="Total"),
                            ],
                        )
                        .properties(height=210, title=f"Distribuição: {titulo_var}")
                    )
                else:
                    hist_chart = (
                        alt.Chart(chart_data)
                        .mark_bar(color="#2563eb", binSpacing=1)
                        .encode(
                            x=alt.X(f"{var}:Q", bin=alt.Bin(maxbins=25), title=titulo_var),
                            y=alt.Y("count()", title="Partidas"),
                            tooltip=[
                                alt.Tooltip(f"{var}:Q", bin=alt.Bin(maxbins=25), title="Faixa"),
                                alt.Tooltip("count()", title="Total"),
                            ],
                        )
                        .properties(height=210, title=f"Distribuição: {titulo_var}")
                    )

                st.altair_chart(hist_chart, use_container_width=True)


# ==============================================================================
# DASHBOARD 2: KPIS & MÉTRICAS PARA APOSTADORES E ANALISTAS
# ==============================================================================
with tab2:
    st.subheader("Painel Estratégico de Apostas e Desempenho")
    
    st.info(
        "👥 **Público-Alvo:** Apostadores Esportivos, Traders e Analistas Táticos de Futebol.  \n"
        "🎯 **Convenção Visual:** **Verde (🟢)** indica sucesso/vantagem do Mandante | "
        "**Vermelho (🔴)** indica vitória/vantagem do Visitante."
    )

    if df_filtrado.empty:
        st.warning("⚠️ Nenhuma partida encontrada para os filtros selecionados.")
    else:
        # ----------------------------------------------------------------------
        # CÁLCULO DOS 4 KPIS PRINCIPAIS (st.metric)
        # ----------------------------------------------------------------------
        total_jogos = len(df_filtrado)
        vitorias_mandante = (df_filtrado["home_team_outcome"] == "Home Win").sum()
        taxa_mandante = (vitorias_mandante / total_jogos) * 100 if total_jogos > 0 else 0

        # Baseline histórico da base total: 45.8%
        delta_mandante = taxa_mandante - 45.8

        media_gols = df_filtrado["total_goals"].mean() if "total_goals" in df_filtrado else 0
        delta_gols = media_gols - 2.70 # baseline histórico de futebol europeu ~2.70 gols

        odd_media_mandante = df_filtrado["B365H"].dropna().mean()
        
        # Zebras: Vitória do Visitante quando a Odd do Visitante era >= 3.50
        partidas_com_odds = df_filtrado.dropna(subset=["B365A"])
        total_com_odds = len(partidas_com_odds)
        zebras = (
            (partidas_com_odds["away_team_goal"] > partidas_com_odds["home_team_goal"]) & 
            (partidas_com_odds["B365A"] >= 3.50)
        ).sum()
        taxa_zebra = (zebras / total_com_odds * 100) if total_com_odds > 0 else 0

        # Exibição das Métricas
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            label="🟢 Taxa de Vitória Mandante",
            value=f"{taxa_mandante:.1f}%",
            delta=f"{delta_mandante:+.1f}% vs média histórica",
            delta_color="normal",
            help="Frequência com que o time da casa vence a partida (fator campo).",
        )
        m2.metric(
            label="⚽ Média de Gols por Jogo",
            value=f"{media_gols:.2f}",
            delta=f"{delta_gols:+.2f} gols",
            help="Soma dos gols do mandante e visitante por confronto.",
        )
        m3.metric(
            label="📈 Odd Média Mandante (B365H)",
            value=f"{odd_media_mandante:.2f}" if not np.isnan(odd_media_mandante) else "N/D",
            help="Cotação média para vitória da casa; valores baixos indicam favoritismo acentuado.",
        )
        m4.metric(
            label="🔴 Ocorrência de 'Zebras' (Visitante)",
            value=f"{taxa_zebra:.1f}%",
            delta=f"{zebras:,} partidas",
            delta_color="inverse",
            help="Vitória do visitante com cotação alta (B365A >= 3.50).",
        )

        st.markdown("---")
        st.subheader("Visuais Estratégicos")

        # ----------------------------------------------------------------------
        # VISUAL 1 & VISUAL 2 EM COLUNAS
        # ----------------------------------------------------------------------
        vcol1, vcol2 = st.columns([1.2, 1], gap="medium")

        with vcol1:
            st.markdown("##### 1. Desfecho das Partidas por Categoria de Liga")
            st.caption("Proporção de Vitórias do Mandante (Verde), Empates (Cinza) e Vitórias do Visitante (Vermelho).")

            res_league = (
                df_filtrado.groupby(["league_bin", "match_result"])
                .size()
                .reset_index(name="Partidas")
            )

            # Reatividade por clique na legenda
            selecao_resultado = alt.selection_point(fields=["match_result"], bind="legend")

            grafico_barras_ligas = (
                alt.Chart(res_league)
                .mark_bar()
                .encode(
                    x=alt.X("league_bin:N", title="Grupo da Liga"),
                    y=alt.Y("Partidas:Q", stack="normalize", title="Proporção Relativa", axis=alt.Axis(format="%")),
                    color=alt.Color("match_result:N", scale=CORES_RESULTADO_3, title="Desfecho"),
                    opacity=alt.condition(selecao_resultado, alt.value(1.0), alt.value(0.3)),
                    tooltip=[
                        alt.Tooltip("league_bin:N", title="Grupo da Liga"),
                        alt.Tooltip("match_result:N", title="Desfecho"),
                        alt.Tooltip("Partidas:Q", format=","),
                    ],
                )
                .add_params(selecao_resultado)
                .properties(height=340)
            )

            st.altair_chart(grafico_barras_ligas, use_container_width=True)

        with vcol2:
            st.markdown("##### 2. Dispersão das Odds: Mandante x Visitante")
            st.caption("Verde = Mandante venceu | Vermelho = Visitante venceu. Arraste para selecionar.")

            df_scatter = df_filtrado.dropna(subset=["B365H", "B365A"]).sample(
                n=min(1800, len(df_filtrado.dropna(subset=["B365H", "B365A"]))),
                random_state=42
            )

            brush = alt.selection_interval()

            grafico_scatter = (
                alt.Chart(df_scatter)
                .mark_circle(size=45)
                .encode(
                    x=alt.X("B365H:Q", scale=alt.Scale(domain=[1, 15], clamp=True), title="Odd Mandante (B365H)"),
                    y=alt.Y("B365A:Q", scale=alt.Scale(domain=[1, 20], clamp=True), title="Odd Visitante (B365A)"),
                    color=alt.condition(
                        brush,
                        alt.Color("match_result:N", scale=CORES_RESULTADO_3, title="Resultado"),
                        alt.value("#cbd5e1"),
                    ),
                    tooltip=[
                        alt.Tooltip("season:N", title="Temporada"),
                        alt.Tooltip("home_team_goal:Q", title="Gols Casa"),
                        alt.Tooltip("away_team_goal:Q", title="Gols Fora"),
                        alt.Tooltip("B365H:Q", title="Odd Casa"),
                        alt.Tooltip("B365A:Q", title="Odd Fora"),
                        alt.Tooltip("match_result:N", title="Resultado"),
                    ],
                )
                .add_params(brush)
                .properties(height=340)
            )

            st.altair_chart(grafico_scatter, use_container_width=True)

        # ----------------------------------------------------------------------
        # VISUAL 3: EVOLUÇÃO TEMPORAL POR TEMPORADA
        # ----------------------------------------------------------------------
        st.markdown("##### 3. Evolução da Média de Gols (Casa vs Fora) por Temporada")
        st.caption("Verde = Média Gols Mandante | Vermelho = Média Gols Visitante ao longo dos anos.")

        gols_temporada = (
            df_filtrado.groupby("season")[["home_team_goal", "away_team_goal", "total_goals"]]
            .mean()
            .reset_index()
        )

        gols_melted = gols_temporada.melt(
            id_vars="season",
            value_vars=["home_team_goal", "away_team_goal"],
            var_name="Tipo de Gol",
            value_name="Média de Gols",
        )
        gols_melted["Tipo de Gol"] = gols_melted["Tipo de Gol"].map({
            "home_team_goal": "Média Gols Mandante",
            "away_team_goal": "Média Gols Visitante",
        })

        cores_linhas = alt.Scale(
            domain=["Média Gols Mandante", "Média Gols Visitante"],
            range=[COR_VERDE_MANDANTE, COR_VERMELHO_VISITANTE],
        )

        linha_evolucao = (
            alt.Chart(gols_melted)
            .mark_line(point=True, strokeWidth=2.5)
            .encode(
                x=alt.X("season:N", title="Temporada"),
                y=alt.Y("Média de Gols:Q", scale=alt.Scale(domain=[0.8, 2.0]), title="Média de Gols por Jogo"),
                color=alt.Color("Tipo de Gol:N", scale=cores_linhas, title="Tipo de Gol"),
                tooltip=["season:N", "Tipo de Gol:N", alt.Tooltip("Média de Gols:Q", format=".2f")],
            )
            .properties(height=260)
        )

        st.altair_chart(linha_evolucao, use_container_width=True)
