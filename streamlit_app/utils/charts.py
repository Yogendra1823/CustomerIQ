import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st

def plot_segment_donut(df_segments: pd.DataFrame):
    """
    Generate a Plotly Donut Chart of the segment distribution.
    """
    fig = px.pie(
        df_segments,
        values="size",
        names="name",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_revenue_bar(df_segments: pd.DataFrame):
    """
    Generate a Plotly Horizontal Bar Chart of segment revenue share.
    """
    df_sorted = df_segments.sort_values(by="revenue_share", ascending=True)
    fig = px.bar(
        df_sorted,
        x="revenue_share",
        y="name",
        orientation="h",
        color="name",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(
        xaxis_title="Revenue Share (%)",
        yaxis_title="",
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_pca_scatter_2d(df_pca: pd.DataFrame):
    """
    Generate a 2D PCA scatter plot.
    """
    fig = px.scatter(
        df_pca,
        x="PC1",
        y="PC2",
        color="Segment",
        hover_data=["ID"],
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_pca_scatter_3d(df_pca: pd.DataFrame):
    """
    Generate a 3D PCA scatter plot.
    """
    fig = px.scatter_3d(
        df_pca,
        x="PC1",
        y="PC2",
        z="PC3",
        color="Segment",
        hover_data=["ID"],
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_rfm_scatter_3d(df_customers: pd.DataFrame):
    """
    Generate a 3D scatter plot of RFM (Recency, Frequency, Monetary).
    """
    # Sample 1000 for smooth rendering
    df_sample = df_customers.sample(n=min(1000, len(df_customers)), random_state=42)
    fig = px.scatter_3d(
        df_sample,
        x="days_since_last_purchase",
        y="purchase_frequency",
        z="total_spend",
        color="segment_name",
        hover_data=["external_id"],
        color_discrete_sequence=px.colors.qualitative.Safe,
        labels={
            "days_since_last_purchase": "Recency (Days)",
            "purchase_frequency": "Frequency (Orders)",
            "total_spend": "Monetary (Spend)"
        }
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_cohort_heatmap(cohort_matrix: pd.DataFrame):
    """
    Plot cohort retention heatmap.
    """
    fig = go.Figure(data=go.Heatmap(
        z=cohort_matrix.values,
        x=cohort_matrix.columns,
        y=cohort_matrix.index,
        colorscale='Blues',
        text=[[f"{val*100:.1f}%" if not np.isnan(val) else "" for val in row] for row in cohort_matrix.values],
        texttemplate="%{text}",
        hoverongaps=False
    ))
    fig.update_layout(
        xaxis_title="Months Since First Order",
        yaxis_title="Cohort Month",
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig
