"""
Salla Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from semantic_layer_mocked import queries

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Salla Analytics",
    page_icon="📊",
    layout="wide"
)

# Color scheme: Black, Red, Gray only
COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_darker': '#0d0d0d', 
    'purple': '#ff4a4b',
    'orange': '#FF6B35',
    'gray_light': '#9e9e9e',
    'gray_mid': '#616161',
    'gray_dark': '#2e2e2e',
    'text': '#e0e0e0'
}

CHART_COLORS = ['#ff4a4b', '#ff6b6b', '#ff8c8c', '#ffa5a5', '#c73e1d', '#e4572e', '#f18f01', '#ffa500']

# Custom CSS
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COLORS['bg_darker']};
    }}
    
    .main {{
        background-color: {COLORS['bg_darker']};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text']};
    }}
    
    p, label, span, div {{
        color: {COLORS['text']};
    }}
    
    [data-testid="stMetricValue"] {{
        color: {COLORS['purple']};
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {COLORS['gray_light']};
    }}
    
    .stMarkdown {{
        color: {COLORS['text']};
    }}
    
    .stSelectbox label, .stSlider label {{
        color: {COLORS['text']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data(ttl=300)
def load_top_products():
    return queries.get_top_products_by_region()

@st.cache_data(ttl=300)
def load_popular_categories(top_n=10):
    return queries.get_popular_categories(top_n)

@st.cache_data(ttl=300)
def load_time_series():
    return queries.get_time_series_sales()

@st.cache_data(ttl=300)
def load_avg_sale_by_category():
    return queries.get_avg_sale_by_category()

@st.cache_data(ttl=300)
def load_top_categories_by_location(top_n=10):
    return queries.get_top_categories_by_location(top_n)

@st.cache_data(ttl=300)
def load_top_stores(top_n=10):
    return queries.get_top_stores_by_daily_sales(top_n)

@st.cache_data(ttl=300)
def load_monthly_growth():
    return queries.get_monthly_growth_by_store()

@st.cache_data(ttl=300)
def load_cohort_analysis():
    return queries.get_cohort_analysis()

# ============================================================================
# HEADER
# ============================================================================

st.title("Salla E-Commerce Analytics")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📦 Task 1: Top Products",
    "🏷️ Task 2: Popular Categories",
    "📈 Task 3: Time Series",
    "📍 Task 4: By Location",
    "🏪 Task 5: Top Stores",
    "📊 Task 6: Growth Rate",
    "👥 Task 7: Cohorts"
])

# ============================================================================
# TAB 1: TOP SELLING PRODUCTS
# ============================================================================

with tab1:
    st.header("Top Selling Products")
    st.markdown("Analyze best-performing products overall and by region")
    
    st.markdown("")
    st.markdown("")
    
    # Load data
    df = load_top_products()

    # Layout
    col1, col_right = st.columns([1, 4])
    
    # Filters for data processing
    regions = ['All Regions'] + sorted(df['customer_state'].unique().tolist())
    
    with col1:
        st.subheader("Filters")
        selected_region = st.selectbox("Select Region", regions)
        
        top_n = st.slider("Number of Products", 5, 50, 15)
        
        st.markdown("")
        st.markdown("")
    
    # Filter data
    if selected_region == 'All Regions':
        df_filtered = df.groupby('product_id').agg({
            'total_revenue': 'sum',
            'total_quantity': 'sum',
            'num_orders': 'sum'
        }).reset_index()
        region_text = "All Regions"
    else:
        df_filtered = df[df['customer_state'] == selected_region].copy()
        region_text = selected_region
    
    # Get top N
    df_top = df_filtered.nlargest(top_n, 'total_revenue').reset_index(drop=True)
    
    # Add Key Insights to filter column
    with col1:
        st.markdown("### Key Insights")
        st.markdown(f"""- Showing top {len(df_top)} products  
