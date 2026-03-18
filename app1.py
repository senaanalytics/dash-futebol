import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="⚽ Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1f2e, #252a3a);
        border: 1px solid #2e3547; border-radius: 12px; padding: 16px;
    }
    [data-testid="metric-container"] label { color: #8b9ab8 !important; font-size: 12px !important; font-weight: 600 !important; text-transform: uppercase; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8ecf5 !important; font-size: 28px !important; font-weight: 700 !important; }
    .dashboard-header { background: linear-gradient(135deg, #1a3a5c, #0d2137); border-radius: 16px; padding: 24px 32px; margin-bottom: 24px; border: 1px solid #1e4976; }
    .dashboard-header h1 { color: #fff; font-size: 2.2rem; margin: 0; font-weight: 800; }
    .dashboard-header p  { color: #7fb3d3; margin: 6px 0 0 0; }
    .section-title { color: #c8d8f0; font-size: 1.1rem; font-weight: 700; margin: 24px 0 12px 0; padding-bottom: 8px; border-bottom: 2px solid #1e4976; text-transform: uppercase; }
    [data-testid="stSidebar"] { background-color: #131720; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1f2e; border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #8b9ab8; border-radius: 8px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #1e4976 !important; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

PT    = "plotly_dark"
C_WIN  = "#10b981"
C_DRAW = "#f59e0b"
C_LOSS = "#ef4444"

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
    def url(fid):
        return f"https://drive.google.com/uc?export=download&confirm=t&id={fid}"

    games       = pd.read_csv(url(IDS["games"]),       encoding="latin1")
    leagues     = pd.read_csv(url(IDS["leagues"]),     encoding="latin1")
    teams       = pd.read_csv(url(IDS["teams"]),       encoding="latin1")
    teamstats   = pd.read_csv(url(IDS["teamstats"]),   encoding="latin1")
    players     = pd.read_csv(url(IDS["players"]),     encoding="latin1")
    shots       = pd.read_csv(url(IDS["shots"]),       encoding="latin1")
    appearances = pd.read_csv(url(IDS["appearances"]), encoding="latin1")

    games["date"]     = pd.to_datetime(games["date"],     errors="coerce")
    teamstats["date"] = pd.to_datetime(teamstats["date"], errors="coerce")

    games = games.merge(leagues, on="leagueID", how="left")
    games = games.merge(teams.rename(columns={"teamID":"homeTeamID","name":"homeTeam"}), on="homeTeamID", how="left")
    games = games.merge(teams.rename(columns={"teamID":"awayTeamID","name":"awayTeam"}), on="awayTeamID", how="left")
    games["result"]     = games.apply(lambda r: "Home Win" if r.homeGoals > r.awayGoals else ("Away Win" if r.homeGoals < r.awayGoals else "Draw"), axis=1)
    games["totalGoals"] = games["homeGoals"] + games["awayGoals"]

    # Adiciona leagueID ao teamstats via games
    g_lean = games[["gameID","leagueID"]].drop_duplicates()
    teamstats = teamstats.merge(g_lean, on="gameID", how="left")

    return games, leagues, teams, teamstats, players, shots, appearances

games, leagues, teams, teamstats, players, shots, appearances = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Filtros")
    st.markdown("---")
    liga_sel  = st.selectbox("🏆 Liga", ["Todas"] + sorted(leagues["name"].tolist()))
    temporadas = sorted(games["season"].unique().tolist())
    temp_sel  = st.multiselect("📅 Temporada(s)", temporadas, default=temporadas)
    st.markdown("---")

    if liga_sel != "Todas":
        lid = leagues.loc[leagues["name"] == liga_sel, "leagueID"].values[0]
        gf  = games[(games["leagueID"] == lid) & (games["season"].isin(temp_sel))]
        times_lista = sorted(set(gf["homeTeam"].dropna().tolist() + gf["awayTeam"].dropna().tolist()))
    else:
        times_lista = sorted(teams["name"].dropna().tolist())

    time_sel = st.selectbox("🔵 Time para análise individual", ["Selecione..."] + times_lista)
    st.markdown("---")
    st.markdown("<small style='color:#4a5568'>Dados: Kaggle | 2014–2020</small>", unsafe_allow_html=True)

# ── FILTROS GLOBAIS ───────────────────────────────────────────
df_games = games[games["season"].isin(temp_sel)].copy()
df_stats = teamstats[teamstats["season"].isin(temp_sel)].copy()
if liga_sel != "Todas":
    lid      = leagues.loc[leagues["name"] == liga_sel, "leagueID"].values[0]
    df_games = df_games[df_games["leagueID"] == lid]
    df_stats = df_stats[df_stats["leagueID"] == lid]

# ── HEADER ────────────────────────────────────────────────────
liga_label = liga_sel if liga_sel != "Todas" else "Todas as Ligas"
temp_label = ", ".join(map(str, sorted(temp_sel))) if temp_sel else "—"
st.markdown(f"""
<div class="dashboard-header">
    <h1>⚽ Football Analytics Dashboard</h1>
    <p>🏆 {liga_label} &nbsp;|&nbsp; 📅 {temp_label} &nbsp;|&nbsp; {len(df_games):,} jogos</p>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
n = len(df_games)
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("🎮 Jogos",        f"{n:,}")
c2.metric("⚽ Gols",         f"{int(df_games['totalGoals'].sum()):,}")
c3.metric("📊 Média/Jogo",   f"{df_games['totalGoals'].mean():.2f}" if n else "0")
c4.metric("🏠 Casa",         f"{(df_games['result']=='Home Win').sum():,}")
c5.metric("✈️ Fora",         f"{(df_games['result']=='Away Win').sum():,}")
c6.metric("🤝 Empates",      f"{(df_games['result']=='Draw').sum():,}")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral","🏆 Ranking","📈 Análise por Time","🔮 xGoals & Avançado"])

# ══ TAB 1 ═════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Distribuição de Resultados</p>', unsafe_allow_html=True)
        rc = df_games["result"].value_counts().reset_index(); rc.columns = ["R","Q"]
        fig = px.pie(rc, names="R", values="Q", hole=0.45,
                     color="R", color_discrete_map={"Home Win":C_WIN,"Away Win":C_LOSS,"Draw":C_DRAW}, template=PT)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=320)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<p class="section-title">Gols por Temporada</p>', unsafe_allow_html=True)
        gt = df_games.groupby("season").agg(total=("totalGoals","sum"), media=("totalGoals","mean")).reset_index()
        fig = go.Figure()
        fig.add_bar(x=gt["season"], y=gt["total"], name="Total", marker_color="#3b82f6", opacity=0.85)
        fig.add_scatter(x=gt["season"], y=gt["media"], name="Média", mode="lines+markers",
                        marker=dict(size=8), line=dict(color="#f59e0b",width=2), yaxis="y2")
        fig.update_layout(template=PT, height=320, margin=dict(t=10,b=10,l=10,r=10),
                          legend=dict(orientation="h",y=1.1),
                          yaxis2=dict(overlaying="y",side="right",title="Média"))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">Heatmap de Placares</p>', unsafe_allow_html=True)
        dp = df_games[(df_games["homeGoals"]<=6)&(df_games["awayGoals"]<=6)]
        pv = dp.groupby(["homeGoals","awayGoals"]).size().reset_index(name="c")
        pt = pv.pivot(index="awayGoals", columns="homeGoals", values="c").fillna(0)
        fig = px.imshow(pt, labels=dict(x="Gols Casa",y="Gols Fora",color="Jogos"),
                        color_continuous_scale="Blues", template=PT, text_auto=True)
        fig.update_layout(height=320, margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        if liga_sel == "Todas":
            st.markdown('<p class="section-title">Média de Gols por Liga</p>', unsafe_allow_html=True)
            gl = df_games.groupby("name")["totalGoals"].mean().reset_index().sort_values("totalGoals")
            fig = px.bar(gl, x="totalGoals", y="name", orientation="h", color="totalGoals",
                         color_continuous_scale="blues", labels={"totalGoals":"Média","name":"Liga"},
                         template=PT, text_auto=".2f")
            fig.update_layout(height=320, margin=dict(t=10,b=10,l=10,r=10), coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p class="section-title">Resultados por Temporada</p>', unsafe_allow_html=True)
            evo = df_games.groupby(["season","result"]).size().reset_index(name="count")
            fig = px.bar(evo, x="season", y="count", color="result", barmode="group", template=PT,
                         color_discrete_map={"Home Win":C_WIN,"Away Win":C_LOSS,"Draw":C_DRAW})
            fig.update_layout(height=320, margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)

# ══ TAB 2 ═════════════════════════════════════════════════════
with tab2:
    agg = df_stats.groupby("teamID").agg(
        jogos=("gameID","count"),
        vitorias=("result",lambda x:(x=="W").sum()),
        empates=("result",lambda x:(x=="D").sum()),
        derrotas=("result",lambda x:(x=="L").sum()),
        gols=("goals","sum"), xg=("xGoals","sum"),
        chutes=("shots","sum"), chutes_gol=("shotsOnTarget","sum"),
    ).reset_index()
    home_gs = df_games[["gameID","homeTeamID","awayGoals"]].rename(columns={"homeTeamID":"teamID","awayGoals":"gs"})
    away_gs = df_games[["gameID","awayTeamID","homeGoals"]].rename(columns={"awayTeamID":"teamID","homeGoals":"gs"})
    gs_df   = pd.concat([home_gs,away_gs]).groupby("teamID")["gs"].sum().reset_index(name="gols_sofridos")
    agg = agg.merge(gs_df, on="teamID", how="left")
    agg["pontos"] = agg["vitorias"]*3 + agg["empates"]
    agg["saldo"]  = agg["gols"] - agg["gols_sofridos"]
    agg["aprov"]  = (agg["pontos"]/(agg["jogos"]*3)*100).round(1)
    agg = agg.merge(teams, on="teamID", how="left").sort_values("pontos", ascending=False).reset_index(drop=True)
    agg.index += 1

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">🔴 Top 10 Goleadores</p>', unsafe_allow_html=True)
        top = agg.nlargest(10,"gols").sort_values("gols")
        fig = px.bar(top, x="gols", y="name", orientation="h", color="gols",
                     color_continuous_scale="reds", labels={"gols":"Gols","name":"Time"}, template=PT, text_auto=True)
        fig.update_layout(height=360, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<p class="section-title">🏅 Top 10 por Pontos</p>', unsafe_allow_html=True)
        top = agg.head(10).sort_values("pontos")
        fig = px.bar(top, x="pontos", y="name", orientation="h", color="pontos",
                     color_continuous_scale="greens", labels={"pontos":"Pts","name":"Time"}, template=PT, text_auto=True)
        fig.update_layout(height=360, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">📋 Classificação Completa</p>', unsafe_allow_html=True)
    tabela = agg[["name","pontos","jogos","vitorias","empates","derrotas","gols","gols_sofridos","saldo","aprov"]].rename(columns={
        "name":"Time","pontos":"Pts","jogos":"J","vitorias":"V","empates":"E","derrotas":"D",
        "gols":"GM","gols_sofridos":"GS","saldo":"SG","aprov":"Aprov%"})
    st.dataframe(tabela, use_container_width=True, height=400)

# ══ TAB 3 ═════════════════════════════════════════════════════
with tab3:
    if time_sel == "Selecione...":
        st.info("👈 Selecione um time na barra lateral para ver a análise individual.")
    else:
        match = teams[teams["name"] == time_sel]
        if match.empty:
            st.error(f"Time '{time_sel}' não encontrado.")
        else:
            tid = int(match["teamID"].values[0])

            # ✅ Filtra diretamente pelo teamID numérico — sem depender de merge
            ts = teamstats[
                (teamstats["teamID"] == tid) &
                (teamstats["season"].isin(temp_sel))
            ].copy()

            # Aplica filtro de liga se necessário
            if liga_sel != "Todas":
                lid_filtro = leagues.loc[leagues["name"] == liga_sel, "leagueID"].values[0]
                gids = games[games["leagueID"] == lid_filtro]["gameID"].unique()
                ts = ts[ts["gameID"].isin(gids)]

            if ts.empty:
                st.warning(f"Sem dados para **{time_sel}** nos filtros selecionados.")
            else:
                v = (ts["result"]=="W").sum()
                e = (ts["result"]=="D").sum()
                d = (ts["result"]=="L").sum()
                st.markdown(f"### 🔵 {time_sel}")
                c1,c2,c3,c4,c5,c6 = st.columns(6)
                c1.metric("🎮 Jogos",    len(ts))
                c2.metric("🏆 Pontos",   int(v*3+e))
                c3.metric("✅ Vitórias", int(v))
                c4.metric("🤝 Empates",  int(e))
                c5.metric("❌ Derrotas", int(d))
                c6.metric("⚽ Gols",     int(ts["goals"].sum()))

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<p class="section-title">Resultados por Temporada</p>', unsafe_allow_html=True)
                    rt = ts.groupby(["season","result"]).size().reset_index(name="count")
                    fig = px.bar(rt, x="season", y="count", color="result", barmode="stack", template=PT,
                                 color_discrete_map={"W":C_WIN,"D":C_DRAW,"L":C_LOSS},
                                 labels={"season":"Temporada","count":"Jogos","result":"Resultado"})
                    fig.update_layout(height=300, margin=dict(t=5,b=5,l=5,r=5))
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.markdown('<p class="section-title">Gols Reais vs xGoals</p>', unsafe_allow_html=True)
                    gxg = ts.groupby("season").agg(gols=("goals","sum"),xg=("xGoals","sum")).reset_index()
                    fig = go.Figure()
                    fig.add_bar(x=gxg["season"], y=gxg["gols"], name="Gols Reais", marker_color=C_WIN)
                    fig.add_bar(x=gxg["season"], y=gxg["xg"],   name="xGoals",     marker_color="#3b82f6", opacity=0.7)
                    fig.update_layout(barmode="group", template=PT, height=300,
                                      margin=dict(t=5,b=5,l=5,r=5), legend=dict(orientation="h",y=1.1))
                    st.plotly_chart(fig, use_container_width=True)

                col3, col4 = st.columns(2)
                with col3:
                    st.markdown('<p class="section-title">Radar de Performance</p>', unsafe_allow_html=True)
                    cols_r  = ["goals","xGoals","shots","shotsOnTarget","corners","fouls"]
                    labs_r  = ["Gols","xGoals","Chutes","Chutes a Gol","Escanteios","Faltas"]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(r=ts[cols_r].mean().values,         theta=labs_r, fill="toself", name=time_sel,      line_color=C_WIN))
                    fig.add_trace(go.Scatterpolar(r=teamstats[cols_r].mean().values,  theta=labs_r, fill="toself", name="Média Geral", line_color="#3b82f6", opacity=0.5))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), template=PT,
                                      height=340, margin=dict(t=20,b=20,l=20,r=20), legend=dict(orientation="h",y=-0.1))
                    st.plotly_chart(fig, use_container_width=True)
                with col4:
                    st.markdown('<p class="section-title">Disciplina por Temporada</p>', unsafe_allow_html=True)
                    disc = ts.groupby("season").agg(amarelos=("yellowCards","sum"),vermelhos=("redCards","sum")).reset_index()
                    fig = go.Figure()
                    fig.add_bar(x=disc["season"], y=disc["amarelos"],  name="🟡 Amarelos",  marker_color="#f59e0b")
                    fig.add_bar(x=disc["season"], y=disc["vermelhos"], name="🔴 Vermelhos", marker_color=C_LOSS)
                    fig.update_layout(barmode="group", template=PT, height=340,
                                      margin=dict(t=5,b=5,l=5,r=5), legend=dict(orientation="h",y=1.1))
                    st.plotly_chart(fig, use_container_width=True)

# ══ TAB 4 ═════════════════════════════════════════════════════
with tab4:
    st.info("📌 **xGoals (xG)** — Times acima da linha diagonal marcam mais do que o esperado (eficientes). Abaixo, desperdiçam chances.")
    xg = df_stats.groupby("teamID").agg(gols=("goals","sum"),xg=("xGoals","sum")).reset_index()
    xg["diff"] = xg["gols"] - xg["xg"]
    xg = xg.merge(teams, on="teamID", how="left")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Top 10 Mais Eficientes</p>', unsafe_allow_html=True)
        fig = px.bar(xg.nlargest(10,"diff").sort_values("diff"), x="diff", y="name",
                     orientation="h", color="diff", color_continuous_scale="greens",
                     labels={"diff":"Gols - xG","name":"Time"}, template=PT, text_auto=".1f")
        fig.update_layout(height=340, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<p class="section-title">Top 10 Mais Desperdiçadores</p>', unsafe_allow_html=True)
        fig = px.bar(xg.nsmallest(10,"diff").sort_values("diff",ascending=False), x="diff", y="name",
                     orientation="h", color="diff", color_continuous_scale="reds_r",
                     labels={"diff":"Gols - xG","name":"Time"}, template=PT, text_auto=".1f")
        fig.update_layout(height=340, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">Gols Reais vs xGoals</p>', unsafe_allow_html=True)
        fig = px.scatter(xg, x="xg", y="gols", hover_name="name", color="diff",
                         color_continuous_scale="RdYlGn",
                         labels={"xg":"xGoals","gols":"Gols Reais"}, template=PT)
        mv = max(xg["xg"].max(), xg["gols"].max())
        fig.add_trace(go.Scatter(x=[0,mv],y=[0,mv],mode="lines",
                                 line=dict(dash="dash",color="#fff",width=1),name="Gols = xG"))
        fig.update_layout(height=360, margin=dict(t=5,b=5,l=5,r=5))
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st.markdown('<p class="section-title">PPDA — Intensidade de Pressão</p>', unsafe_allow_html=True)
        st.caption("Menor PPDA = maior pressão")
        ppda = df_stats.groupby("teamID")["ppda"].mean().reset_index()
        ppda = ppda.merge(teams, on="teamID", how="left").nsmallest(12,"ppda").sort_values("ppda")
        fig  = px.bar(ppda, x="ppda", y="name", orientation="h", color="ppda",
                      color_continuous_scale="blues_r", labels={"ppda":"PPDA","name":"Time"},
                      template=PT, text_auto=".2f")
        fig.update_layout(height=360, margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("<center><small style='color:#4a5568'>⚽ Football Analytics | Kaggle | 5 Ligas Europeias | 2014–2020</small></center>", unsafe_allow_html=True)
