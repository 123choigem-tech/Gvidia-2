import folium
import pandas as pd


def make_frequency_map(freq_df: pd.DataFrame) -> folium.Map:
    if freq_df.empty:
        return folium.Map(location=[35.5, 128.0], zoom_start=7, tiles="OpenStreetMap")

    df = freq_df.dropna(subset=["lat", "lon"]).copy()
    if df.empty:
        return folium.Map(location=[35.5, 128.0], zoom_start=7, tiles="OpenStreetMap")

    m = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=7,
        tiles="OpenStreetMap",
    )
    max_count = float(df["count"].max()) if not df.empty else 1.0
    for _, row in df.iterrows():
        ratio = float(row["count"]) / max_count if max_count else 0.0
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=max(5, float(row["count"]) / 4),
            color="#0f172a",
            weight=1,
            fill=True,
            fill_color="#00a3a3",
            fill_opacity=0.35 + 0.45 * ratio,
            tooltip=f"{row['location']}: {int(row['count'])}건",
        ).add_to(m)
    return m
