"""
Industry Templates Package
Dynamic loading of industry-specific ABAC templates
"""

import importlib
import os
from pathlib import Path

def get_available_industries():
    """Get list of available industry templates"""
    industries_dir = Path(__file__).parent
    industry_files = [f.stem.replace('_template', '') for f in industries_dir.glob('*_template.py')]
    return [i.capitalize() for i in industry_files]

def load_industry_template(industry_name):
    """
    Dynamically load industry template module
    
    Args:
        industry_name: Name of industry (e.g., "Finance", "Healthcare")
    
    Returns:
        Module containing FUNCTIONS_SQL, TAG_DEFINITIONS, ABAC_POLICIES_SQL, etc.
    """
    module_name = f"{industry_name.lower()}_template"
    try:
        module = importlib.import_module(f"industries.{module_name}")
        return module
    except ImportError:
        raise ValueError(f"Industry template '{industry_name}' not found")

# Export for easy access
__all__ = ['get_available_industries', 'load_industry_template']

