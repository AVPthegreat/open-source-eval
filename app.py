"""
Global Economic Trends Dashboard
Interactive Streamlit application for visualizing macroeconomic indicators
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from api.world_bank import wb_api
from visualizations.charts import (
    create_line_chart,
    create_bar_chart,
    create_comparison_bar_chart,
    create_growth_rate_chart,
    create_prediction_chart
)
from utils.helpers import (
    format_large_number,
    format_percentage,
    calculate_statistics,
    calculate_cagr,
    get_latest_values,
    save_data_cache,
    load_data_cache
)
from models.predictor import gdp_predictor


# Page configuration
st.set_page_config(
    page_title="Global Economic Trends Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_data(indicator, countries, start_year, end_year):
    """Fetch and cache data from World Bank API"""
    cache_key = f"{indicator}_{'_'.join(countries)}_{start_year}_{end_year}"
    
    # Try loading from cache
    cached_data = load_data_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Fetch fresh data
    if indicator == "GDP":
        data = wb_api.fetch_gdp(countries, start_year, end_year)
    elif indicator == "Inflation":
        data = wb_api.fetch_inflation(countries, start_year, end_year)
    elif indicator == "Unemployment":
        data = wb_api.fetch_unemployment(countries, start_year, end_year)
    else:
        return pd.DataFrame()
    
    # Save to cache
    if not data.empty:
        save_data_cache(data, cache_key)
    
    return data


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">🌍 Global Economic Trends Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Visualize and analyze macroeconomic indicators across countries</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Country selection
    st.sidebar.subheader("Select Countries")
    
    # Get available countries
    all_countries = wb_api.POPULAR_COUNTRIES
    
    # Country selection with popular defaults
    default_countries = ['USA', 'CHN', 'IND', 'DEU', 'JPN']
    selected_country_codes = st.sidebar.multiselect(
        "Choose countries to compare:",
        options=list(all_countries.keys()),
        default=default_countries,
        format_func=lambda x: f"{all_countries[x]} ({x})"
    )
    
    if not selected_country_codes:
        st.warning("⚠️ Please select at least one country from the sidebar.")
        st.stop()
    
    # Indicator selection
    st.sidebar.subheader("Select Indicator")
    indicator = st.sidebar.selectbox(
        "Economic Indicator:",
        ["GDP", "Inflation", "Unemployment"],
        help="""
        - GDP: Gross Domestic Product (current US$)
        - Inflation: Consumer prices annual %
        - Unemployment: % of total labor force
        """
    )
    
    # Year range
    st.sidebar.subheader("Time Period")
    current_year = datetime.now().year
    year_range = st.sidebar.slider(
        "Select year range:",
        min_value=1960,
        max_value=current_year - 1,
        value=(2000, current_year - 1),
        step=1
    )
    
    start_year, end_year = year_range
    
    # Visualization options
    st.sidebar.subheader("Visualization Options")
    show_growth = st.sidebar.checkbox("Show Growth Rates", value=False)
    show_comparison = st.sidebar.checkbox("Year Comparison", value=False)
    
    # Prediction options (only for GDP)
    show_prediction = False
    if indicator == "GDP":
        st.sidebar.subheader("🔮 Prediction")
        show_prediction = st.sidebar.checkbox("Enable GDP Prediction", value=False)
    
    # Fetch data button
    if st.sidebar.button("📊 Load Data", type="primary"):
        st.session_state['data_loaded'] = True
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state['data_loaded'] = False
    
    # Main content
    if not st.session_state['data_loaded']:
        st.info("👈 Configure your settings in the sidebar and click 'Load Data' to begin.")
        
        # Show some information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📈 GDP")
            st.write("Gross Domestic Product measures the total economic output of a country.")
        
        with col2:
            st.markdown("### 💹 Inflation")
            st.write("Annual percentage change in consumer prices, indicating purchasing power.")
        
        with col3:
            st.markdown("### 👥 Unemployment")
            st.write("Percentage of labor force that is jobless and seeking employment.")
        
        st.stop()
    
    # Load data
    with st.spinner(f"Fetching {indicator} data from World Bank..."):
        df = fetch_data(indicator, selected_country_codes, start_year, end_year)
    
    if df.empty:
        st.error("❌ No data available for the selected parameters. Try different countries or years.")
        st.stop()
    
    # Display metrics
    st.header(f"📊 {indicator} Analysis")
    
    # Latest values
    latest = get_latest_values(df)
    
    # Create metric cards
    cols = st.columns(min(len(selected_country_codes), 4))
    for idx, (_, row) in enumerate(latest.iterrows()):
        with cols[idx % 4]:
            if indicator == "GDP":
                value_str = format_large_number(row['value'])
            else:
                value_str = format_percentage(row['value'])
            
            st.metric(
                label=f"{row['country']} ({int(row['year'])})",
                value=value_str
            )
    
    # Main visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Statistics", "🔍 Analysis", "📥 Data"])
    
    with tab1:
        st.subheader(f"{indicator} Over Time")
        
        # Line chart
        if indicator == "GDP":
            y_label = "GDP (Current US$)"
        elif indicator == "Inflation":
            y_label = "Inflation Rate (%)"
        else:
            y_label = "Unemployment Rate (%)"
        
        fig_line = create_line_chart(
            df,
            f"{indicator} Trends ({start_year}-{end_year})",
            y_label,
            height=500
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Growth rates
        if show_growth:
            st.subheader("Year-over-Year Growth Rates")
            fig_growth = create_growth_rate_chart(
                df,
                f"{indicator} Growth Rate ({start_year}-{end_year})",
                height=450
            )
            st.plotly_chart(fig_growth, use_container_width=True)
        
        # Year comparison
        if show_comparison:
            st.subheader("Multi-Year Comparison")
            available_years = sorted(df['year'].unique())
            
            # Select comparison years
            comparison_years = st.multiselect(
                "Select years to compare:",
                options=available_years,
                default=available_years[-3:] if len(available_years) >= 3 else available_years
            )
            
            if comparison_years:
                fig_comparison = create_comparison_bar_chart(
                    df,
                    comparison_years,
                    f"{indicator} Comparison",
                    y_label,
                    height=450
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
    
    with tab2:
        st.subheader("Statistical Summary")
        
        # Calculate statistics
        stats = calculate_statistics(df)
        
        # Format statistics based on indicator
        if indicator == "GDP":
            for col in ['mean', 'median', 'min', 'max', 'latest']:
                stats[col] = stats[col].apply(format_large_number)
            stats['std'] = stats['std'].apply(lambda x: format_large_number(x, 1))
        else:
            for col in ['mean', 'median', 'min', 'max', 'std', 'latest']:
                stats[col] = stats[col].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(
            stats,
            column_config={
                "country": "Country",
                "mean": "Average",
                "median": "Median",
                "min": "Minimum",
                "max": "Maximum",
                "std": "Std Dev",
                "latest": "Latest Value"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # CAGR calculation
        st.subheader("Compound Annual Growth Rate (CAGR)")
        cagr_df = calculate_cagr(df)
        
        if not cagr_df.empty:
            cagr_display = cagr_df.copy()
            if indicator == "GDP":
                cagr_display['start_value'] = cagr_display['start_value'].apply(format_large_number)
                cagr_display['end_value'] = cagr_display['end_value'].apply(format_large_number)
            cagr_display['cagr'] = cagr_display['cagr'].apply(lambda x: f"{x:.2f}%")
            
            st.dataframe(
                cagr_display,
                column_config={
                    "country": "Country",
                    "start_year": "Start Year",
                    "end_year": "End Year",
                    "start_value": "Start Value",
                    "end_value": "End Value",
                    "cagr": "CAGR"
                },
                hide_index=True,
                use_container_width=True
            )
    
    with tab3:
        if indicator == "GDP" and show_prediction:
            st.subheader("🔮 GDP Prediction Model")
            
            # Train predictor
            with st.spinner("Training prediction model..."):
                metrics = gdp_predictor.train(df)
            
            # Predict next year
            predictions = gdp_predictor.predict_next_year(df)
            
            if not predictions.empty:
                # Show predictions
                st.markdown("### Next Year Predictions")
                
                pred_cols = st.columns(min(len(predictions), 4))
                for idx, (_, row) in enumerate(predictions.iterrows()):
                    with pred_cols[idx % 4]:
                        st.metric(
                            label=f"{row['country']} ({int(row['year'])})",
                            value=format_large_number(row['value']),
                            delta="Predicted"
                        )
                
                # Visualization with predictions
                st.markdown("### Historical Data with Predictions")
                fig_pred = create_prediction_chart(
                    df,
                    predictions,
                    "GDP with Next Year Prediction",
                    "GDP (Current US$)",
                    height=500
                )
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # Model details
                st.markdown("### Model Performance")
                
                selected_country_for_details = st.selectbox(
                    "Select country to view model details:",
                    options=list(metrics.keys())
                )
                
                if selected_country_for_details:
                    st.markdown(gdp_predictor.get_model_summary(selected_country_for_details))
        else:
            st.subheader("Country Rankings")
            
            # Latest year ranking
            latest_year = df['year'].max()
            ranking = df[df['year'] == latest_year].sort_values('value', ascending=False)
            
            st.markdown(f"#### Top Countries by {indicator} ({int(latest_year)})")
            
            fig_ranking = create_bar_chart(
                df,
                latest_year,
                f"{indicator} Rankings",
                y_label,
                height=450
            )
            st.plotly_chart(fig_ranking, use_container_width=True)
    
    with tab4:
        st.subheader("Raw Data")
        
        # Display data table
        st.dataframe(
            df.sort_values(['country', 'year']),
            column_config={
                "country": "Country",
                "country_code": "Code",
                "year": "Year",
                "value": indicator
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"{indicator}_{start_year}_{end_year}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            Data source: <a href='https://data.worldbank.org/' target='_blank'>World Bank Open Data</a> | 
            Built with ❤️ using Streamlit
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
