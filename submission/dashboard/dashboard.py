import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    df = pd.read_csv(csv_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load_data()

# Sidebar Filters
with st.sidebar:
    st.title("🚲 Bike Sharing Analytics")
    st.markdown("Filter interaktif untuk mengeksplorasi pola penyewaan sepeda Capital Bikeshare (2011–2012).")

    min_date = df["dteday"].min().date()
    max_date = df["dteday"].max().date()

    date_range = st.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    selected_seasons = st.multiselect(
        "Pilih Musim (Season)",
        options=["Spring", "Summer", "Fall", "Winter"],
        default=["Spring", "Summer", "Fall", "Winter"]
    )

    weather_options = list(df["weather_label"].unique())
    selected_weather = st.multiselect(
        "Kondisi Cuaca (Weather)",
        options=weather_options,
        default=weather_options
    )

    selected_day_type = st.multiselect(
        "Tipe Hari (Day Type)",
        options=["Working Day", "Weekend / Holiday"],
        default=["Working Day", "Weekend / Holiday"]
    )

# Handle single date selection safely
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0] if isinstance(date_range, tuple) else date_range

filtered_df = df[
    (df["dteday"].dt.date >= start_date) &
    (df["dteday"].dt.date <= end_date) &
    (df["season_label"].isin(selected_seasons)) &
    (df["weather_label"].isin(selected_weather)) &
    (df["day_type"].isin(selected_day_type))
]

st.title("Dashboard Analisis Penyewaan Sepeda (2011–2012)")
st.markdown(
    "Dashboard interaktif untuk memantau pola jam operasional **Casual vs Registered User**, "
    "dampak **cuaca dan musim**, serta **segmentasi zona waktu & tingkat permintaan**."
)

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter saat ini. Silakan ubah pilihan filter di sidebar.")
    st.stop()

# KPI Metrics
daily_agg = filtered_df.groupby("dteday", as_index=False)[["casual", "registered", "cnt"]].sum()
total_rentals = int(filtered_df["cnt"].sum())
total_registered = int(filtered_df["registered"].sum())
total_casual = int(filtered_df["casual"].sum())
avg_daily = daily_agg["cnt"].mean()

reg_pct = (total_registered / total_rentals * 100) if total_rentals > 0 else 0
cas_pct = (total_casual / total_rentals * 100) if total_rentals > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan", f"{total_rentals:,}")
with col2:
    st.metric("Registered Users", f"{total_registered:,}", f"{reg_pct:.1f}% dari total")
with col3:
    st.metric("Casual Users", f"{total_casual:,}", f"{cas_pct:.1f}% dari total")
with col4:
    st.metric("Rata-Rata Harian", f"{avg_daily:,.0f} unit/hari")

st.divider()

tab1, tab2, tab3 = st.tabs([
    "1. Pola Jam & Segmen Pengguna",
    "2. Pengaruh Cuaca & Musim",
    "3. Analisis Lanjutan (Clustering)"
])

with tab1:
    st.subheader("Perbandingan Pola Penyewaan per Jam: Working Day vs Weekend / Holiday")
    hourly_grp = filtered_df.groupby(["day_type", "hr"], as_index=False)[["casual", "registered", "cnt"]].mean()

    c1, c2 = st.columns(2)
    for idx, (col, dtype) in enumerate(zip([c1, c2], ["Working Day", "Weekend / Holiday"])):
        with col:
            sub = hourly_grp[hourly_grp["day_type"] == dtype]
            fig, ax = plt.subplots(figsize=(7, 4.2))
            if not sub.empty:
                ax.plot(sub["hr"], sub["registered"], marker="o", linewidth=2.2, color="#1E88E5", label="Registered")
                ax.plot(sub["hr"], sub["casual"], marker="s", linewidth=2.2, color="#FB8C00", label="Casual")
                ax.fill_between(sub["hr"], sub["registered"], color="#1E88E5", alpha=0.08)
                ax.fill_between(sub["hr"], sub["casual"], color="#FB8C00", alpha=0.10)
            ax.set_title(f"{dtype}", fontsize=11.5, fontweight="bold")
            ax.set_xlabel("Jam (00:00 - 23:00)")
            ax.set_ylabel("Rata-Rata Penyewaan / Jam")
            ax.set_xticks(range(0, 24, 2))
            ax.set_ylim(bottom=0)
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.legend(frameon=False)
            st.pyplot(fig)
            plt.close(fig)

