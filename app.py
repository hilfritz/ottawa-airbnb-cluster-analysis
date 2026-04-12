from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Ottawa Airbnb Dashboard", page_icon="🏠", layout="wide")

DATA_PATH = Path("DATA AIRBNB.csv")

EXPECTED_COLUMNS = [
    "id",
    "name",
    "host_id",
    "host_name",
    "neighbourhood_group",
    "neighbourhood",
    "latitude",
    "longitude",
    "room_type",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "last_review",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
    "number_of_reviews_ltm",
    "license",
]


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find dataset: {file_path}")

    attempts: list[pd.DataFrame] = []

    try:
        df1 = pd.read_csv(file_path, sep=";", engine="python")
        attempts.append(df1)
    except Exception:
        pass

    try:
        df2 = pd.read_csv(file_path, sep=";", engine="python", header=None)
        if df2.shape[1] >= len(EXPECTED_COLUMNS):
            rename_map = {
                old: new for old, new in zip(df2.columns[: len(EXPECTED_COLUMNS)], EXPECTED_COLUMNS)
            }
            df2 = df2.rename(columns=rename_map)
        attempts.append(df2)
    except Exception:
        pass

    if not attempts:
        raise ValueError("Unable to read the dataset.")

    def score(df: pd.DataFrame) -> int:
        cols = {str(c).strip().lower() for c in df.columns}
        wanted = {"price", "latitude", "longitude", "room_type", "neighbourhood"}
        return len(cols & wanted)

    df = max(attempts, key=score).copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    aliases = {
        "neighbourhood_cleansed": "neighbourhood",
        "neighborhood": "neighbourhood",
    }
    for old, new in aliases.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})

    if "price" not in df.columns and df.shape[1] >= 10:
        df = df.rename(columns={df.columns[9]: "price"})
    if "latitude" not in df.columns and df.shape[1] >= 7:
        df = df.rename(columns={df.columns[6]: "latitude"})
    if "longitude" not in df.columns and df.shape[1] >= 8:
        df = df.rename(columns={df.columns[7]: "longitude"})
    if "room_type" not in df.columns and df.shape[1] >= 9:
        df = df.rename(columns={df.columns[8]: "room_type"})
    if "neighbourhood" not in df.columns and df.shape[1] >= 6:
        df = df.rename(columns={df.columns[5]: "neighbourhood"})
    if "name" not in df.columns and df.shape[1] >= 2:
        df = df.rename(columns={df.columns[1]: "name"})

    numeric_cols = [
        "price",
        "latitude",
        "longitude",
        "minimum_nights",
        "number_of_reviews",
        "reviews_per_month",
        "availability_365",
        "calculated_host_listings_count",
        "number_of_reviews_ltm",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "last_review" in df.columns:
        df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce", dayfirst=True)

    required = [c for c in ["price", "latitude", "longitude"] if c in df.columns]
    if required:
        df = df.dropna(subset=required)

    if "latitude" in df.columns:
        df = df[df["latitude"].between(45.0, 45.6, inclusive="both")]
    if "longitude" in df.columns:
        df = df[df["longitude"].between(-76.2, -75.0, inclusive="both")]
    if "price" in df.columns:
        df = df[df["price"] > 0]

    return df.reset_index(drop=True)


@st.cache_data
def add_clusters(df: pd.DataFrame, k: int = 3) -> pd.DataFrame:
    cluster_cols = [c for c in ["price", "latitude", "longitude"] if c in df.columns]
    out = df.copy()

    if len(cluster_cols) < 3 or len(df) < k:
        out["cluster"] = "-1"
        return out

    features = out[cluster_cols].copy()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    out["cluster"] = model.fit_predict(scaled).astype(str)
    return out


@st.cache_data
def summarize_clusters(df: pd.DataFrame) -> pd.DataFrame:
    if "cluster" not in df.columns or df.empty:
        return pd.DataFrame()

    grouped = (
        df.groupby("cluster", dropna=False)
        .agg(
            listings=("cluster", "size"),
            avg_price=("price", "mean"),
            median_price=("price", "median"),
            min_price=("price", "min"),
            max_price=("price", "max"),
        )
        .reset_index()
        .sort_values("avg_price", ascending=True)
    )
    return grouped


@st.cache_data
def label_clusters(df: pd.DataFrame) -> dict[str, str]:
    if "cluster" not in df.columns or df.empty:
        return {}

    summary = (
        df.groupby("cluster")["price"]
        .mean()
        .sort_values()
        .reset_index()
    )

    labels = ["Budget", "Mid-range", "Premium"]
    cluster_map: dict[str, str] = {}

    for i, row in summary.iterrows():
        cluster_key = str(row["cluster"])
        if i < len(labels):
            cluster_map[cluster_key] = labels[i]
        else:
            cluster_map[cluster_key] = f"Tier {i + 1}"

    return cluster_map


@st.cache_data
def cluster_centroids(df: pd.DataFrame) -> pd.DataFrame:
    if "cluster" not in df.columns or df.empty:
        return pd.DataFrame(columns=["cluster", "latitude", "longitude", "avg_price", "listings"])

    centroids = (
        df.groupby("cluster", dropna=False)
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            avg_price=("price", "mean"),
            listings=("cluster", "size"),
        )
        .reset_index()
    )
    return centroids


