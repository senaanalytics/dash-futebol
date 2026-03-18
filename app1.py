import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS CUSTOMIZADO
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fundo geral */
    .stApp { background-color: #0e1117; }

    /* Cards de métricas */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1f2e, #252a3a);
        border: 1px solid #2e3547;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label {
        color: #8b9ab8 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e8ecf5 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 13px !important;
    }

    /* Header do título */
    .dashboard-header {
        background: linear-gradient(135deg, #1a3a5c, #0d2137);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        border: 1px solid #1e4976;
        box-shadow: 0 8px 32px rgba(0, 100, 200, 0.2);
    }
    .dashboard-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        color: #7fb3d3;
        margin: 6px 0 0 0;
        font-size: 1rem;
    }

    /* Seção de título */
    .section-title {
        color: #c8d8f0;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #1e4976;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #131720;
        border-right: 1px solid #1e2535;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        color: #8b9ab8 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1f2e;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8b9ab8;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e4976 !important;
        color: #ffffff !important;
    }

    /* Tabelas */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    thead tr th { background-color: #1a2744 !important; color: #c8d8f0 !important; }

    /* Divider */
    hr { border-color: #1e2535; }
</style>
""", unsafe_allow_html=True)

# Tema dos gráficos Plotly
PLOT_TEMPLATE = "plotly_dark"
COLORS_MAIN  = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899"]
COLOR_WIN    = "#10b981"
COLOR_DRAW   = "#f59e0b"
COLOR_LOSS   = "#ef4444"


# ─────────────────────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    IDS = {
        "games":       "1ng4DUeu_uN-AG-kYXjoBkpRVtQFKvp8q",
        "leagues":     "1IHzSWWjEaDfPxY1TRi1n-kamHsoxcIQ7",
        "teams":       "1bB2I7RBEhj0dHBVXV2ss91VDyS-TX4E0",
        "teamstats":   "1YL65tiEwXs0QNCwGabDN4Wz2VRsoLHDB",
        "players":     "1UbiSPcM27s6wxfGOob0FpndTqK-KKoVN",
        "shots":       "1iwZvYv0KyHNkQfv0pRt0qQoLHVkjACjN",
        "appearances": "1RSOA6UaQR-Pb8B20sQKvG1VUgd--i7bm",
    }

    def gdrive_url(file_id):
        return f"https://drive.google.com/uc?export=download&confirm=t&id={file_id}"

    games       = pd.read_csv(gdrive_url(IDS["games"]),       encoding="latin1")
    leagues     = pd.read_csv(gdrive_url(IDS["leagues"]),     encoding="latin1")
    teams       = pd.read_csv(gdrive_url(IDS["teams"]),       encoding="latin1")
    teamstats   = pd.read_csv(gdrive_url(IDS["teamstats"]),   encoding="latin1")
    players     = pd.read_csv(gdrive_url(IDS["players"]),     encoding="latin1")
    shots       = pd.read_csv(gdrive_url(IDS["shots"]),       encoding="latin1")
    appearances = pd.read_csv(gdrive_url(IDS["appearances"]), encoding="latin1")

    games["date"]     = pd.to_datetime(games["date"])
    teamstats["date"] = pd.to_datetime(teamstats["date"])

    # Enriquecer teamstats com nomes de times
    teamstats = teamstats.merge(teams[["teamID","name"]], on="teamID", how="left")

    # Enriquecer games com ligas e nomes dos times
    games = games.merge(leagues, on="leagueID", how="left")
    games = games.merge(teams.rename(columns={"teamID":"homeTeamID","name":"homeTeam"}), on="homeTeamID", how="left")
    games = games.merge(teams.rename(columns={"teamID":"awayTeamID","name":"awayTeam"}), on="awayTeamID", how="left")

    # Resultado do jogo
    games["result"] = games.apply(
        lambda r: "Home Win" if r.homeGoals > r.awayGoals
                  else ("Away Win" if r.homeGoals < r.awayGoals else "Draw"),
        axis=1
    )
    games["totalGoals"] = games["homeGoals"] + games["awayGoals"]

    return games, leagues, teams, teamstats, players, shots, appearances

games, leagues, teams, teamstats, players, shots, appearances = load_data()


# ─────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Filtros")
    st.markdown("---")

    ligas_disponiveis = sorted(leagues["name"].tolist())
    liga_sel = st.selectbox("🏆 Liga", ["Todas"] + ligas_disponiveis)

    temporadas = sorted(games["season"].unique().tolist())
    temp_sel = st.multiselect("📅 Temporada(s)", temporadas, default=temporadas)

    st.markdown("---")
    if liga_sel != "Todas":
        league_id = leagues.loc[leagues["name"] == liga_sel, "leagueID"].values[0]
        times_liga = games[(games["leagueID"] == league_id) & (games["season"].isin(temp_sel))]
        home_teams = times_liga["homeTeam"].dropna().unique().tolist()
        away_teams = times_liga["awayTeam"].dropna().unique().tolist()
        times_disponiveis = sorted(set(home_teams + away_teams))
    else:
        times_disponiveis = sorted(teams["name"].tolist())

    time_sel = st.selectbox("🔵 Time para análise individual", ["Selecione..."] + times_disponiveis)
    st.markdown("---")
    st.markdown("<small style='color:#4a5568'>Dados: Kaggle Football Dataset<br>Temporadas 2014–2020</small>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FILTRAR DADOS
# ─────────────────────────────────────────────────────────────
df_games = games[games["season"].isin(temp_sel)].copy()
df_stats = teamstats[teamstats["season"].isin(temp_sel)].copy()

if liga_sel != "Todas":
    league_id = leagues.loc[leagues["name"] == liga_sel, "leagueID"].values[0]
    df_games = df_games[df_games["leagueID"] == league_id]
    game_ids = df_games["gameID"].unique()
    df_stats = df_stats[df_stats["gameID"].isin(game_ids)]


# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
liga_label = liga_sel if liga_sel != "Todas" else "Todas as Ligas"
temp_label = ", ".join(map(str, sorted(temp_sel))) if temp_sel else "—"

st.markdown(f"""
<div class="dashboard-header">
    <h1>⚽ Football Analytics Dashboard</h1>
    <p>🏆 {liga_label} &nbsp;|&nbsp; 📅 Temporadas: {temp_label} &nbsp;|&nbsp; {len(df_games):,} jogos analisados</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# KPIs GERAIS
# ─────────────────────────────────────────────────────────────
total_jogos   = len(df_games)
total_gols    = int(df_games["totalGoals"].sum())
media_gols    = df_games["totalGoals"].mean()
home_wins     = (df_games["result"] == "Home Win").sum()
away_wins     = (df_games["result"] == "Away Win").sum()
empates       = (df_games["result"] == "Draw").sum()
pct_home      = home_wins / total_jogos * 100 if total_jogos else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("🎮 Total de Jogos",   f"{total_jogos:,}")
c2.metric("⚽ Total de Gols",    f"{total_gols:,}")
c3.metric("📊 Média Gols/Jogo",  f"{media_gols:.2f}")
c4.metric("🏠 Vitórias Casa",    f"{home_wins:,}", f"{pct_home:.1f}%")
c5.metric("✈️ Vitórias Fora",    f"{away_wins:,}", f"{away_wins/total_jogos*100:.1f}%" if total_jogos else "0%")
c6.metric("🤝 Empates",          f"{empates:,}",   f"{empates/total_jogos*100:.1f}%" if total_jogos else "0%")

st.markdown("---")


# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Geral",
    "🏆 Ranking de Times",
    "📈 Análise por Time",
    "🔮 xGoals & Métricas Avançadas",
])