- Avg sales per product: SAR {df_top['total_revenue'].mean():,.0f}  
- Avg quantity per product: {df_top['total_quantity'].mean():,.0f}""")
    
    # Right column content
    with col_right:
        # Summary Statistics above charts
        st.markdown("### Summary Statistics")
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Total Sales (SAR)", f"{df_top['total_revenue'].sum():,.0f}")
        with col_metric2:
            st.metric("Total Quantity", f"{df_top['total_quantity'].sum():,.0f}")
        with col_metric3:
            st.metric("Total Orders", f"{df_top['num_orders'].sum():,.0f}")
        
        st.markdown("")
        
        # Charts in columns
        col2, col3 = st.columns(2)
    
        with col2:
            st.subheader(f"Sales Ranking - {region_text}")
            
            # Bar chart with solid purple
            df_display_top = df_top.head(20).copy()
            df_display_top['product_id_short'] = df_display_top['product_id'].apply(lambda x: x[:3] + '...')
            
            fig1 = go.Figure()
            
            fig1.add_trace(go.Bar(
                x=df_display_top['product_id_short'],
                y=df_display_top['total_revenue'],
                marker=dict(
                    color=COLORS['purple'],
                    line=dict(width=0)
                ),
                customdata=df_display_top['product_id'],
                hovertemplate='<b>Product:</b> %{customdata}<br><b>Sales:</b> SAR %{y:,.0f}<extra></extra>'
            ))
            
            fig1.update_layout(
                height=400,
                plot_bgcolor=COLORS['bg_dark'],
                paper_bgcolor=COLORS['bg_dark'],
                font=dict(color=COLORS['text']),
                xaxis=dict(
                    title='Product ID',
                    tickangle=-45,
                    gridcolor=COLORS['gray_dark'],
                    showgrid=False
                ),
                yaxis=dict(
                    title='Sales (SAR)',
                    gridcolor=COLORS['gray_dark'],
                    showgrid=True
                ),
                margin=dict(l=50, r=20, t=20, b=80)
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col3:
            st.subheader("Product Performance Analysis")
            
            # Scatter plot with solid purple
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=df_top['total_quantity'],
                y=df_top['total_revenue'],
                mode='markers',
                marker=dict(
                    size=df_top['num_orders'] / df_top['num_orders'].max() * 50 + 10,
                    color=COLORS['purple'],
                    line=dict(width=1, color=COLORS['gray_dark'])
                ),
                text=df_top['product_id'],
                hovertemplate='<b>Product:</b> %{text}<br>' +
                             '<b>Sales:</b> SAR %{y:,.0f}<br>' +
                             '<b>Quantity:</b> %{x}<br>' +
                             '<extra></extra>'
            ))
            
            fig2.update_layout(
                height=400,
                plot_bgcolor=COLORS['bg_dark'],
                paper_bgcolor=COLORS['bg_dark'],
                font=dict(color=COLORS['text']),
                xaxis=dict(
                    title='Quantity Sold',
                    gridcolor=COLORS['gray_dark'],
                    showgrid=True
                ),
                yaxis=dict(
                    title='Sales (SAR)',
                    gridcolor=COLORS['gray_dark'],
                    showgrid=True
                ),
                margin=dict(l=50, r=20, t=20, b=50)
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("")
    st.markdown("")
    
    # Detailed table
    with st.expander("📋 View Detailed Product Data"):
        df_display = df_top.copy()
        df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['total_quantity'] = df_display['total_quantity'].apply(lambda x: f"{x:,.0f}")
        df_display['num_orders'] = df_display['num_orders'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 2: POPULAR CATEGORIES
# ============================================================================

with tab2:
    st.header("Most Popular Product Categories")
    st.markdown("Analyze category performance based on sales and order volume")
    
    st.markdown("")
    st.markdown("")
    
    # Load data
    top_n_categories = st.slider("Show Top N Categories:", 5, 25, 12, key='top_n_categories')
    df_categories = load_popular_categories(top_n_categories)
    
    # Metrics
    st.markdown("### Summary Statistics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric("Total Sales (SAR)", f"{df_categories['total_revenue'].sum():,.0f}")
    with metric_cols[1]:
        st.metric("Orders", f"{df_categories['num_orders'].sum():,.0f}")
    with metric_cols[2]:
        st.metric("Units Sold", f"{df_categories['total_quantity'].sum():,.0f}")
    with metric_cols[3]:
        st.metric("Products", f"{df_categories['num_unique_products'].sum():,.0f}")
    
    st.markdown("")
    st.markdown("")
    
    # Visualizations side by side
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.subheader("Sales by Category")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_categories['product_category_name'],
            x=df_categories['total_revenue'],
            orientation='h',
            marker=dict(color=COLORS['purple']),
            hovertemplate='<b>%{y}</b><br>Sales: SAR %{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            height=500,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Sales (SAR)", showgrid=True, gridcolor=COLORS['gray_dark']),
            yaxis=dict(title="", categoryorder='total ascending'),
            margin=dict(l=150, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with viz_col2:
        st.subheader("Order Volume by Category")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            y=df_categories['product_category_name'],
            x=df_categories['num_orders'],
            orientation='h',
            marker=dict(color=COLORS['purple']),
            hovertemplate='<b>%{y}</b><br>Orders: %{x:,.0f}<extra></extra>'
        ))
        
        fig2.update_layout(
            height=500,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Number of Orders", showgrid=True, gridcolor=COLORS['gray_dark']),
            yaxis=dict(title="", categoryorder='total ascending'),
            margin=dict(l=150, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed data table
    st.markdown("")
    with st.expander("📋 View Detailed Data Table"):
        df_display = df_categories.copy()
        df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['total_quantity'] = df_display['total_quantity'].apply(lambda x: f"{x:,.0f}")
        df_display['num_orders'] = df_display['num_orders'].apply(lambda x: f"{x:,.0f}")
        df_display['num_unique_products'] = df_display['num_unique_products'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 3: TIME SERIES SALES
# ============================================================================

with tab3:
    st.header("Sales Trends Over Time")
    st.markdown("Analyze monthly, quarterly, and yearly sales performance")
    
    st.markdown("")
    st.markdown("")
    
    # Load data
    df_time = load_time_series()
    
    # Time period selector
    time_period = st.radio(
        "Select Time Period:",
        ['Monthly', 'Quarterly', 'Yearly'],
        horizontal=True
    )
    
    st.markdown("")
    
    # Aggregate data based on selection
    if time_period == 'Monthly':
        df_agg = df_time.groupby('year_month').agg({
            'total_revenue': 'sum',
            'total_quantity': 'sum',
            'num_orders': 'sum'
        }).reset_index()
        x_col, x_label = 'year_month', 'Month'
    elif time_period == 'Quarterly':
        df_agg = df_time.groupby('year_quarter').agg({
            'total_revenue': 'sum',
            'total_quantity': 'sum',
            'num_orders': 'sum'
        }).reset_index()
        x_col, x_label = 'year_quarter', 'Quarter'
    else:
        df_agg = df_time.groupby('year').agg({
            'total_revenue': 'sum',
            'total_quantity': 'sum',
            'num_orders': 'sum'
        }).reset_index()
        x_col, x_label = 'year', 'Year'
    
    # Summary Statistics
    st.markdown("### Summary Statistics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric("Total Sales (SAR)", f"{df_agg['total_revenue'].sum():,.0f}")
    with metric_cols[1]:
        st.metric("Total Orders", f"{df_agg['num_orders'].sum():,.0f}")
    with metric_cols[2]:
        st.metric("Units Sold", f"{df_agg['total_quantity'].sum():,.0f}")
    with metric_cols[3]:
        avg_order = df_agg['total_revenue'].sum() / df_agg['num_orders'].sum()
        st.metric("Avg Order Value (SAR)", f"{avg_order:,.0f}")
    
    st.markdown("")
    st.markdown("")
    
    # Main time series chart
    st.subheader(f"{time_period} Sales Trend")
    
    fig = go.Figure()
    
    # Sales line with area fill
    fig.add_trace(go.Scatter(
        x=df_agg[x_col],
        y=df_agg['total_revenue'],
        mode='lines+markers',
        name='Sales',
        line=dict(color=COLORS['purple'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor=f"rgba(255, 74, 75, 0.1)",
        hovertemplate='<b>' + x_label + ':</b> %{x}<br><b>Sales:</b> SAR %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        height=450,
        plot_bgcolor=COLORS['bg_dark'],
        paper_bgcolor=COLORS['bg_dark'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            title=x_label,
            showgrid=False
        ),
        yaxis=dict(
            title='Sales (SAR)',
            showgrid=True,
            gridcolor=COLORS['gray_dark']
        ),
        margin=dict(l=60, r=20, t=20, b=60),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed data table
    st.markdown("")
    with st.expander("📋 View Detailed Data Table"):
        df_display = df_agg.copy()
        df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['total_quantity'] = df_display['total_quantity'].apply(lambda x: f"{x:,.0f}")
        df_display['num_orders'] = df_display['num_orders'].apply(lambda x: f"{x:,.0f}")
        if 'sales_growth' in df_display.columns:
            df_display['sales_growth'] = df_display['sales_growth'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 4: AVERAGE SALE & TOP CATEGORIES BY LOCATION
# ============================================================================

with tab4:
    st.header("Category Performance by Location")
    st.markdown("Analyze average sales by category and top categories by customer state")
    
    st.markdown("")
    st.markdown("")
    
    # Section 1: Average Sale by Category
    st.subheader("Average Sale by Product Category")
    
    st.markdown("")
    
    df_avg_sale = load_avg_sale_by_category()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Bar chart for top 15 categories
        df_top_avg = df_avg_sale.head(15)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_top_avg['product_category_name'],
            x=df_top_avg['avg_sale'],
            orientation='h',
            marker=dict(color=COLORS['purple']),
            hovertemplate='<b>%{y}</b><br>Avg Sale: SAR %{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            height=500,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Average Sale Value (SAR)", showgrid=True, gridcolor=COLORS['gray_dark']),
            yaxis=dict(title="", categoryorder='total ascending'),
            margin=dict(l=180, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Top 5 Categories**")
        st.markdown("")
        for idx, row in df_avg_sale.head(5).iterrows():
            st.metric(
                label=row['product_category_name'][:18],
                value=f"SAR {row['avg_sale']:,.0f}"
            )
    
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    
    # Section 2: Top Categories by Location
    st.subheader("Top Product Categories by State")
    
    st.markdown("")
    
    top_n_location = st.slider("Top N Categories per State:", 3, 12, 5, key='top_n_location')
    df_location = load_top_categories_by_location(top_n_location)
    
    # Heatmap
    df_pivot = df_location.pivot(
        index='product_category_name',
        columns='customer_state',
        values='total_revenue'
    ).fillna(0)
    
    fig2 = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale=[[0, COLORS['bg_dark']], [0.5, COLORS['gray_mid']], [1, COLORS['purple']]],
        hovertemplate='<b>Category:</b> %{y}<br><b>State:</b> %{x}<br><b>Sales:</b> SAR %{z:,.0f}<extra></extra>',
        colorbar=dict(
            title=dict(text='Sales (SAR)', font=dict(color=COLORS['text'])),
            tickfont=dict(color=COLORS['text'])
        )
    ))
    
    fig2.update_layout(
        height=600,
        plot_bgcolor=COLORS['bg_dark'],
        paper_bgcolor=COLORS['bg_dark'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            title='State',
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            title='Category',
            showgrid=False
        ),
        margin=dict(l=180, r=20, t=20, b=100)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("")
    st.markdown("")
    
    # State detail view
    st.subheader("State Detail View")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_state = st.selectbox(
            "Select State:",
            sorted(df_location['customer_state'].unique()),
            key='state_selector'
        )
    
    df_state = df_location[df_location['customer_state'] == selected_state].copy()
    
    with col2:
        # Bar chart for selected state
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=df_state['total_revenue'],
            y=df_state['product_category_name'],
            orientation='h',
            marker=dict(color=COLORS['purple']),
            hovertemplate='<b>%{y}</b><br>Sales: SAR %{x:,.0f}<br>Rank: %{customdata}<extra></extra>',
            customdata=df_state['rank_in_state']
        ))
        
        fig3.update_layout(
            height=400,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Sales (SAR)", showgrid=True, gridcolor=COLORS['gray_dark']),
            yaxis=dict(title="", categoryorder='total ascending'),
            margin=dict(l=180, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # Detailed data table for selected state
    st.markdown("")
    with st.expander(f"📋 View Detailed Data for {selected_state}"):
        df_display = df_state.copy()
        df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['total_quantity'] = df_display['total_quantity'].apply(lambda x: f"{x:,.0f}")
        df_display['num_orders'] = df_display['num_orders'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(
            df_display[['rank_in_state', 'product_category_name', 'total_revenue', 'total_quantity', 'num_orders']],
            use_container_width=True,
            hide_index=True
        )

# ============================================================================
# TAB 5: TOP STORES BY AVERAGE DAILY SALES
# ============================================================================

with tab5:
    st.header("Top Performing Stores")
    st.markdown("Identify highest-performing stores based on average daily sales")
    
    st.markdown("")
    st.markdown("")
    
    # Load data
    top_n_stores = st.slider("Show Top N Stores:", 5, 30, 15, key='top_n_stores')
    df_stores = load_top_stores(top_n_stores)
    
    # Summary Statistics
    st.markdown("### Summary Statistics")
    metric_cols = st.columns(5)
    
    with metric_cols[0]:
        st.metric("Stores", f"{len(df_stores)}")
    with metric_cols[1]:
        st.metric("Avg Daily Sales (SAR)", f"{df_stores['avg_daily_sales'].mean():,.0f}")
    with metric_cols[2]:
        st.metric("Total Sales (SAR)", f"{df_stores['total_revenue'].sum():,.0f}")
    with metric_cols[3]:
        st.metric("Total Orders", f"{df_stores['total_orders'].sum():,.0f}")
    with metric_cols[4]:
        st.metric("Avg Days Active", f"{df_stores['days_active'].mean():,.0f}")
    
    st.markdown("")
    st.markdown("")
    
    # Main visualizations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Average Daily Sales by Store")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_stores['seller_id'],
            x=df_stores['avg_daily_sales'],
            orientation='h',
            marker=dict(color=COLORS['purple']),
            hovertemplate='<b>Store:</b> %{y}<br><b>Avg Daily Sales:</b> SAR %{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            height=550,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Average Daily Sales (SAR)", showgrid=True, gridcolor=COLORS['gray_dark']),
            yaxis=dict(title="Store ID", categoryorder='total ascending'),
            margin=dict(l=150, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Performance Metrics")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=df_stores['days_active'],
            y=df_stores['avg_daily_sales'],
            mode='markers',
            marker=dict(
                size=df_stores['total_revenue'] / df_stores['total_revenue'].max() * 40 + 10,
                color=df_stores['total_orders'],
                colorscale=[[0, COLORS['gray_mid']], [1, COLORS['purple']]],
                showscale=True,
                colorbar=dict(
                    title=dict(text='Orders', font=dict(color=COLORS['text'])),
                    tickfont=dict(color=COLORS['text'])
                ),
                line=dict(width=1, color=COLORS['gray_dark'])
            ),
            text=df_stores['seller_id'],
            hovertemplate='<b>Store:</b> %{text}<br>' +
                         '<b>Days Active:</b> %{x}<br>' +
                         '<b>Avg Daily Sales:</b> SAR %{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
        
        fig2.update_layout(
            height=550,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Days Active", showgrid=True, gridcolor=COLORS['gray_dark']),
            yaxis=dict(title="Avg Daily Sales (SAR)", showgrid=True, gridcolor=COLORS['gray_dark']),
            margin=dict(l=60, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("")
    st.markdown("")
    
    # Analysis insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Sales Distribution")
        
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=df_stores['seller_id'],
            y=df_stores['total_revenue'],
            marker=dict(color=COLORS['purple']),
            hovertemplate='<b>Store:</b> %{x}<br><b>Total Sales:</b> SAR %{y:,.0f}<extra></extra>'
        ))
        
        fig3.update_layout(
            height=350,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Store ID", showgrid=False, tickangle=-45),
            yaxis=dict(title="Total Sales (SAR)", showgrid=True, gridcolor=COLORS['gray_dark']),
            margin=dict(l=60, r=20, t=20, b=80)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.subheader("Key Insights")
        
        st.markdown(f"""
        **Top Store Performance**  
        - Best store ID: {df_stores.iloc[0]['seller_id']}  
        - Avg daily sales: SAR {df_stores.iloc[0]['avg_daily_sales']:,.0f}  
        - Days active: {df_stores.iloc[0]['days_active']:,.0f}  
        
        **Overall Metrics**  
        - Highest total sales: SAR {df_stores['total_revenue'].max():,.0f}  
        - Most orders: {df_stores['total_orders'].max():,.0f}  
        - Most days active: {df_stores['days_active'].max():,.0f}  
        
        **Performance Correlation**  
        - Avg sales/day varies significantly across stores  
        - Store longevity (days active) doesn't always correlate with daily sales  
        - Bubble size represents total revenue in scatter plot
        """)
    
    # Detailed data table
    st.markdown("")
    with st.expander("📋 View Detailed Data Table"):
        df_display = df_stores.copy()
        df_display['avg_daily_sales'] = df_display['avg_daily_sales'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['days_active'] = df_display['days_active'].apply(lambda x: f"{x:,.0f}")
        df_display['total_orders'] = df_display['total_orders'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 6: MONTHLY GROWTH RATE BY STORE
# ============================================================================

with tab6:
    st.header("Store Growth Analysis")
    st.markdown("Track month-over-month sales growth for each store")
    
    st.markdown("")
    st.markdown("")
    
    # Load data
    df_growth = load_monthly_growth()
    
    # Summary Statistics
    st.markdown("### Summary Statistics")
    metric_cols = st.columns(5)
    
    with metric_cols[0]:
        st.metric("Stores Tracked", f"{df_growth['seller_id'].nunique():,.0f}")
    with metric_cols[1]:
        avg_growth = df_growth['growth_pct'].mean()
        st.metric("Avg Growth Rate", f"{avg_growth:.1f}%")
    with metric_cols[2]:
        median_growth = df_growth['growth_pct'].median()
        st.metric("Median Growth", f"{median_growth:.1f}%")
    with metric_cols[3]:
        positive_growth = (df_growth['growth_pct'] > 0).sum() / len(df_growth) * 100
        st.metric("Positive Growth", f"{positive_growth:.0f}%")
    with metric_cols[4]:
        max_growth = df_growth['growth_pct'].max()
        st.metric("Max Growth", f"{max_growth:.1f}%")
    
    st.markdown("")
    st.markdown("")
    
    # Store selector for trends
    st.subheader("Growth Trends - Store Comparison")
    
    top_growth_stores = df_growth.groupby('seller_id')['growth_pct'].mean().nlargest(10).index.tolist()
    
    selected_stores = st.multiselect(
        "Select stores to compare (up to 8):",
        options=sorted(df_growth['seller_id'].unique()),
        default=top_growth_stores[:5],
        max_selections=8,
        key='store_growth_selector'
    )
    
    if selected_stores:
        df_filtered = df_growth[df_growth['seller_id'].isin(selected_stores)]
        
        fig = go.Figure()
        
        for i, store in enumerate(selected_stores):
            df_store = df_filtered[df_filtered['seller_id'] == store]
            fig.add_trace(go.Scatter(
                x=df_store['month'],
                y=df_store['growth_pct'],
                name=store,
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                mode='lines+markers',
                marker=dict(size=6)
            ))
        
        fig.add_hline(y=0, line_dash="dash", line_color=COLORS['gray_light'], line_width=1)
        
        fig.update_layout(
            height=450,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Month", showgrid=False, tickangle=-45),
            yaxis=dict(title="Growth Rate (%)", showgrid=True, gridcolor=COLORS['gray_dark']),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=60, r=20, t=60, b=80)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one store to view growth trends.")
    
    st.markdown("")
    st.markdown("")
    
    # Heatmap
    st.subheader("Growth Rate Heatmap - Top 25 Stores")
    
    top_stores = df_growth.groupby('seller_id')['growth_pct'].mean().nlargest(25).index
    df_pivot = df_growth[df_growth['seller_id'].isin(top_stores)].pivot(
        index='seller_id',
        columns='month',
        values='growth_pct'
    )
    
    fig2 = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale='RdYlGn',
        zmid=0,
        hovertemplate='<b>Store:</b> %{y}<br><b>Month:</b> %{x}<br><b>Growth:</b> %{z:.1f}%<extra></extra>',
        colorbar=dict(
            title=dict(text='Growth %', font=dict(color=COLORS['text'])),
            tickfont=dict(color=COLORS['text'])
        )
    ))
    
    fig2.update_layout(
        height=600,
        plot_bgcolor=COLORS['bg_dark'],
        paper_bgcolor=COLORS['bg_dark'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            title='Month',
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            title='Store ID',
            showgrid=False
        ),
        margin=dict(l=150, r=20, t=20, b=100)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed data table
    st.markdown("")
    with st.expander("📋 View Detailed Data Table"):
        # Show data for selected stores or top 20
        if selected_stores:
            df_display = df_growth[df_growth['seller_id'].isin(selected_stores)].copy()
        else:
            df_display = df_growth[df_growth['seller_id'].isin(top_growth_stores[:20])].copy()
        
        df_display['monthly_revenue'] = df_display['monthly_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['prev_month_revenue'] = df_display['prev_month_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['growth_pct'] = df_display['growth_pct'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 7: COHORT ANALYSIS
# ============================================================================

with tab7:
    st.header("Customer Cohort Analysis")
    st.markdown("Analyze customer behavior patterns based on their first purchase month")
    
    st.markdown("")
    st.markdown("")
    
    # Load data
    df_cohort = load_cohort_analysis()
    
    # Summary Statistics
    st.markdown("### Summary Statistics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        total_customers = df_cohort[df_cohort['cohort_age'] == 0]['num_customers'].sum()
        st.metric("Total Customers", f"{total_customers:,.0f}")
    with metric_cols[1]:
        total_revenue = df_cohort['total_revenue'].sum()
        st.metric("Total Sales (SAR)", f"{total_revenue:,.0f}")
    with metric_cols[2]:
        avg_revenue_per_customer = total_revenue / total_customers if total_customers > 0 else 0
        st.metric("Avg per Customer (SAR)", f"{avg_revenue_per_customer:,.0f}")
    with metric_cols[3]:
        num_cohorts = df_cohort['cohort_month'].nunique()
        st.metric("Total Cohorts", f"{num_cohorts}")
    
    st.markdown("")
    st.markdown("")
    
    # Metric selector
    metric_type = st.radio(
        "Select Metric to Visualize:",
        ['Sales', 'Customer Count', 'Avg Sales per Customer'],
        horizontal=True
    )
    
    st.markdown("")
    
    # Pivot data based on metric
    if metric_type == 'Sales':
        df_pivot = df_cohort.pivot(
            index='cohort_month',
            columns='cohort_age',
            values='total_revenue'
        )
        title = 'Total Sales by Cohort Over Time'
        colorscale = [[0, COLORS['bg_dark']], [0.5, COLORS['gray_mid']], [1, COLORS['purple']]]
        value_format = '.0f'
    elif metric_type == 'Customer Count':
        df_pivot = df_cohort.pivot(
            index='cohort_month',
            columns='cohort_age',
            values='num_customers'
        )
        title = 'Customer Count by Cohort Over Time'
        colorscale = [[0, COLORS['bg_dark']], [0.5, COLORS['gray_mid']], [1, COLORS['purple']]]
        value_format = '.0f'
    else:  # Avg Sales per Customer
        df_pivot = df_cohort.pivot(
            index='cohort_month',
            columns='cohort_age',
            values='avg_revenue_per_customer'
        )
        title = 'Average Sales per Customer by Cohort Over Time'
        colorscale = [[0, COLORS['bg_dark']], [0.5, COLORS['gray_mid']], [1, COLORS['purple']]]
        value_format = '.0f'
    
    # Cohort heatmap
    st.subheader(title)
    
    fig1 = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale=[[0, '#ffffff'], [1, COLORS['orange']]],
        xgap=2,
        ygap=2,
        hovertemplate='<b>Cohort:</b> %{y}<br><b>Months Since First Purchase:</b> %{x}<br><b>Value:</b> %{z:' + value_format + '}<extra></extra>',
        colorbar=dict(
            title=dict(text=metric_type, font=dict(color=COLORS['text'])),
            tickfont=dict(color=COLORS['text'])
        )
    ))
    
    fig1.update_layout(
        height=600,
        plot_bgcolor=COLORS['bg_dark'],
        paper_bgcolor=COLORS['bg_dark'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            title='Months Since First Purchase',
            side="top",
            showgrid=False
        ),
        yaxis=dict(
            title='Cohort Month',
            showgrid=False
        ),
        margin=dict(l=100, r=20, t=60, b=40)
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("")
    st.markdown("")
    
    # Retention analysis
    st.subheader("Cohort Retention Rate (%)")
    
    df_retention = df_cohort.pivot(
        index='cohort_month',
        columns='cohort_age',
        values='num_customers'
    )
    
    # Calculate retention as percentage of month 0
    df_retention_pct = df_retention.div(df_retention[0], axis=0) * 100
    
    fig2 = go.Figure(data=go.Heatmap(
        z=df_retention_pct.values,
        x=df_retention_pct.columns,
        y=df_retention_pct.index,
        colorscale=[[0, '#ffffff'], [1, COLORS['orange']]],
        zmin=0,
        zmax=100,
        xgap=2,
        ygap=2,
        hovertemplate='<b>Cohort:</b> %{y}<br><b>Months Since First Purchase:</b> %{x}<br><b>Retention:</b> %{z:.1f}%<extra></extra>',
        colorbar=dict(
            title=dict(text='Retention %', font=dict(color=COLORS['text'])),
            tickfont=dict(color=COLORS['text'])
        )
    ))
    
    fig2.update_layout(
        height=600,
        plot_bgcolor=COLORS['bg_dark'],
        paper_bgcolor=COLORS['bg_dark'],
        font=dict(color=COLORS['text']),
        xaxis=dict(
            title='Months Since First Purchase',
            side="top",
            showgrid=False
        ),
        yaxis=dict(
            title='Cohort Month',
            showgrid=False
        ),
        margin=dict(l=100, r=20, t=60, b=40)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("")
    st.markdown("")
    
    # Additional analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cohort Size Distribution")
        
        df_cohort_size = df_cohort[df_cohort['cohort_age'] == 0][['cohort_month', 'num_customers']].sort_values('cohort_month')
        
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=df_cohort_size['cohort_month'],
            y=df_cohort_size['num_customers'],
            marker=dict(color=COLORS['purple']),
            hovertemplate='<b>Cohort:</b> %{x}<br><b>Customers:</b> %{y:,.0f}<extra></extra>'
        ))
        
        fig3.update_layout(
            height=400,
            plot_bgcolor=COLORS['bg_dark'],
            paper_bgcolor=COLORS['bg_dark'],
            font=dict(color=COLORS['text']),
            xaxis=dict(title="Cohort Month", showgrid=False, tickangle=-45),
            yaxis=dict(title="Number of Customers", showgrid=True, gridcolor=COLORS['gray_dark']),
            margin=dict(l=60, r=20, t=20, b=80)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.subheader("Key Insights")
        
        # Calculate some retention metrics
        if 0 in df_retention_pct.columns and 3 in df_retention_pct.columns:
            avg_retention_3m = df_retention_pct[3].mean()
        else:
            avg_retention_3m = 0
        
        if 0 in df_retention_pct.columns and 6 in df_retention_pct.columns:
            avg_retention_6m = df_retention_pct[6].mean()
        else:
            avg_retention_6m = 0
        
        st.markdown(f"""
        **Cohort Overview**  
        - Total cohorts tracked: {num_cohorts}  
        - Total customers: {total_customers:,.0f}  
        - Avg cohort size: {total_customers/num_cohorts:,.0f}  
        
        **Retention Rates**  
        - Avg 3-month retention: {avg_retention_3m:.1f}%  
        - Avg 6-month retention: {avg_retention_6m:.1f}%  
        
        **Sales Performance**  
        - Total sales: SAR {total_revenue:,.0f}  
        - Avg per customer: SAR {avg_revenue_per_customer:,.0f}  
        
        **Analysis Notes**  
        - First heatmap shows absolute values  
        - Second heatmap shows retention % relative to cohort start
        """)
    
    # Detailed data table
    st.markdown("")
    with st.expander("📋 View Detailed Cohort Data"):
        df_display = df_cohort.copy()
        df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"SAR {x:,.2f}")
        df_display['num_customers'] = df_display['num_customers'].apply(lambda x: f"{x:,.0f}")
        df_display['num_orders'] = df_display['num_orders'].apply(lambda x: f"{x:,.0f}")
        df_display['avg_revenue_per_customer'] = df_display['avg_revenue_per_customer'].apply(lambda x: f"SAR {x:,.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: {COLORS['gray_light']};'>Salla Analytics Dashboard | Data refreshes every 5 minutes</div>", unsafe_allow_html=True)
