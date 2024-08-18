import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Set page title
st.set_page_config(page_title='Estadisticas Wallace FC')
st.title('Estadisticas Wallace FC')
st.write('Este tablero permite visualizar las estadisticas del equipo de futbol Wallace FC desde la temporada 2024.')

# Load data
matches = pd.read_excel('Stats Wallace.xlsx', sheet_name='Matches')
players = pd.read_excel('Stats Wallace.xlsx', sheet_name='Players')
tournaments = pd.read_excel('Stats Wallace.xlsx', sheet_name='Tournaments')
stats = pd.read_excel('Stats Wallace.xlsx', sheet_name='Stats')

stats_matches = pd.merge(stats, matches, left_on='Partido ID', right_on='Match ID', how='left')
matches_stats = pd.merge(matches, stats, left_on='Match ID', right_on='Partido ID', how='left')

# Tournament Selection
tournament = st.selectbox('Selecciona un torneo:', ['Todos'] + list(matches['Torneo'].unique()))
if tournament != 'Todos':
    matches = matches[matches['Torneo'] == tournament]
    stats_matches = stats_matches[stats_matches['Torneo'] == tournament]

# Create Tabs
general_tab, players_tab, rankings_tab, todo_tab = st.tabs(['⚽ General', '🥅 Jugadores', '🎯 Rankings', 'Other/Test'])
matches['Resultado'] = np.where(matches['GF'] > matches['GC'], 'W', np.where(matches['GF'] == matches['GC'], 'D', 'L'))


with todo_tab:
    # Matches without received goals
    no_received_goals = matches[matches['GC'] == 0]['Match ID'].count()
    st.metric('Clean Sheets', no_received_goals)
    # Highest win streak
    win_streak = 0
    current_streak = 0
    for result in matches['Resultado']:
        if result == 'W':
            current_streak += 1
            if current_streak > win_streak:
                win_streak = current_streak
        else:
            current_streak = 0
    st.metric('Win Streak', win_streak)

with general_tab:
    top1, top2 = st.columns(2)
    with top1:
        #Top Scorer
        top_scorer = stats_matches.groupby('Jugador')['Goles'].sum().sort_values(ascending=False).reset_index().head(1)
        st.metric(top_scorer['Jugador'].values[0],str(top_scorer['Goles'].values[0]) + ' goles', delta_color="normal")
        best_location = matches[matches['Resultado'] == 'W'].groupby('Ubicacion')['Match ID'].count().sort_values(ascending=False).reset_index().head(1)
        st.metric('Mejor Estadio',best_location['Ubicacion'].values[0],str(best_location['Match ID'].values[0]) + ' wins', delta_color="normal")
    with top2:
        #Top Assister
        top_assister = stats_matches.groupby('Jugador')['Asistencias'].sum().sort_values(ascending=False).reset_index().head(1)
        st.metric(top_assister['Jugador'].values[0],str(top_assister['Asistencias'].values[0]) + ' asistencias', delta_color="normal")
        worst_location = matches[matches['Resultado'] == 'L'].groupby('Ubicacion')['Match ID'].count().sort_values(ascending=False).reset_index().head(1)
        st.metric('Peor Estadio',worst_location['Ubicacion'].values[0],str(worst_location['Match ID'].values[0]) + ' losses', delta_color="inverse")
    # General Stats
    total_goals = matches['GF'].sum()
    total_assists = stats_matches['Asistencias'].sum()
    received_goals = matches['GC'].sum()
    total_matches = matches['Match ID'].count()
    goals_per_match = round(total_goals/total_matches,2)
    assists_per_match = round(total_assists/total_matches,2)
    received_goals_per_match = round(received_goals/total_matches, 2)

    won_matches = matches[matches['GF'] > matches['GC']]['Match ID'].count()
    tied_matches = matches[matches['GF'] == matches['GC']]['Match ID'].count()
    lost_matches = matches[matches['GF'] < matches['GC']]['Match ID'].count()
    win_rate = round(won_matches/total_matches,3)*100
    
    # Display general stats
    st.write('Partidos Totales:', total_matches)    
    # Pie Chart of won, tied and lost matches
    fig = px.pie(names=['Ganados', 'Empatados', 'Perdidos'], values=[won_matches, tied_matches, lost_matches],
                template='plotly_dark', title='Distribucion de Partidos')
    fig.update_layout(title_x=0.3)
    st.plotly_chart(fig)
    
    # Create columns for Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric('Goles Totales', total_goals)
        st.metric('Goles por partido', goals_per_match)
    with col2:
        st.metric('Asistencias Totales', total_assists)
        st.metric('Asistencias por partido', assists_per_match)
    with col3:
        st.metric('Goles Recibidos', received_goals)
        st.metric('Goles Recibidos por partido', received_goals_per_match)

    # Goal trend by month-year
    matches_monthly = matches.copy()
    matches_monthly['Fecha'] = pd.to_datetime(matches['Fecha'])
    matches_monthly['Mes'] = matches['Fecha'].dt.to_period('M')
    goals_by_month = matches_monthly.groupby('Mes')['GF'].sum().reset_index()
    matches_by_month = matches_monthly.groupby('Mes')['Match ID'].count().reset_index()
    # Combine matches by month and goals by month in a plot
    goals_by_month['Mes'] = goals_by_month['Mes'].astype(str)
    matches_by_month['Mes'] = matches_by_month['Mes'].astype(str)

    fig = px.line(goals_by_month, x='Mes', y='GF', title='Tendencia de Goles por Mes', template='plotly_dark')
    fig.add_scatter(x=goals_by_month['Mes'], y=goals_by_month['GF'], name='Goles', mode='markers')
    fig.add_bar(x=matches_by_month['Mes'], y=matches_by_month['Match ID'], name='Partidos', opacity=0.5, text=matches_by_month['Match ID'], textposition='outside')

    fig.update_layout(title_x=0.3)
    fig.update_xaxes(title='Mes')
    fig.update_yaxes(title='Goles')
    st.plotly_chart(fig)
    