# ══════════════════════════════════════════════════════════════
# TAB 1 — VISÃO GERAL
# ══════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns(2)

    # Distribuição de resultados (pizza)
    with col1:
        st.markdown('<p class="section-title">Distribuição de Resultados</p>', unsafe_allow_html=True)
        res_count = df_games["result"].value_counts().reset_index()
        res_count.columns = ["Resultado", "Qtd"]
        fig_pizza = px.pie(
            res_count, names="Resultado", values="Qtd",
            color="Resultado",
            color_discrete_map={"Home Win": COLOR_WIN, "Away Win": COLOR_LOSS, "Draw": COLOR_DRAW},
            hole=0.45, template=PLOT_TEMPLATE,
        )
        fig_pizza.update_traces(textposition="outside", textinfo="percent+label")
        fig_pizza.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=320)
        st.plotly_chart(fig_pizza, use_container_width=True)

    # Gols por temporada
    with col2:
        st.markdown('<p class="section-title">Gols por Temporada</p>', unsafe_allow_html=True)
        gols_temp = df_games.groupby("season").agg(
            total_gols=("totalGoals", "sum"),
            media_gols=("totalGoals", "mean"),
            jogos=("gameID", "count"),
        ).reset_index()
        fig_gols = go.Figure()
        fig_gols.add_bar(
            x=gols_temp["season"], y=gols_temp["total_gols"],
            name="Total de Gols", marker_color="#3b82f6", opacity=0.85,
        )
        fig_gols.add_scatter(
            x=gols_temp["season"], y=gols_temp["media_gols"],
            name="Média/Jogo", mode="lines+markers",
            marker=dict(size=8), line=dict(color="#f59e0b", width=2),
            yaxis="y2",
        )
        fig_gols.update_layout(
            template=PLOT_TEMPLATE, height=320,
            legend=dict(orientation="h", y=1.1),
            margin=dict(t=10, b=10, l=10, r=10),
            yaxis=dict(title="Total de Gols"),
            yaxis2=dict(title="Média/Jogo", overlaying="y", side="right"),
        )
        st.plotly_chart(fig_gols, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    # Distribuição de placar (heatmap)
    with col3:
        st.markdown('<p class="section-title">Distribuição de Placares</p>', unsafe_allow_html=True)
        df_placar = df_games[df_games["homeGoals"] <= 6][df_games["awayGoals"] <= 6]
        pivot = df_placar.groupby(["homeGoals", "awayGoals"]).size().reset_index(name="count")
        pivot_table = pivot.pivot(index="awayGoals", columns="homeGoals", values="count").fillna(0)
        fig_heat = px.imshow(
            pivot_table,
            labels=dict(x="Gols Casa", y="Gols Fora", color="Jogos"),
            color_continuous_scale="Blues", template=PLOT_TEMPLATE,
            text_auto=True,
        )
        fig_heat.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_heat, use_container_width=True)

    # Gols por liga (se todas as ligas)
    with col4:
        if liga_sel == "Todas":
            st.markdown('<p class="section-title">Gols por Liga</p>', unsafe_allow_html=True)
            gols_liga = df_games.groupby("name").agg(
                media=("totalGoals", "mean"),
                total=("totalGoals", "sum"),
            ).reset_index().sort_values("media", ascending=True)
            fig_liga = px.bar(
                gols_liga, x="media", y="name",
                orientation="h", color="media",
                color_continuous_scale="blues",
                labels={"media": "Média Gols/Jogo", "name": "Liga"},
                template=PLOT_TEMPLATE, text_auto=".2f",
            )
            fig_liga.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), coloraxis_showscale=False)
            st.plotly_chart(fig_liga, use_container_width=True)
        else:
            st.markdown('<p class="section-title">Evolução de Resultados por Temporada</p>', unsafe_allow_html=True)
            evo = df_games.groupby(["season", "result"]).size().reset_index(name="count")
            fig_evo = px.bar(
                evo, x="season", y="count", color="result",
                color_discrete_map={"Home Win": COLOR_WIN, "Away Win": COLOR_LOSS, "Draw": COLOR_DRAW},
                barmode="group", template=PLOT_TEMPLATE,
                labels={"season": "Temporada", "count": "Jogos", "result": "Resultado"},
            )
            fig_evo.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_evo, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — RANKING DE TIMES
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">Tabela de Classificação Geral</p>', unsafe_allow_html=True)

    # Construir tabela de classificação
    stats_agg = df_stats.groupby("teamID").agg(
        jogos=("gameID", "count"),
        vitorias=("result", lambda x: (x == "W").sum()),
        empates=("result",  lambda x: (x == "D").sum()),
        derrotas=("result", lambda x: (x == "L").sum()),
        gols_marcados=("goals",  "sum"),
        xG_total=("xGoals", "sum"),
        chutes=("shots",  "sum"),
        chutes_gol=("shotsOnTarget", "sum"),
        cartoes_amarelos=("yellowCards", "sum"),
        cartoes_vermelhos=("redCards",   "sum"),
    ).reset_index()

    # Gols sofridos (perspectiva do adversário)
    gols_sofridos = df_stats.merge(
        df_games[["gameID","homeGoals","awayGoals","homeTeamID","awayTeamID"]], on="gameID"
    )
    gols_sofridos["gols_sofridos"] = gols_sofridos.apply(
        lambda r: r["awayGoals"] if r["location"] == "h" else r["homeGoals"], axis=1
    )
    gs = gols_sofridos.groupby("teamID")["gols_sofridos"].sum().reset_index()
    stats_agg = stats_agg.merge(gs, on="teamID", how="left")

    stats_agg["pontos"]   = stats_agg["vitorias"] * 3 + stats_agg["empates"]
    stats_agg["saldo"]    = stats_agg["gols_marcados"] - stats_agg["gols_sofridos"]
    stats_agg["aprov"]    = (stats_agg["pontos"] / (stats_agg["jogos"] * 3) * 100).round(1)
    stats_agg["precisao"] = (stats_agg["chutes_gol"] / stats_agg["chutes"].replace(0, 1) * 100).round(1)
    stats_agg = stats_agg.merge(teams, on="teamID", how="left")
    stats_agg = stats_agg.sort_values("pontos", ascending=False).reset_index(drop=True)
    stats_agg.index += 1

    # Top 10 — gols marcados
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">🔴 Top 10 — Gols Marcados</p>', unsafe_allow_html=True)
        top_gols = stats_agg.nlargest(10, "gols_marcados")[["name","gols_marcados","jogos","pontos"]]
        fig_top = px.bar(
            top_gols.sort_values("gols_marcados"), x="gols_marcados", y="name",
            orientation="h", color="gols_marcados", color_continuous_scale="reds",
            labels={"gols_marcados":"Gols","name":"Time"}, template=PLOT_TEMPLATE, text_auto=True,
        )
        fig_top.update_layout(height=360, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">🏅 Top 10 — Pontos</p>', unsafe_allow_html=True)
        top_pts = stats_agg.head(10)[["name","pontos","vitorias","empates","derrotas","aprov"]]
        fig_pts = px.bar(
            top_pts.sort_values("pontos"), x="pontos", y="name",
            orientation="h", color="pontos", color_continuous_scale="greens",
            labels={"pontos":"Pontos","name":"Time"}, template=PLOT_TEMPLATE, text_auto=True,
        )
        fig_pts.update_layout(height=360, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig_pts, use_container_width=True)

    # Tabela completa
    st.markdown('<p class="section-title">📋 Classificação Completa</p>', unsafe_allow_html=True)
    tabela_display = stats_agg[[
        "name","pontos","jogos","vitorias","empates","derrotas",
        "gols_marcados","gols_sofridos","saldo","aprov","precisao"
    ]].rename(columns={
        "name":"Time","pontos":"Pts","jogos":"J","vitorias":"V",
        "empates":"E","derrotas":"D","gols_marcados":"GM",
        "gols_sofridos":"GS","saldo":"SG","aprov":"Aprov%","precisao":"Precisão%"
    })
    st.dataframe(tabela_display, use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════
# TAB 3 — ANÁLISE INDIVIDUAL DO TIME
# ══════════════════════════════════════════════════════════════
with tab3:
    if time_sel == "Selecione...":
        st.info("👈 Selecione um time na barra lateral para ver a análise individual.")
    else:
        team_rows = teams.loc[teams["name"] == time_sel, "teamID"]
        if team_rows.empty:
            st.warning(f"Time '{time_sel}' não encontrado na base de dados.")
        else:
            team_id = team_rows.values[0]
            # Filtra df_stats pelo teamID — não depende do merge de nomes
            ts_time = teamstats[
                (teamstats["teamID"] == team_id) &
                (teamstats["season"].isin(temp_sel))
            ].copy()

            # Aplica filtro de liga se necessário
            if liga_sel != "Todas":
                league_id_filter = leagues.loc[leagues["name"] == liga_sel, "leagueID"].values[0]
                game_ids_liga = games[games["leagueID"] == league_id_filter]["gameID"].unique()
                ts_time = ts_time[ts_time["gameID"].isin(game_ids_liga)]

        if team_rows.empty:
            pass
        elif ts_time.empty:
            st.warning(f"Sem dados para {time_sel} nos filtros selecionados.")
        else:
            jogos_t    = len(ts_time)
            vitorias_t = (ts_time["result"] == "W").sum()
            empates_t  = (ts_time["result"] == "D").sum()
            derrotas_t = (ts_time["result"] == "L").sum()
            pontos_t   = vitorias_t * 3 + empates_t
            gols_t     = ts_time["goals"].sum()
            xg_t       = ts_time["xGoals"].sum()

            st.markdown(f"### 🔵 {time_sel}")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("🎮 Jogos",    jogos_t)
            c2.metric("🏆 Pontos",   pontos_t)
            c3.metric("✅ Vitórias", vitorias_t)
            c4.metric("🤝 Empates",  empates_t)
            c5.metric("❌ Derrotas", derrotas_t)
            c6.metric("⚽ Gols",     int(gols_t))

            st.markdown("---")
            col1, col2 = st.columns(2)

            # Resultado por temporada
            with col1:
                st.markdown('<p class="section-title">Resultados por Temporada</p>', unsafe_allow_html=True)
                res_temp = ts_time.groupby(["season", "result"]).size().reset_index(name="count")
                fig_rt = px.bar(
                    res_temp, x="season", y="count", color="result",
                    color_discrete_map={"W": COLOR_WIN, "D": COLOR_DRAW, "L": COLOR_LOSS},
                    barmode="stack", template=PLOT_TEMPLATE,
                    labels={"season":"Temporada","count":"Jogos","result":"Resultado"},
                )
                fig_rt.update_layout(height=300, margin=dict(t=5,b=5,l=5,r=5))
                st.plotly_chart(fig_rt, use_container_width=True)

            # Gols marcados vs xGoals
            with col2:
                st.markdown('<p class="section-title">Gols Reais vs xGoals por Temporada</p>', unsafe_allow_html=True)
                gxg = ts_time.groupby("season").agg(
                    gols=("goals","sum"), xg=("xGoals","sum")
                ).reset_index()
                fig_gxg = go.Figure()
                fig_gxg.add_bar(x=gxg["season"], y=gxg["gols"], name="Gols Reais", marker_color=COLOR_WIN)
                fig_gxg.add_bar(x=gxg["season"], y=gxg["xg"],   name="xGoals",     marker_color="#3b82f6", opacity=0.7)
                fig_gxg.update_layout(
                    barmode="group", template=PLOT_TEMPLATE,
                    height=300, margin=dict(t=5,b=5,l=5,r=5),
                    legend=dict(orientation="h", y=1.1),
                )
                st.plotly_chart(fig_gxg, use_container_width=True)

            col3, col4 = st.columns(2)

            # Radar de performance
            with col3:
                st.markdown('<p class="section-title">Radar de Performance (Médias)</p>', unsafe_allow_html=True)
                medias_time = ts_time[["goals","xGoals","shots","shotsOnTarget","corners","fouls"]].mean()
                medias_geral = df_stats[["goals","xGoals","shots","shotsOnTarget","corners","fouls"]].mean()
                categorias = ["Gols","xGoals","Chutes","Chutes a Gol","Escanteios","Faltas"]
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=medias_time.values, theta=categorias,
                    fill="toself", name=time_sel, line_color=COLOR_WIN,
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=medias_geral.values, theta=categorias,
                    fill="toself", name="Média Geral", line_color="#3b82f6", opacity=0.5,
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    template=PLOT_TEMPLATE, height=340,
                    margin=dict(t=20,b=20,l=20,r=20),
                    legend=dict(orientation="h", y=-0.1),
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            # Disciplina
            with col4:
                st.markdown('<p class="section-title">Disciplina por Temporada</p>', unsafe_allow_html=True)
                disc = ts_time.groupby("season").agg(
                    amarelos=("yellowCards","sum"), vermelhos=("redCards","sum"), faltas=("fouls","sum")
                ).reset_index()
                fig_disc = go.Figure()
                fig_disc.add_bar(x=disc["season"], y=disc["amarelos"], name="🟡 Amarelos", marker_color="#f59e0b")
                fig_disc.add_bar(x=disc["season"], y=disc["vermelhos"], name="🔴 Vermelhos", marker_color=COLOR_LOSS)
                fig_disc.update_layout(
                    barmode="group", template=PLOT_TEMPLATE,
                    height=340, margin=dict(t=5,b=5,l=5,r=5),
                    legend=dict(orientation="h", y=1.1),
                )
                st.plotly_chart(fig_disc, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 4 — xGOALS & MÉTRICAS AVANÇADAS
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">Expected Goals (xG) — O que são?</p>', unsafe_allow_html=True)
    st.info("📌 **xGoals (xG)** mede a qualidade das chances criadas. Um xG de 1.5 significa que o time criou chances equivalentes a 1.5 gols esperados. Times que marcam acima do xG são eficientes; abaixo, estão desperdiçando chances.")

    col1, col2 = st.columns(2)

    # Over/Under performers
    with col1:
        st.markdown('<p class="section-title">Top 10 — Gols acima do xG (Eficiência)</p>', unsafe_allow_html=True)
        xg_agg = df_stats.groupby("teamID").agg(
            gols=("goals","sum"), xg=("xGoals","sum")
        ).reset_index()
        xg_agg["diff_xg"] = xg_agg["gols"] - xg_agg["xg"]
        xg_agg = xg_agg.merge(teams, on="teamID", how="left")

        top_over = xg_agg.nlargest(10, "diff_xg")
        fig_over = px.bar(
            top_over.sort_values("diff_xg"), x="diff_xg", y="name",
            orientation="h", color="diff_xg", color_continuous_scale="greens",
            labels={"diff_xg":"Gols - xG","name":"Time"}, template=PLOT_TEMPLATE, text_auto=".1f",
        )
        fig_over.update_layout(height=340, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig_over, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Top 10 — Gols abaixo do xG (Desperdício)</p>', unsafe_allow_html=True)
        top_under = xg_agg.nsmallest(10, "diff_xg")
        fig_under = px.bar(
            top_under.sort_values("diff_xg", ascending=False), x="diff_xg", y="name",
            orientation="h", color="diff_xg", color_continuous_scale="reds_r",
            labels={"diff_xg":"Gols - xG","name":"Time"}, template=PLOT_TEMPLATE, text_auto=".1f",
        )
        fig_under.update_layout(height=340, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig_under, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    # Scatter gols x xg
    with col3:
        st.markdown('<p class="section-title">Gols Reais vs xGoals (por Time)</p>', unsafe_allow_html=True)
        xg_med = df_stats.groupby("teamID").agg(
            gols=("goals","sum"), xg=("xGoals","sum"), jogos=("gameID","count")
        ).reset_index().merge(teams, on="teamID", how="left")
        fig_scatter = px.scatter(
            xg_med, x="xg", y="gols", hover_name="name", size="jogos",
            color="diff_xg" if "diff_xg" in xg_med.columns else "jogos",
            color_continuous_scale="RdYlGn",
            labels={"xg":"xGoals Total","gols":"Gols Reais"},
            template=PLOT_TEMPLATE,
        )
        # Linha de referência (gols = xG)
        max_val = max(xg_med["xg"].max(), xg_med["gols"].max())
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode="lines", line=dict(dash="dash", color="#ffffff", width=1),
            name="Gols = xG", showlegend=True,
        ))
        fig_scatter.update_layout(height=380, margin=dict(t=5,b=5,l=5,r=5))
        st.plotly_chart(fig_scatter, use_container_width=True)

    # PPDA — Intensidade de pressão
    with col4:
        st.markdown('<p class="section-title">PPDA — Intensidade de Pressão (menor = mais pressão)</p>', unsafe_allow_html=True)
        st.caption("PPDA (Passes permitidos por ação defensiva) — Times com PPDA mais baixo pressionam mais alto.")
        ppda_agg = df_stats.groupby("teamID")["ppda"].mean().reset_index()
        ppda_agg = ppda_agg.merge(teams, on="teamID", how="left")
        ppda_top = ppda_agg.nsmallest(12, "ppda").sort_values("ppda")
        fig_ppda = px.bar(
            ppda_top, x="ppda", y="name",
            orientation="h", color="ppda", color_continuous_scale="blues_r",
            labels={"ppda":"PPDA Médio","name":"Time"}, template=PLOT_TEMPLATE, text_auto=".2f",
        )
        fig_ppda.update_layout(height=380, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig_ppda, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small style='color:#4a5568'>⚽ Football Analytics Dashboard &nbsp;|&nbsp; "
    "Dados: Kaggle &nbsp;|&nbsp; Temporadas 2014–2020 &nbsp;|&nbsp; "
    "5 Ligas Europeias</small></center>",
    unsafe_allow_html=True,
)
