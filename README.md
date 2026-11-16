# Bike Sharing Analytics Dashboard 🚲

Proyek Akhir Analisis Data menggunakan **Bike Sharing Dataset** (Capital Bikeshare 2011–2012) yang mencakup proses *Data Wrangling*, *Exploratory Data Analysis (EDA)*, *Explanatory Visualization*, *Rule-Based Clustering (Manual Grouping & Binning)*, serta *Interactive Dashboard* berbasis Streamlit.

## Struktur Direktori
```text
submission
├── dashboard
│   ├── dashboard.py
│   └── main_data.csv
├── data
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment - Anaconda
```bash
conda create --name bike-ds python=3.10
conda activate bike-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
cd submission
python -m venv venv
source venv/bin/activate  # Untuk Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run Streamlit App
```bash
streamlit run dashboard/dashboard.py
```
