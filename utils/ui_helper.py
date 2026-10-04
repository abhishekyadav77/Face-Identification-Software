# -*- coding: utf-8 -*-
"""
UI helpers - CSS injection, sidebar branding, reusable HTML snippets.
Every dynamic value that goes into HTML is escaped (names are user input!).
"""

from html import escape
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from utils.db_helper import BASE_DIR, SOUNDS_DIR, load_settings
from utils.simple_facerec import get_engine

ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


def esc(value) -> str:
    return escape(str(value), quote=True)


def inject_css() -> None:
    css_file = ASSETS_DIR / "style.css"
    if css_file.exists():
        st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_sidebar() -> None:
    """Logo above the page menu + live engine status below it."""
    if LOGO_PATH.exists():
        st.logo(str(LOGO_PATH), size="large")

    engine = get_engine()
    settings = load_settings()
    if engine.available:
        status_cls, status_txt = "ok", "&#9679; FACE ENGINE: READY"
    else:
        status_cls, status_txt = "bad", "&#9679; FACE ENGINE: OFFLINE"
    st.sidebar.markdown(
        f"""
        <div class="node-card">
          <p class="t">ACTIVE NODE</p>
          <p class="s {status_cls}">{status_txt}</p>
          <p class="f">Match tolerance {settings['tolerance']:.2f} &middot; Terminal NODE-3000</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, icon: str = "") -> None:
    st.markdown(
        f"""
        <div class="page-hero">
          <div class="hero-icon">{icon}</div>
          <div><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value, sub: str = "", tone: str = "") -> None:
    """Big-number card. tone: '' (neutral) | 'ok' | 'bad'."""
    st.markdown(
        f'<div class="stat-card {tone}"><div class="lbl">{esc(label)}</div>'
        f'<div class="val">{esc(value)}</div><div class="sub">{esc(sub)}&nbsp;</div></div>',
        unsafe_allow_html=True,
    )


def kv_card(title: str, rows: list[tuple[str, str]]) -> None:
    """Card with label/value rows. Values are trusted HTML snippets built by callers."""
    body = "".join(f'<div class="kv"><span>{esc(k)}</span><span>{v}</span></div>' for k, v in rows)
    st.markdown(f'<div class="terminal-card"><h4>{esc(title)}</h4>{body}</div>', unsafe_allow_html=True)


# ---------- one-time messages that survive st.rerun() ----------
def flash(message: str, kind: str = "success") -> None:
    st.session_state["_flash"] = (kind, message)


def show_flash() -> None:
    item = st.session_state.pop("_flash", None)
    if item:
        kind, message = item
        {"success": st.success, "error": st.error, "warning": st.warning}.get(kind, st.info)(message)


# ---------- media ----------
def bgr_to_rgb(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def play_siren(target=None) -> None:
    """Play the alarm sound (autoplay works because the user just clicked/scanned)."""
    siren = SOUNDS_DIR / "sirensound.mp3"
    if siren.exists():
        (target or st).audio(siren.read_bytes(), format="audio/mpeg", autoplay=True)
