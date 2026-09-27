import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Spotify Wrapped Dashboard", page_icon="🎧", layout="wide"
)

# Custom Styling for Spotify Dark Theme
st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .metric-card {
        background-color: #181818;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #282828;
        text-align: center;
        margin-bottom: 10px;
    }
    .spotify-green { color: #1DB954; }
    .spotify-yellow { color: #FFE600; }
    .spotify-pink { color: #FF007F; }
    .spotify-purple { color: #A020F0; }
    </style>
""",
    unsafe_allow_dict_style=True,
)


def generate_visual_card(
    df, total_minutes, top_genres, top_songs, top_artists, aura_metrics
):
    """Generates a high-res matplotlib Spotify Wrapped image card."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 11), facecolor="#121212")
    ax.set_facecolor("#121212")

    c_green, c_yellow, c_pink, c_purple, c_white, c_sub = (
        "#1DB954",
        "#FFE600",
        "#FF007F",
        "#A020F0",
        "#FFFFFF",
        "#B3B3B3",
    )

    # Title
    plt.text(
        0.5,
        0.94,
        "SPOTIFY WRAPPED",
        color=c_green,
        fontsize=24,
        fontweight="bold",
        ha="center",
    )
    plt.text(
        0.5,
        0.91,
        "YOUR YEAR IN MUSIC",
        color=c_sub,
        fontsize=12,
        ha="center",
        fontweight="bold",
    )

    # Minutes & Top Genre
    plt.text(
        0.08,
        0.83,
        "LISTENING TIME",
        color=c_yellow,
        fontsize=13,
        fontweight="bold",
    )
    plt.text(
        0.08,
        0.79,
        f"{total_minutes:,} MINS",
        color=c_white,
        fontsize=28,
        fontweight="bold",
    )

    plt.text(0.55, 0.83, "TOP GENRE", color=c_pink, fontsize=13, fontweight="bold")
    plt.text(
        0.55,
        0.79,
        f"{top_genres.index[0]}",
        color=c_white,
        fontsize=24,
        fontweight="bold",
    )

    # Audio Aura
    plt.text(
        0.08,
        0.70,
        "AUDIO AURA",
        color=c_purple,
        fontsize=13,
        fontweight="bold",
    )
    plt.text(
        0.08,
        0.66,
        "Energetic & Groovy",
        color=c_white,
        fontsize=18,
        fontweight="bold",
    )
    plt.text(
        0.08,
        0.63,
        f"Dance: {aura_metrics['dance']}% | Energy: {aura_metrics['energy']}% | Tempo: {aura_metrics['bpm']} BPM",
        color=c_sub,
        fontsize=10,
    )

    # Top Songs
    plt.text(
        0.08, 0.54, "TOP SONGS", color=c_green, fontsize=15, fontweight="bold"
    )
    y_pos = 0.49
    for idx, row in enumerate(top_songs.head(5).itertuples(), 1):
        plt.text(
            0.08,
            y_pos,
            f"{idx}. {row.Song}",
            color=c_white,
            fontsize=12,
            fontweight="bold",
        )
        plt.text(
            0.08,
            y_pos - 0.022,
            f"    {row.Artist} • {row.Streams_Millions:.1f}M Streams",
            color=c_sub,
            fontsize=9,
        )
        y_pos -= 0.055

    # Top Artists
    plt.text(
        0.55,
        0.54,
        "TOP ARTISTS",
        color=c_yellow,
        fontsize=15,
        fontweight="bold",
    )
    y_pos = 0.49
    for idx, (artist, streams) in enumerate(
        top_artists.head(5).items(), 1
    ):
        plt.text(
            0.55,
            y_pos,
            f"{idx}. {artist}",
            color=c_white,
            fontsize=12,
            fontweight="bold",
        )
        plt.text(
            0.55,
            y_pos - 0.022,
            f"    {streams:,.1f}M Streams",
            color=c_sub,
            fontsize=9,
        )
        y_pos -= 0.055

    ax.axis("off")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(
        buf,
        format="png",
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    buf.seek(0)
    plt.close()
    return buf


def main():
    st.title("🎧 Your Personal Spotify Wrapped")
    st.caption("Upload your music dataset or analyze default data.")

    # File Uploader
    uploaded_file = st.sidebar.file_uploader(
        "Upload Dataset (.xlsx / .csv)", type=["xlsx", "csv"]
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, sheet_name="Music_Dataset")
    else:
        # Default filename in local working directory
        try:
            df = pd.read_excel(
                "international_music_dataset_expanded_finnal.xlsx",
                sheet_name="Music_Dataset",
            )
        except Exception:
            st.warning(
                "Please upload a dataset file using the sidebar to continue."
            )
            return

    # Sidebar Options
    top_n = st.sidebar.slider(
        "Select Number of Top Items", min_value=3, max_value=10, value=5
    )

    # Compute Metrics
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

    aura_metrics = {
        "dance": int(df["Danceability"].mean() * 100),
        "energy": int(df["Energy"].mean() * 100),
        "bpm": int(df["Tempo_BPM"].mean()),
    }

    # Tab Navigation (Story Experience)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "⏱️ Listening Time",
            "🔮 Audio Aura",
            "🎶 Top Genres",
            "🔥 Top Songs",
            "👑 Top Artists",
        ]
    )

    with tab1:
        st.header("⏱️ Total Listening Time")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Listening Time", f"{total_minutes:,} Minutes")
            st.write(
                "That puts you in the **top 1% of music lovers worldwide**!"
            )
            st.write(f"Total Tracks Analyzed: `{len(df)}`")
            st.write(f"Unique Artists Listened To: `{df['Artist'].nunique()}`")
        with col2:
            st.info(
                "💡 **Fun Fact:** You listened to enough music to drive across the country multiple times!"
            )

    with tab2:
        st.header("🔮 Your Audio Aura")
        col1, col2, col3 = st.columns(3)
        col1.metric("Danceability", f"{aura_metrics['dance']}%")
        col2.metric("Energy Level", f"{aura_metrics['energy']}%")
        col3.metric("Average Tempo", f"{aura_metrics['bpm']} BPM")

        st.subheader("Vibe Analysis")
        st.success(
            "✨ **Your Aura Color:** Neon Green & Vibrant Violet — You thrive on energetic, high-tempo beats with expressive vocals."
        )

    with tab3:
        st.header(f"🎶 Your Top {top_n} Genres")
        st.bar_chart(top_genres)
        st.dataframe(
            top_genres.reset_index().rename(
                columns={"index": "Genre", "Genre": "Track Count"}
            ),
            use_container_width=True,
        )

    with tab4:
        st.header(f"🔥 Top {top_n} Songs by Popularity & Streams")
        st.dataframe(
            top_songs[
                [
                    "Song",
                    "Artist",
                    "Album",
                    "Popularity_Score",
                    "Streams_Millions",
                    "Genre",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with tab5:
        st.header(f"👑 Top {top_n} Artists by Stream Count")
        st.bar_chart(top_artists)
        st.dataframe(
            top_artists.reset_index().rename(
                columns={"Streams_Millions": "Total Streams (Millions)"}
            ),
            use_container_width=True,
        )

    # Export Section
    st.divider()
    st.subheader("🖼️ Download Your Wrapped Image Summary")

    img_buffer = generate_visual_card(
        df, total_minutes, top_genres, top_songs, top_artists, aura_metrics
    )
    st.image(img_buffer, caption="Spotify Wrapped Card", width=400)

    st.download_button(
        label="📥 Download Spotify Wrapped Card",
        data=img_buffer,
        file_name="spotify_wrapped_summary.png",
        mime="image/png",
    )


if __name__ == "__main__":
    main()
