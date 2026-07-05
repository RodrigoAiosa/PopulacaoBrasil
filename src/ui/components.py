"""
Componentes UI reutilizáveis
"""
import streamlit as st
from typing import Optional, Dict, Any

from src.utils.constants import THEME_COLORS


def inject_css(css_file: Optional[str] = None, custom_css: Optional[str] = None):
    """
    Injeta CSS no aplicativo
    """
    css = ""
    
    if css_file:
        with open(css_file, "r") as f:
            css += f.read()
    
    if custom_css:
        css += custom_css
    
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_card(
    label: str,
    value: str,
    unit: str = "",
    foot: str = "",
    color: Optional[str] = None
):
    """
    Renderiza um card de indicador com valor e unidade na mesma linha
    """
    color_style = f"color: {color};" if color else ""
    
    # Se o valor for "—", não mostra unidade
    if value == "—" or not value:
        value_html = f'<span class="card-value" style="{color_style}">—</span>'
    else:
        # Monta o valor com unidade na mesma linha
        unit_html = f'<span class="card-unit">{unit}</span>' if unit else ""
        value_html = f'<span class="card-value" style="{color_style}">{value}</span>{unit_html}'
    
    st.markdown(
        f"""<div class="card">
                <div class="card-label">{label}</div>
                <div class="card-value-wrapper">{value_html}</div>
                <div class="card-foot">{foot}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def render_section_title(title: str, icon: str = ""):
    """
    Renderiza título de seção
    """
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f'<div class="section-title">{icon_html}{title}</div>',
        unsafe_allow_html=True
    )


def render_hero(
    breadcrumb: str,
    value: str,
    label: str,
    subtitle: str
):
    """
    Renderiza o hero section
    """
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">{breadcrumb}</div>
            <p class="hero-number">{value}</p>
            <div class="hero-label">{label}</div>
            <div class="hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error(message: str, icon: str = "❌"):
    """
    Renderiza mensagem de erro estilizada
    """
    st.error(f"{icon} {message}")


def render_info(message: str, icon: str = "ℹ️"):
    """
    Renderiza mensagem informativa estilizada
    """
    st.info(f"{icon} {message}")