def render_map(df: pd.DataFrame, mode: str) -> None:
    hover_cols = [c for c in ["neighbourhood", "room_type", "price", "cluster_label"] if c in df.columns]

    cluster_color_map = {
        "Budget": "#1f77b4",
        "Mid-range": "#2ca02c",
        "Premium": "#d62728",
        "Unclassified": "#7f7f7f",
    }

    if mode == "Heatmap":
        fig = px.density_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            z="price" if "price" in df.columns else None,
            radius=22,
            zoom=9.5,
            height=600,
            hover_name="name" if "name" in df.columns else None,
            hover_data=hover_cols,
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    if mode == "Clusters with centroids":
        fig = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            color="cluster_label" if "cluster_label" in df.columns else None,
            color_discrete_map=cluster_color_map,
            size="price" if "price" in df.columns else None,
            hover_name="name" if "name" in df.columns else None,
            hover_data=hover_cols,
            zoom=9.5,
            height=600,
        )

        centroids = cluster_centroids(df)
        if not centroids.empty:
            centroids["cluster"] = centroids["cluster"].astype(str)
            label_map = label_clusters(df)
            centroids["cluster_label"] = centroids["cluster"].map(label_map).fillna("Unclassified")

            fig.add_scattermapbox(
                lat=centroids["latitude"],
                lon=centroids["longitude"],
                mode="markers",
                marker=dict(
                    size=26,
                    color="black",
                    opacity=0.9,
                ),
                showlegend=False,
                hoverinfo="skip",
            )

            fig.add_scattermapbox(
                lat=centroids["latitude"],
                lon=centroids["longitude"],
                mode="markers+text",
                marker=dict(
                    size=20,
                    color="#FFD700",
                    opacity=0.95,
                    symbol="circle",
                ),
                text=centroids["cluster_label"],
                textposition="top right",
                name="Centroids",
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Avg price: $%{customdata[0]:.2f}<br>"
                    "Listings: %{customdata[1]}<extra></extra>"
                ),
                customdata=centroids[["avg_price", "listings"]].to_numpy(),
            )

        fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    if mode == "3D price columns":
        cluster_color_map_rgb = {
            "Budget": [31, 119, 180, 180],
            "Mid-range": [44, 160, 44, 180],
            "Premium": [214, 39, 40, 180],
            "Unclassified": [127, 127, 127, 180],
        }

        df_3d = df.copy()
        df_3d["fill_color"] = df_3d["cluster_label"].map(cluster_color_map_rgb).apply(
            lambda x: x if isinstance(x, list) else [127, 127, 127, 180]
        )

        view_state = pdk.ViewState(
            latitude=float(df_3d["latitude"].mean()),
            longitude=float(df_3d["longitude"].mean()),
            zoom=9.6,
            pitch=25,
        )

        tooltip = {
            "html": (
                "<b>{name}</b><br/>"
                "Neighbourhood: {neighbourhood}<br/>"
                "Room type: {room_type}<br/>"
                "Price: ${price}<br/>"
                "Cluster: {cluster_label}"
            ),
            "style": {"backgroundColor": "steelblue", "color": "white"},
        }

        layer = pdk.Layer(
            "ColumnLayer",
            data=df_3d,
            get_position="[longitude, latitude]",
            get_elevation="price",
            elevation_scale=1,
            radius=70,
            pickable=True,
            extruded=True,
            get_fill_color="fill_color",
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light",
        )
        st.pydeck_chart(deck, use_container_width=True)
        return

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="cluster_label" if "cluster_label" in df.columns else None,
        color_discrete_map=cluster_color_map,
        size="price" if "price" in df.columns else None,
        hover_name="name" if "name" in df.columns else None,
        hover_data=hover_cols,
        zoom=9.5,
        height=600,
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