with players_tab:
    # Player Selection
    player = st.selectbox('Selecciona un jugador:', list(players['Nombre'].unique()))
    if player:
        stats_matches_alt = stats_matches[stats_matches['Jugador'] == player]
    
    # Create columns for player stats
    col1, col2, col3 = st.columns(3)
    
    # Player Stats
    postion = players[players['Nombre'] == player]['Posicion'].values[0]
    active = players[players['Nombre'] == player]['Activo'].values[0]
    played_matches = players[players['Nombre'] == player]['PJ'].values[0]
    total_goals = stats_matches_alt['Goles'].sum()
    total_assists = stats_matches_alt['Asistencias'].sum()
    total_yellow = stats_matches_alt['Amarillas'].sum()
    total_red = stats_matches_alt['Rojas'].sum()
    
    with col1:
        st.metric('Posicion', postion)
        if active == 'Si':
            today = pd.Timestamp.today().strftime('%d-%m-%Y')
            st.metric('Activo', active, delta=today)
        else:
            fecha_fin = players[players['Nombre'] == player]['Fecha Fin'].values[0]
            fecha_fin = pd.to_datetime(fecha_fin)
            fecha_fin = fecha_fin.strftime('%d-%m-%Y')
            st.metric('Activo', active, delta=fecha_fin, delta_color="inverse")
    with col2:
        st.metric('Goles', total_goals)
        st.metric('Asistencias', total_assists)
    with col3:
        st.metric('Tarjetas Amarillas', total_yellow)
        st.metric('Tarjetas Rojas', total_red)
    
    # Player Trend per match
    st.write('---')
    st.subheader(f'Tendencia de {player} por Partido')
    # Select player stat
    player_stat = st.radio('Selecciona una estadistica:', ['Goles', 'Asistencias', 'Amarillas', 'Rojas'], horizontal=True)    
    # Trend per match
    player_trend = stats_matches_alt.groupby('Partido ID')[player_stat].sum().reset_index()
    # player_trend['Fecha'] = player_trend['Fecha'].dt.strftime('%d-%m-%Y')
    # Merge player trend to matches
    matches_ptrend = pd.merge(matches, player_trend, left_on='Match ID', right_on='Partido ID', how='left')
    # Fill NaN values with 0
    matches_ptrend[player_stat] = matches_ptrend[player_stat].fillna(0)
    # Create a line plot for trend per match
    fig = px.line(matches_ptrend, x='Fecha', y=player_stat, title=f'Tendencia de {player_stat} por Partido', template='plotly_dark',
                  custom_data=['Oponente', 'Torneo'])
    # Add Oponente and Torneo to hover
    fig.update_traces(hovertemplate='Fecha: %{x} <br>Oponente: %{customdata[0]} <br>Torneo: %{customdata[1]} <br>' + player_stat + ': %{y}')
    fig.update_layout(title_x=0.3)
    fig.update_xaxes(title='Fecha')
    fig.update_yaxes(title=player_stat)
    st.plotly_chart(fig)
    
    st.write('---')
    st.subheader(f'Asistencia Total de {player}')
    # Player assistance to matches
    played_matches = players[players['Nombre'] == player]['PJ'].values[0]
    total_player_matches = players[players['Nombre'] == player]['PT'].values[0]
    assistance_rate = round(played_matches/total_player_matches, 2)*100
    # Display player assistance rate
    assist1, assist2, assist3 = st.columns(3)
    with assist1:
        st.metric('Partidos Jugados', played_matches)
    with assist2:
        st.metric('Partidos Totales', total_player_matches)
    with assist3:
        st.metric('Tasa de Asistencia', str(assistance_rate) + '%')
    

with rankings_tab:
    rank1, rank2 = st.columns(2)
    with rank1:
        # Top of people who scored at least 1 goal
        st.write('Goleadores')
        top_scorers = stats_matches.groupby('Jugador')['Goles'].sum().sort_values(ascending=False).reset_index()
        top_scorers = top_scorers[top_scorers['Goles'] > 0]
        st.dataframe(top_scorers,hide_index=True, use_container_width=True, height=380)
        
        # Top of people who had at least 1 yellow card
        st.write('Tarjetas Amarillas')
        top_yellow = stats_matches.groupby('Jugador')['Amarillas'].sum().sort_values(ascending=False).reset_index()
        top_yellow = top_yellow[top_yellow['Amarillas'] > 0]
        st.dataframe(top_yellow,hide_index=True, use_container_width=True)
    with rank2:
        # Top of people who assisted at least 1 goal
        st.write('Asistidores')
        top_assisters = stats_matches.groupby('Jugador')['Asistencias'].sum().sort_values(ascending=False).reset_index()
        top_assisters = top_assisters[top_assisters['Asistencias'] > 0]
        st.dataframe(top_assisters,hide_index=True, use_container_width=True, height=380)
        
        # Top of people who had at least 1 red card
        st.write('Tarjetas Rojas')
        top_red = stats_matches.groupby('Jugador')['Rojas'].sum().sort_values(ascending=False).reset_index()
        top_red = top_red[top_red['Rojas'] > 0]
        st.dataframe(top_red,hide_index=True, use_container_width=True)
    
    
    
    
