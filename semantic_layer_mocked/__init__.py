"""
Mock Semantic Layer for Salla Analytics

This module provides a centralized interface for all business metrics and analytics queries.
It abstracts the underlying data transformations and provides clean, reusable functions.
"""

from .queries import (
    get_top_products_by_region,
    get_popular_categories,
    get_time_series_sales,
    get_avg_sale_by_category,
    get_top_categories_by_location,
    get_top_stores_by_daily_sales,
    get_monthly_growth_by_store,
    get_cohort_analysis
)

__all__ = [
    'get_top_products_by_region',
    'get_popular_categories',
    'get_time_series_sales',
    'get_avg_sale_by_category',
    'get_top_categories_by_location',
    'get_top_stores_by_daily_sales',
    'get_monthly_growth_by_store',
    'get_cohort_analysis'
]

