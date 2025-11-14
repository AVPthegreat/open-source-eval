"""
Utility functions for data processing and formatting
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Optional


def format_large_number(value: float, precision: int = 2) -> str:
    """
    Format large numbers with appropriate suffixes
    
    Args:
        value: Number to format
        precision: Decimal places
        
    Returns:
        Formatted string (e.g., "1.23T", "456.78B")
    """
    if pd.isna(value):
        return "N/A"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1e12:
        return f"{sign}{abs_value/1e12:.{precision}f}T"
    elif abs_value >= 1e9:
        return f"{sign}{abs_value/1e9:.{precision}f}B"
    elif abs_value >= 1e6:
        return f"{sign}{abs_value/1e6:.{precision}f}M"
    elif abs_value >= 1e3:
        return f"{sign}{abs_value/1e3:.{precision}f}K"
    else:
        return f"{sign}{abs_value:.{precision}f}"


def format_percentage(value: float, precision: int = 2) -> str:
    """
    Format percentage values
    
    Args:
        value: Percentage value
        precision: Decimal places
        
    Returns:
        Formatted string (e.g., "3.45%")
    """
    if pd.isna(value):
        return "N/A"
    return f"{value:.{precision}f}%"


def calculate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate summary statistics for each country
    
    Args:
        df: DataFrame with columns: country, year, value
        
    Returns:
        DataFrame with statistics by country
    """
    stats = df.groupby('country')['value'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('min', 'min'),
        ('max', 'max'),
        ('std', 'std'),
        ('latest', 'last')
    ]).reset_index()
    
    return stats


def calculate_growth_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate year-over-year growth rates
    
    Args:
        df: DataFrame with columns: country, year, value
        
    Returns:
        DataFrame with growth_rate column added
    """
    df = df.sort_values(['country', 'year'])
    df['growth_rate'] = df.groupby('country')['value'].pct_change() * 100
    return df


def calculate_cagr(
    df: pd.DataFrame,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None
) -> pd.DataFrame:
    """
    Calculate Compound Annual Growth Rate (CAGR) for each country
    
    Args:
        df: DataFrame with columns: country, year, value
        start_year: Starting year (if None, uses min year)
        end_year: Ending year (if None, uses max year)
        
    Returns:
        DataFrame with CAGR by country
    """
    results = []
    
    for country in df['country'].unique():
        country_data = df[df['country'] == country].sort_values('year')
        
        if start_year:
            start_data = country_data[country_data['year'] == start_year]
        else:
            start_data = country_data.iloc[[0]]
        
        if end_year:
            end_data = country_data[country_data['year'] == end_year]
        else:
            end_data = country_data.iloc[[-1]]
        
        if len(start_data) == 0 or len(end_data) == 0:
            continue
        
        start_val = start_data['value'].iloc[0]
        end_val = end_data['value'].iloc[0]
        start_yr = start_data['year'].iloc[0]
        end_yr = end_data['year'].iloc[0]
        
        years = end_yr - start_yr
        
        if years > 0 and start_val > 0:
            cagr = ((end_val / start_val) ** (1 / years) - 1) * 100
            results.append({
                'country': country,
                'start_year': start_yr,
                'end_year': end_yr,
                'start_value': start_val,
                'end_value': end_val,
                'cagr': cagr
            })
    
    return pd.DataFrame(results)


def save_data_cache(data: pd.DataFrame, filename: str, cache_dir: str = "data"):
    """
    Save data to cache as JSON
    
    Args:
        data: DataFrame to cache
        filename: Cache filename
        cache_dir: Cache directory
    """
    os.makedirs(cache_dir, exist_ok=True)
    filepath = os.path.join(cache_dir, f"{filename}.json")
    
    # Add timestamp
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'data': data.to_dict(orient='records')
    }
    
    with open(filepath, 'w') as f:
        json.dump(cache_data, f, indent=2)


def load_data_cache(
    filename: str,
    cache_dir: str = "data",
    max_age_hours: int = 24
) -> Optional[pd.DataFrame]:
    """
    Load data from cache if it exists and is recent
    
    Args:
        filename: Cache filename
        cache_dir: Cache directory
        max_age_hours: Maximum age of cache in hours
        
    Returns:
        DataFrame if cache is valid, None otherwise
    """
    filepath = os.path.join(cache_dir, f"{filename}.json")
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r') as f:
            cache_data = json.load(f)
        
        # Check cache age
        cache_time = datetime.fromisoformat(cache_data['timestamp'])
        age_hours = (datetime.now() - cache_time).total_seconds() / 3600
        
        if age_hours > max_age_hours:
            return None
        
        return pd.DataFrame(cache_data['data'])
    
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None


def get_year_range(df: pd.DataFrame) -> tuple:
    """
    Get the min and max years from the dataset
    
    Args:
        df: DataFrame with year column
        
    Returns:
        Tuple of (min_year, max_year)
    """
    if df.empty or 'year' not in df.columns:
        return (2000, 2023)
    
    return (int(df['year'].min()), int(df['year'].max()))


def prepare_download_data(df: pd.DataFrame, indicator_name: str) -> pd.DataFrame:
    """
    Prepare data for CSV download with proper formatting
    
    Args:
        df: DataFrame to prepare
        indicator_name: Name of the indicator
        
    Returns:
        Formatted DataFrame
    """
    df_download = df.copy()
    df_download = df_download.rename(columns={
        'country': 'Country',
        'country_code': 'Country Code',
        'year': 'Year',
        'value': indicator_name
    })
    
    return df_download.sort_values(['Country', 'Year'])


def get_latest_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get the most recent value for each country
    
    Args:
        df: DataFrame with columns: country, year, value
        
    Returns:
        DataFrame with latest values
    """
    latest = df.sort_values('year').groupby('country').tail(1)
    return latest.sort_values('value', ascending=False)


def compare_countries(
    df: pd.DataFrame,
    country1: str,
    country2: str
) -> dict:
    """
    Compare statistics between two countries
    
    Args:
        df: DataFrame with data
        country1: First country name
        country2: Second country name
        
    Returns:
        Dictionary with comparison metrics
    """
    data1 = df[df['country'] == country1]
    data2 = df[df['country'] == country2]
    
    if data1.empty or data2.empty:
        return {}
    
    return {
        'country1': country1,
        'country2': country2,
        'mean_diff': data1['value'].mean() - data2['value'].mean(),
        'median_diff': data1['value'].median() - data2['value'].median(),
        'latest_diff': data1['value'].iloc[-1] - data2['value'].iloc[-1],
        'correlation': data1['value'].corr(data2['value']) if len(data1) == len(data2) else None
    }
