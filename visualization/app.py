import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Streamlit App", page_icon=":bar_chart:", layout="wide")

START_YEAR = 1950
END_YEAR = 2023


# Load data
@st.cache_data
def get_circuit_data():
    return pd.read_csv("data/processed/circuits.csv")


@st.cache_data
def get_driver_data():
    return pd.read_csv("data/processed/drivers.csv")


# Helper functions
def filter_year(data, year):
    return data[data["year"] == year]


def get_season_rankings(drivers):
    """
    Returns the driver standings for the season
    """
    return (
        drivers[drivers["round"] == drivers["round"].max()]
        .sort_values(by="points", ascending=False)
        .set_index("position")
    )


def get_circuit_rankings(drivers, circuits, selection):
    """
    Returns the driver standings for a specific circuit
    """
    rnd_num = circuits[circuits["name"] == selection]["round"].values[0]

    return (
        drivers[drivers["round"] == rnd_num]
        .sort_values(by="points", ascending=False)
        .set_index("position")
    )


# Display data
def show_winner_text(rankings):
    """
    Displays the winner of the season
    """
    winner = rankings.head(1)
    winner_name = f"{winner['forename'].values[0]} {winner['surname'].values[0]}"
    winner_number = f"[{winner['number'].values[0]}]"

    # Combine elements with HTML for styling (use with caution)
    winner_text = f"""
    <span style="font-size: 24px;;">Winner:</span>
    <span style="font-size: 40px; color: red;">{winner_name}</span>
    <span style="font-size: 40px; color: red;">{winner_number}</span>
    """

    st.markdown(winner_text, unsafe_allow_html=True)


def show_world_map(circuits):
    """
    Plots the Formula 1 Races in a choropleth map
    """

    fig = px.scatter_geo(
        circuits,
        lat="lat",
        lon="lng",
        hover_name="name",
        color="country",
        color_discrete_sequence=px.colors.qualitative.Set1,
        text="round",
    )

    fig.update_layout(
        margin={"r": 0, "t": 25, "l": 0, "b": 0},
        clickmode="event+select",
        showlegend=False,
    )
    fig.update_geos(
        showcountries=True,
        showland=True,
        showocean=True,
        countrycolor="darkgrey",
        landcolor="lightgreen",
        oceancolor="lightblue",
    )
    fig.update_traces(marker_size=12)

    st.plotly_chart(fig, use_container_width=True)


def show_races(circuits):
    """
    Plots the Races that year in order
    """
    circuits = circuits.sort_values(by="round")
    circuits = circuits.set_index("round")
    st.table(circuits[["name", "country"]])


def show_driver_progression(drivers, rankings):
    """
    Plots the Formula 1 driver progression in that year
    """

    drivers.sort_values(by=["round"], inplace=True)
    drivers["name"] = drivers["forename"] + " " + drivers["surname"]

    line = px.line(
        drivers,
        x="round",
        y="points",
        color="code",
        hover_data=["name"],
        category_orders={"code": rankings},
    )

    line.update_traces(
        mode="lines+markers",
        line=dict(shape="linear"),
        marker=dict(size=6),
    )
    line.update_layout(
        xaxis_title="Race Number",
        yaxis_title="Driver Points",
        title="",
        legend_title="Driver",
        title_x=0.5,
        height=700,
    )

    st.plotly_chart(line, use_container_width=True)


def show_driver_points(rankings):
    """
    Plots the driver points for the season
    """
    rankings["name"] = (
        rankings.index.astype(str)
        + ". "
        + rankings["forename"]
        + " "
        + rankings["surname"]
    )
    bar = px.bar(
        rankings,
        x="points",
        y="code",
        color="code",
        hover_data=["name"],
        text="name",
    )
    bar.update_layout(
        showlegend=False,
        xaxis_title="Driver Points",
        yaxis_title="Driver",
        title="",
        title_x=0.5,
        height=700,
    )
    bar.update_traces(
        # textposition="outside",
        insidetextanchor="end",
        texttemplate="%{text}",
    )

    # Add annotations for data points with points equal to 0
    for i, row in rankings.iterrows():
        if row["points"] == 0:
            bar.add_annotation(
                x=0,
                y=row["code"],
                text=row["name"],
                showarrow=False,
                xanchor="left",
            )

    st.plotly_chart(bar, use_container_width=True)


circuits = get_circuit_data()
drivers = get_driver_data()

# Select year
selected_year = st.sidebar.selectbox(
    "Select the year you want to explore",
    list(reversed(range(START_YEAR, END_YEAR + 1))),
    index=0,
)

filtered_circuits = filter_year(circuits, selected_year)
filtered_drivers = filter_year(drivers, selected_year)
rankings = get_season_rankings(filtered_drivers)


# Layout
st.image("img/f1_logo.png", width=300)
st.title(f"Formula 1 Season {selected_year}")

with st.sidebar:
    st.text("Circuits in the season")
    show_races(filtered_circuits)

show_winner_text(rankings)
show_world_map(filtered_circuits)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(
        "<div style='text-align: center; font-size: 20px;'>Driver Progression</div>",
        unsafe_allow_html=True,
    )
    show_driver_progression(filtered_drivers, rankings["code"].tolist())
with col2:
    st.markdown(
        "<div style='text-align: center; font-size: 20px;'>Final Driver Standings</div>",
        unsafe_allow_html=True,
    )
    show_driver_points(rankings)


# st.header("Rankings for a Specific Circuit")
# selected_circuit = st.selectbox("Select a circuit", filtered_circuits["name"].tolist())
# st.text(f"Rankings for {selected_circuit}")
# if selected_circuit:
#     # Assuming you have a function get_circuit_rankings that takes a circuit and returns the rankings for that circuit
#     circuit_rankings = get_circuit_rankings(
#         filtered_drivers, filtered_circuits, selected_circuit
#     )
#     st.table(circuit_rankings)
#     show_driver_points(circuit_rankings)
#     st.text("Note: Drivers only get points if they finish in the top 10")
