"""
Chart generation functions using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List
def create_line_chart(
    df: pd.DataFrame,
    title: str,
    y_label: str,
    height: int = 500
) -> go.Figure:
    """
    Create an interactive line chart comparing countries over time
    
    Args:
        df: DataFrame with columns: country, year, value
        title: Chart title
        y_label: Y-axis label
        height: Chart height in pixels
        
    Returns:
        Plotly figure object
    """
    fig = px.line(
        df,
        x='year',
        y='value',
        color='country',
        markers=True,
        title=title,
        labels={
            'year': 'Year',
            'value': y_label,
            'country': 'Country'
        },
        height=height
    )
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=12),
        title_font_size=18,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            dtick=2  # Show every 2 years
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray'
        )
    )
    
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=6)
    )
    
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    year: int,
    title: str,
    y_label: str,
    height: int = 500
) -> go.Figure:
    """
    Create a bar chart comparing countries for a specific year
    
    Args:
        df: DataFrame with columns: country, year, value
        year: Year to display
        title: Chart title
        y_label: Y-axis label
        height: Chart height in pixels
        
    Returns:
        Plotly figure object
    """
    # Filter data for the specific year
    df_year = df[df['year'] == year].sort_values('value', ascending=False)
    
    fig = px.bar(
        df_year,
        x='country',
        y='value',
        color='value',
        title=f"{title} ({year})",
        labels={
            'country': 'Country',
            'value': y_label
        },
        height=height,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        template='plotly_white',
        font=dict(size=12),
        title_font_size=18,
        xaxis=dict(
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray'
        ),
        showlegend=False
    )
    
    fig.update_traces(
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5
    )
    
    return fig


def create_comparison_bar_chart(
    df: pd.DataFrame,
    years: List[int],
    title: str,
    y_label: str,
    height: int = 500
) -> go.Figure:
    """
    Create a grouped bar chart comparing countries across multiple years
    
    Args:
        df: DataFrame with columns: country, year, value
        years: List of years to compare
        title: Chart title
        y_label: Y-axis label
        height: Chart height in pixels
        
    Returns:
        Plotly figure object
    """
    # Filter data for specified years
    df_filtered = df[df['year'].isin(years)]
    
    fig = px.bar(
        df_filtered,
        x='country',
        y='value',
        color='year',
        barmode='group',
        title=title,
        labels={
            'country': 'Country',
            'value': y_label,
            'year': 'Year'
        },
        height=height,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_layout(
        template='plotly_white',
        font=dict(size=12),
        title_font_size=18,
        xaxis=dict(
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray'
        ),
        legend=dict(
            title='Year',
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_growth_rate_chart(
    df: pd.DataFrame,
    title: str,
    height: int = 500
) -> go.Figure:
    """
    Create a chart showing year-over-year growth rates
    
    Args:
        df: DataFrame with columns: country, year, value
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Plotly figure object
    """
    # Calculate growth rates
    growth_data = []
    
    for country in df['country'].unique():
        country_data = df[df['country'] == country].sort_values('year')
        country_data = country_data.copy()
        country_data['growth_rate'] = country_data['value'].pct_change() * 100
        growth_data.append(country_data)
    
    df_growth = pd.concat(growth_data, ignore_index=True)
    df_growth = df_growth.dropna(subset=['growth_rate'])
    
    fig = px.line(
        df_growth,
        x='year',
        y='growth_rate',
        color='country',
        markers=True,
        title=title,
        labels={
            'year': 'Year',
            'growth_rate': 'Growth Rate (%)',
            'country': 'Country'
        },
        height=height
    )
    
    # Add horizontal line at y=0
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="red",
        opacity=0.5,
        annotation_text="Zero Growth"
    )
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=12),
        title_font_size=18,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='red',
            zerolinewidth=1
        )
    )
    
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=6)
    )
    
    return fig


def create_prediction_chart(
    df: pd.DataFrame,
    predictions: pd.DataFrame,
    title: str,
    y_label: str,
    height: int = 500
) -> go.Figure:
    """
    Create a chart showing historical data with predictions
    
    Args:
        df: DataFrame with historical data (country, year, value)
        predictions: DataFrame with predictions (country, year, value)
        title: Chart title
        y_label: Y-axis label
        height: Chart height in pixels
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add historical data
    for country in df['country'].unique():
        country_data = df[df['country'] == country].sort_values('year')
        
        fig.add_trace(go.Scatter(
            x=country_data['year'],
            y=country_data['value'],
            mode='lines+markers',
            name=f"{country} (Historical)",
            line=dict(width=2.5),
            marker=dict(size=6)
        ))
    
    # Add predictions
    for country in predictions['country'].unique():
        pred_data = predictions[predictions['country'] == country]
        
        fig.add_trace(go.Scatter(
            x=pred_data['year'],
            y=pred_data['value'],
            mode='lines+markers',
            name=f"{country} (Predicted)",
            line=dict(width=2.5, dash='dash'),
            marker=dict(size=8, symbol='star')
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Year',
        yaxis_title=y_label,
        height=height,
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=12),
        title_font_size=18,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray'
        )
    )
    
    return fig
