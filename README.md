# 🌍 Global Economic Trends Dashboard

A comprehensive interactive dashboard for visualizing macroeconomic indicators across countries using World Bank Open Data.

## Features

- 📊 **Multi-Country Comparison**: Compare GDP, inflation, and unemployment across multiple nations
- 📈 **Interactive Visualizations**: Line and bar charts with Plotly
- 🔮 **GDP Prediction**: Machine learning model to forecast next year's GDP
- 🌐 **Real-time Data**: Fetches latest data from World Bank API
- 💾 **Smart Caching**: Local caching for faster performance

## Economic Indicators

1. **GDP (Current US$)**: Gross Domestic Product
2. **Inflation Rate**: Consumer prices annual %
3. **Unemployment Rate**: Total % of labor force

## Installation

```bash
# Clone the repository
cd open-source-eval

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## How to Use

1. **Select Countries**: Choose one or more countries from the sidebar
2. **Choose Indicator**: Select GDP, Inflation, or Unemployment
3. **Set Time Range**: Pick start and end years
4. **View Charts**: Explore line charts and bar comparisons
5. **GDP Prediction**: Enable prediction to see next year's forecast

## Data Source

All data is sourced from the [World Bank Open Data API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api)

## Project Structure

```
open-source-eval/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── data/                       # Cached API responses
├── models/                     # ML models
│   └── predictor.py           # GDP prediction model
└── src/
    ├── api/
    │   └── world_bank.py      # World Bank API client
    ├── visualizations/
    │   └── charts.py          # Chart generation functions
    └── utils/
        └── helpers.py         # Utility functions
```

## Technologies Used

- **Streamlit**: Interactive web framework
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **Scikit-learn**: Machine learning for predictions
- **World Bank API**: Economic data source

## Future Enhancements

- Add more economic indicators (Trade, FDI, Debt)
- Regional comparisons (continents, income groups)
- Advanced ML models (ARIMA, Prophet)
- Export data to CSV/Excel
- Historical event annotations

## License

MIT License

---

Built with ❤️ for data enthusiasts and economic analysis