with tab2:
    st.subheader("Dampak Kondisi Cuaca dan Musim Terhadap Rata-Rata Penyewaan Harian")
    daily_env = filtered_df.groupby(["dteday", "weather_label", "season_label"], as_index=False)["cnt"].sum()

    c1, c2 = st.columns(2)
    with c1:
        w_order = ["Clear / Partly Cloudy", "Mist / Cloudy", "Light Snow / Light Rain", "Heavy Rain / Snow"]
        w_series = daily_env.groupby("weather_label")["cnt"].mean().reindex([w for w in w_order if w in daily_env["weather_label"].unique()])
        fig, ax = plt.subplots(figsize=(7, 4.2))
        colors = ["#1E88E5" if v == w_series.max() else ("#E53935" if v == w_series.min() else "#B0BEC5") for v in w_series.values]
        bars = ax.bar(w_series.index, w_series.values, color=colors, width=0.55)
        ax.set_title("Rata-Rata Penyewaan Harian per Kondisi Cuaca", fontsize=11.5, fontweight="bold")
        ax.set_ylabel("Rata-Rata Penyewaan Harian")
        ax.set_ylim(0, w_series.max() * 1.18 if len(w_series) > 0 else 100)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.xticks(rotation=12, ha="right")
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, h + (w_series.max()*0.02), f"{h:,.0f}", ha="center", fontweight="bold", fontsize=9.5)
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        s_order = ["Spring", "Summer", "Fall", "Winter"]
        s_series = daily_env.groupby("season_label")["cnt"].mean().reindex([s for s in s_order if s in daily_env["season_label"].unique()])
        fig, ax = plt.subplots(figsize=(7, 4.2))
        colors = ["#1E88E5" if v == s_series.max() else ("#E53935" if v == s_series.min() else "#B0BEC5") for v in s_series.values]
        bars = ax.bar(s_series.index, s_series.values, color=colors, width=0.55)
        ax.set_title("Rata-Rata Penyewaan Harian per Musim", fontsize=11.5, fontweight="bold")
        ax.set_ylabel("Rata-Rata Penyewaan Harian")
        ax.set_ylim(0, s_series.max() * 1.18 if len(s_series) > 0 else 100)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, h + (s_series.max()*0.02), f"{h:,.0f}", ha="center", fontweight="bold", fontsize=9.5)
        st.pyplot(fig)
        plt.close(fig)

with tab3:
    st.subheader("Clustering: Manual Grouping Zona Waktu & Binning Tingkat Permintaan")
    c1, c2 = st.columns(2)
    with c1:
        period_order = [
            "1. Night (00-05)",
            "2. Morning Commute (06-09)",
            "3. Midday (10-15)",
            "4. Evening Commute (16-19)",
            "5. Late Evening (20-23)"
        ]
        p_grp = filtered_df.groupby(["time_period", "day_type"])["cnt"].mean().unstack().reindex(period_order)
        fig, ax = plt.subplots(figsize=(7, 4.2))
        p_grp.plot(kind="bar", ax=ax, color=["#1E88E5", "#FB8C00"], width=0.65)
        ax.set_title("Rata-Rata Penyewaan / Jam per Zona Waktu", fontsize=11.5, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("Rata-Rata Penyewaan / Jam")
        ax.set_xticklabels(["Night", "Morning", "Midday", "Evening", "Late Eve"], rotation=0)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False)
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        daily_tier_df = filtered_df.groupby(["dteday", "season_label"], as_index=False)["cnt"].sum()
        daily_tier_df["demand_tier"] = pd.cut(
            daily_tier_df["cnt"],
            bins=[0, 3000, 6000, 10000],
            labels=["Low (<=3.000)", "Medium (3.001-6.000)", "High (>6.000)"]
        )
        s_order = [s for s in ["Spring", "Summer", "Fall", "Winter"] if s in daily_tier_df["season_label"].unique()]
        ct = pd.crosstab(daily_tier_df["season_label"], daily_tier_df["demand_tier"], normalize="index").reindex(s_order) * 100
        fig, ax = plt.subplots(figsize=(7, 4.2))
        ct.plot(kind="bar", stacked=True, ax=ax, color=["#E53935", "#90A4AE", "#1E88E5"], width=0.55)
        ax.set_title("Proporsi Tingkat Permintaan Harian per Musim (%)", fontsize=11.5, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("Persentase Hari (%)")
        ax.set_xticklabels(s_order, rotation=0)
        ax.set_ylim(0, 108)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, loc="upper right", fontsize=8.5)
        st.pyplot(fig)
        plt.close(fig)

st.caption("Copyright (c) 2026 - Diyanti Pratiwi | Proyek Akhir Analisis Data Dicoding")