try:
    df_raw = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Failed to load the dataset: {exc}")
    st.stop()

st.sidebar.header("Filters")

room_type_options = (
    sorted(df_raw["room_type"].dropna().astype(str).unique().tolist())
    if "room_type" in df_raw.columns
    else []
)
selected_room_types = st.sidebar.multiselect(
    "Room type",
    options=room_type_options,
    default=room_type_options,
)

price_min = int(df_raw["price"].quantile(0.01)) if "price" in df_raw.columns else 0
price_max = int(df_raw["price"].quantile(0.99)) if "price" in df_raw.columns else 500
selected_price = st.sidebar.slider(
    "Nightly price range",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, price_max),
)

neighbourhood_options = (
    sorted(df_raw["neighbourhood"].dropna().astype(str).unique().tolist())
    if "neighbourhood" in df_raw.columns
    else []
)
selected_neighbourhoods = st.sidebar.multiselect(
    "Neighbourhood",
    options=neighbourhood_options,
    default=neighbourhood_options,
)

filtered = df_raw.copy()
if selected_room_types and "room_type" in filtered.columns:
    filtered = filtered[filtered["room_type"].astype(str).isin(selected_room_types)]
if "price" in filtered.columns:
    filtered = filtered[filtered["price"].between(selected_price[0], selected_price[1], inclusive="both")]
if selected_neighbourhoods and "neighbourhood" in filtered.columns:
    filtered = filtered[filtered["neighbourhood"].astype(str).isin(selected_neighbourhoods)]

clustered = add_clusters(filtered, k=3)
cluster_label_map = label_clusters(clustered)
clustered["cluster_label"] = clustered["cluster"].astype(str).map(cluster_label_map).fillna("Unclassified")

cluster_filter_options = ["Budget", "Mid-range", "Premium"]
selected_clusters = st.sidebar.multiselect(
    "Cluster",
    options=cluster_filter_options,
    default=cluster_filter_options,
)

if "cluster_label" in clustered.columns and selected_clusters:
    clustered = clustered[clustered["cluster_label"].isin(selected_clusters)]

cluster_summary = summarize_clusters(clustered)
if not cluster_summary.empty:
    cluster_summary["cluster"] = cluster_summary["cluster"].astype(str)
    cluster_summary["cluster_label"] = cluster_summary["cluster"].map(cluster_label_map).fillna("Unclassified")

st.title("Ottawa Airbnb Cluster Dashboard")
st.caption(
    "Interactive dashboard for exploring Ottawa Airbnb price segments, room types, neighbourhoods, and spatial clustering."
)

if clustered.empty:
    st.warning("No rows match the current filters.")
    st.stop()

