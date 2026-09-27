import pandas as pd
import streamlit as st

# 1. Page Configuration & Theme Styling
st.set_page_config(
    page_title="Spotify Wrapped",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stMetric {
        background-color: #181818;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #282828;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def main():
    st.title("🎧 Your Spotify Wrapped")
    st.caption("A summary of your year in music.")

    # 2. Dataset Loader
    uploaded_file = st.sidebar.file_uploader(
        "Upload Dataset (.xlsx or .csv)", type=["xlsx", "csv"]
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, sheet_name="Music_Dataset")
    else:
        try:
            df = pd.read_excel(
                "international_music_dataset_expanded_finnal.xlsx",
                sheet_name="Music_Dataset",
            )
        except Exception:
            st.warning(
                "⚠️ Dataset not found locally. Please upload your dataset using the sidebar."
            )
            return

    # Clean & safely convert columns to numeric to avoid formatting errors
    numeric_cols = [
        "Streams_Millions",
        "Popularity_Score",
        "Duration_Sec",
        "Danceability",
        "Energy",
        "Tempo_BPM",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Sidebar Controls
    top_n = st.sidebar.slider(
        "Number of Top Items to Display", min_value=3, max_value=10, value=5
    )

    # 3. Calculate Metrics
    total_minutes = int(df["Duration_Sec"].sum() / 60)
    top_genres = df["Genre"].value_counts().head(top_n)
    top_songs = df.sort_values(
        by=["Popularity_Score", "Streams_Millions"], ascending=[False, False]
    ).head(top_n)
    top_artists = (
        df.groupby("Artist")["Streams_Millions"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    avg_danceability = int(df["Danceability"].mean() * 100)
    avg_energy = int(df["Energy"].mean() * 100)
    avg_bpm = int(df["Tempo_BPM"].mean())

    # 4. Streamlit Wrapped Story Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "⏱️ Listening Time",
            "🔮 Audio Aura",
            "🎶 Top Genres",
            "🔥 Top Songs",
            "👑 Top Artists",
        ]
    )

    # Tab 1: Listening Time
    with tab1:
        st.header("⏱️ Total Listening Time")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Listening Time", f"{total_minutes:,} Mins")
            st.write(
                "That puts you in the **top 1% of music lovers worldwide**!"
            )
            st.write(f"• **Total Songs Analyzed:** `{len(df)}`")
            st.write(
                f"• **Unique Artists Discovered:** `{df['Artist'].nunique()}`"
            )
        with col2:
            st.info(
                "💡 **Fun Fact:** You listened to enough music to drive across the country multiple times!"
            )

    # Tab 2: Audio Aura
    with tab2:
        st.header("🔮 Your Audio Aura")
        c1, c2, c3 = st.columns(3)
        c1.metric("Danceability", f"{avg_danceability}%")
        c2.metric("Energy Level", f"{avg_energy}%")
        c3.metric("Average Tempo", f"{avg_bpm} BPM")

        st.subheader("Your Vibe Summary")
        st.success(
            "✨ **Aura Persona: High-Energy & Energetic Beats**\n\nYour listening habits show a love for lively tempos, upbeat dance tracks, and expressive vocals."
        )

    # Tab 3: Top Genres
    with tab3:
        st.header(f"🎶 Top {top_n} Genres")
        st.write(f"Your #1 genre this year was **{top_genres.index[0]}**!")

        st.bar_chart(top_genres)

        st.subheader("Genre Breakdown")
        st.dataframe(
            top_genres.reset_index().rename(
                columns={"Genre": "Genre Name", "count": "Song Count"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    # Tab 4: Top Songs
    with tab4:
        st.header(f"🔥 Top {top_n} Songs by Popularity & Streams")
        st.write("The tracks you had on repeat all year long:")

        for idx, row in enumerate(top_songs.itertuples(), start=1):
            with st.expander(
                f"#{idx} — {row.Song} by {row.Artist}", expanded=(idx == 1)
            ):
                sc1, sc2, sc3 = st.columns(3)
                sc1.write(f"**Album:** {getattr(row, 'Album', 'N/A')}")
                sc2.write(
                    f"**Streams:** {float(getattr(row, 'Streams_Millions', 0)):.1f} Million"
                )
                sc3.write(
                    f"**Popularity Score:** {int(getattr(row, 'Popularity_Score', 0))}/100"
                )

    # Tab 5: Top Artists
    with tab5:
        st.header(f"👑 Top {top_n} Artists")
        st.write(f"Your #1 artist was **{top_artists.index[0]}**!")

        st.bar_chart(top_artists)

        st.subheader("Streams by Artist")
        st.dataframe(
            top_artists.reset_index().rename(
                columns={"Streams_Millions": "Total Streams (Millions)"}
            ),
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
