"""
Global Economic Trends Dashboard
Interactive Streamlit application for visualizing macroeconomic indicators
"""
import streamlit as st
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
from utils.explanations import generate_explanations
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
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Use pointer cursor for dropdowns (select/multiselect) */
    div[data-baseweb="select"],
    div[data-baseweb="select"] * {
        cursor: pointer !important;
    }
    /* Hide anchor-link icon shown on heading hover */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
    /* Hide default Streamlit footer and hamburger menu */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_data(indicator_key, countries, start_year, end_year):
    """Fetch and cache data from World Bank API"""
    cache_key = f"{indicator_key}_{'_'.join(countries)}_{start_year}_{end_year}"
    
    # Try loading from cache
    cached_data = load_data_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Fetch fresh data using the new generic method
    data = wb_api.fetch_by_indicator_key(indicator_key, countries, start_year, end_year)
    
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
    default_countries = ['IND']
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
    
    # Category selection
    category = st.sidebar.selectbox(
        "Choose Category:",
        options=list(wb_api.INDICATOR_CATEGORIES.keys()),
        help="Select a data category to explore"
    )
    
    # Get indicators for selected category
    available_indicators = wb_api.INDICATOR_CATEGORIES[category]
    
    # Indicator selection within category
    indicator_name = st.sidebar.selectbox(
        "Choose Indicator:",
        options=list(available_indicators.keys()),
        help="Select the specific indicator to visualize"
    )
    
    # Get the indicator key for API calls
    indicator_key = available_indicators[indicator_name]
    
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
    if indicator_key == "gdp":
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
        
        # Show category information
        st.markdown("### 📚 Available Data Categories")
        
        cols = st.columns(3)
        categories_list = list(wb_api.INDICATOR_CATEGORIES.keys())
        
        for idx, cat in enumerate(categories_list):
            with cols[idx % 3]:
                indicator_count = len(wb_api.INDICATOR_CATEGORIES[cat])
                st.markdown(f"**{cat}**")
                st.write(f"{indicator_count} indicators available")
        
        st.markdown("---")
        st.markdown(f"### 🌍 Total Available Data")
        st.markdown(f"- **{len(wb_api.INDICATOR_CATEGORIES)} Categories**")
        st.markdown(f"- **{len(wb_api.INDICATORS)} Indicators**")
        st.markdown(f"- **{len(wb_api.POPULAR_COUNTRIES)} Countries**")
        
        st.stop()
    
    # Load data
    with st.spinner(f"Fetching {indicator_name} data from World Bank..."):
        df = fetch_data(indicator_key, selected_country_codes, start_year, end_year)
    
    if df.empty:
        st.error("❌ No data available for the selected parameters. Try different countries or years.")
        st.stop()
    
    # Display metrics
    st.header(f" {indicator_name}")
    st.markdown(f"**Category:** {category}")
    st.markdown("---")
    
    # Latest values
    latest = get_latest_values(df)
    
    # Create metric cards
    cols = st.columns(min(len(selected_country_codes), 4))
    for idx, (_, row) in enumerate(latest.iterrows()):
        with cols[idx % 4]:
            # Smart formatting based on indicator type
            if 'pct' in indicator_key or 'rate' in indicator_key or 'growth' in indicator_key:
                value_str = format_percentage(row['value'])
            elif 'population' in indicator_key or 'gdp' in indicator_key or 'gni' in indicator_key:
                value_str = format_large_number(row['value'])
            else:
                value_str = f"{row['value']:,.2f}"
            
            st.metric(
                label=f"{row['country']} ({int(row['year'])})",
                value=value_str
            )
    
    # Main visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Statistics", "🔍 Analysis", "📥 Data"])
    
    with tab1:
        st.subheader(f"{indicator_name} Over Time")
        
        # Determine appropriate y-axis label
        y_label = indicator_name
        
        fig_line = create_line_chart(
            df,
            f"{indicator_name} Trends ({start_year}-{end_year})",
            y_label,
            height=500
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Generate dip/rise explanations (only render if significant moves found)
        with st.spinner("Analyzing movements..."):
            explanations = generate_explanations(
                df, indicator_key, top_n=2, min_abs_change_pct=5.0
            )
        if explanations:
            st.markdown("### 📉📈 Dips & Rises: Contextual Explanations")
            for exp in explanations:
                st.markdown(f"- {exp}")
        
        # Growth rates
        if show_growth:
            st.subheader("Year-over-Year Growth Rates")
            fig_growth = create_growth_rate_chart(
                df,
                f"{indicator_name} Growth Rate ({start_year}-{end_year})",
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
                    f"{indicator_name} Comparison",
                    y_label,
                    height=450
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
    
    with tab2:
        st.subheader("Statistical Summary")
        
        # Calculate statistics
        stats = calculate_statistics(df)
        
        # Smart formatting based on indicator type
        if 'pct' in indicator_key or 'rate' in indicator_key or 'growth' in indicator_key:
            for col in ['mean', 'median', 'min', 'max', 'std', 'latest']:
                stats[col] = stats[col].apply(lambda x: f"{x:.2f}%")
        elif 'population' in indicator_key or 'gdp' in indicator_key or 'gni' in indicator_key:
            for col in ['mean', 'median', 'min', 'max', 'latest']:
                stats[col] = stats[col].apply(format_large_number)
            stats['std'] = stats['std'].apply(lambda x: format_large_number(x, 1))
        else:
            for col in ['mean', 'median', 'min', 'max', 'std', 'latest']:
                stats[col] = stats[col].apply(lambda x: f"{x:,.2f}")
        
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
            if 'population' in indicator_key or 'gdp' in indicator_key or 'gni' in indicator_key:
                cagr_display['start_value'] = cagr_display['start_value'].apply(format_large_number)
                cagr_display['end_value'] = cagr_display['end_value'].apply(format_large_number)
            else:
                cagr_display['start_value'] = cagr_display['start_value'].apply(lambda x: f"{x:,.2f}")
                cagr_display['end_value'] = cagr_display['end_value'].apply(lambda x: f"{x:,.2f}")
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
        if indicator_key == "gdp" and show_prediction:
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
            
            st.markdown(f"#### Top Countries by {indicator_name} ({int(latest_year)})")
            
            fig_ranking = create_bar_chart(
                df,
                latest_year,
                f"{indicator_name} Rankings",
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
                "value": indicator_name
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"{indicator_key}_{start_year}_{end_year}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            Data source: <a href='https://data.worldbank.org/' target='_blank'>World Bank Open Data</a>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