st.info(
    "Clusters are labeled automatically by average price: "
    "Budget = lowest average price, Mid-range = middle, Premium = highest."
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Listings", f"{len(clustered):,}")
k2.metric("Average price", f"${clustered['price'].mean():,.2f}" if "price" in clustered.columns else "N/A")
k3.metric("Median price", f"${clustered['price'].median():,.2f}" if "price" in clustered.columns else "N/A")
k4.metric(
    "Neighbourhoods",
    f"{clustered['neighbourhood'].nunique():,}" if "neighbourhood" in clustered.columns else "N/A",
)

left, right = st.columns((1.6, 1))

with left:
    st.subheader("Interactive map")
    map_mode = st.radio(
        "Map view",
        ["Cluster bubbles", "Clusters with centroids", "Heatmap", "3D price columns"],
        horizontal=True,
    )
    render_map(clustered, map_mode)
    st.caption(
        "You can zoom, pan, and hover. Heatmap highlights dense expensive areas, "
        "centroids show cluster centers, and 3D columns emphasize price differences."
    )

with right:
    st.subheader("Cluster summary")
    if not cluster_summary.empty:
        summary_display = cluster_summary.copy()
        summary_display = summary_display[
            ["cluster_label", "listings", "avg_price", "median_price", "min_price", "max_price"]
        ]
        summary_display = summary_display.rename(
            columns={
                "cluster_label": "Cluster",
                "listings": "Listings",
                "avg_price": "Avg price",
                "median_price": "Median price",
                "min_price": "Min price",
                "max_price": "Max price",
            }
        )
        for col in ["Avg price", "Median price", "Min price", "Max price"]:
            summary_display[col] = summary_display[col].round(2)
        st.dataframe(summary_display, use_container_width=True, hide_index=True)
    else:
        st.info("Cluster summary is unavailable for the current selection.")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Price distribution")
    fig_hist = px.histogram(
        clustered,
        x="price",
        color="cluster_label" if "cluster_label" in clustered.columns else None,
        color_discrete_map={
            "Budget": "#1f77b4",
            "Mid-range": "#2ca02c",
            "Premium": "#d62728",
            "Unclassified": "#7f7f7f",
        },
        nbins=30,
        marginal="box",
        height=420,
    )
    fig_hist.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_hist, use_container_width=True)

with c2:
    st.subheader("Average price by room type")
    if "room_type" in clustered.columns:
        room_summary = (
            clustered.groupby("room_type", dropna=False)
            .agg(avg_price=("price", "mean"), listings=("room_type", "size"))
            .reset_index()
            .sort_values("avg_price", ascending=False)
        )
        fig_room = px.bar(
            room_summary,
            x="room_type",
            y="avg_price",
            text="listings",
            height=420,
        )
        fig_room.update_traces(textposition="outside")
        fig_room.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title="Average nightly price",
        )
        st.plotly_chart(fig_room, use_container_width=True)
    else:
        st.info("room_type column not available.")

b1, b2 = st.columns(2)

with b1:
    st.subheader("Top neighbourhoods by listing count")
    if "neighbourhood" in clustered.columns:
        nbh_count = (
            clustered.groupby("neighbourhood", dropna=False)
            .size()
            .reset_index(name="listings")
            .sort_values("listings", ascending=False)
            .head(15)
        )
        fig_nbh = px.bar(
            nbh_count,
            x="listings",
            y="neighbourhood",
            orientation="h",
            height=500,
        )
        fig_nbh.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(categoryorder="total ascending"),
        )
        st.plotly_chart(fig_nbh, use_container_width=True)
    else:
        st.info("neighbourhood column not available.")

with b2:
    st.subheader("Price vs availability")
    if {"availability_365", "price"}.issubset(clustered.columns):
        fig_scatter = px.scatter(
            clustered,
            x="availability_365",
            y="price",
            color="cluster_label" if "cluster_label" in clustered.columns else None,
            color_discrete_map={
                "Budget": "#1f77b4",
                "Mid-range": "#2ca02c",
                "Premium": "#d62728",
                "Unclassified": "#7f7f7f",
            },
            hover_name="name" if "name" in clustered.columns else None,
            hover_data=[c for c in ["neighbourhood", "room_type"] if c in clustered.columns],
            height=500,
        )
        fig_scatter.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("availability_365 column not available.")

st.subheader("Filtered dataset preview")
preview_cols = [
    c for c in [
        "name",
        "neighbourhood",
        "room_type",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "availability_365",
        "cluster_label",
    ] if c in clustered.columns
]
st.dataframe(
    clustered[preview_cols].sort_values("price", ascending=False).head(100),
    use_container_width=True,
    hide_index=True,
)