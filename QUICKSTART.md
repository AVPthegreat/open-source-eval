# Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

## 📱 How to Use

### Basic Usage:

1. **Select Countries**: In the sidebar, choose countries from the dropdown (USA, China, India, etc.)
2. **Choose Indicator**: Select GDP, Inflation, or Unemployment
3. **Set Time Range**: Use the slider to select years (1960-2023)
4. **Load Data**: Click the "Load Data" button
5. **Explore**: Navigate through different tabs to view trends, statistics, and analysis

### Advanced Features:

- **Growth Rates**: Enable to see year-over-year changes
- **Year Comparison**: Compare specific years side-by-side
- **GDP Prediction**: (GDP only) Enable ML-based forecasting for next year
- **Download Data**: Export data as CSV from the Data tab

## 🎯 Features Overview

### 📊 Trends Tab
- Interactive line charts showing historical trends
- Multiple countries comparison
- Growth rate visualization
- Multi-year bar chart comparison

### 📊 Statistics Tab
- Summary statistics (mean, median, min, max)
- Compound Annual Growth Rate (CAGR)
- Standard deviation analysis

### 🔍 Analysis Tab
- GDP predictions using linear regression
- Model performance metrics
- Country rankings
- Prediction confidence intervals

### 📥 Data Tab
- Raw data table
- CSV export functionality
- Full dataset access

## 💡 Tips

- Start with 3-5 countries for better visualization
- Use GDP for prediction features
- Data is cached for 24 hours for faster loading
- Hover over charts for detailed information
- Use the year slider to focus on specific periods

## 🐛 Troubleshooting

**No data showing?**
- Check your internet connection (API requires online access)
- Try different year ranges
- Some countries may have limited data for certain indicators

**Slow loading?**
- First load will be slower (fetching from API)
- Subsequent loads use cached data
- Select fewer countries or shorter time ranges

## 🌟 Example Use Cases

1. **Compare BRICS nations**: Select Brazil, Russia, India, China, South Africa
2. **G7 Analysis**: USA, Japan, Germany, UK, France, Italy, Canada
3. **Emerging Markets**: India, Indonesia, Turkey, Mexico, Brazil
4. **Historical Comparison**: Set range to 1980-2023 to see long-term trends

Enjoy exploring global economic trends! 🌍
