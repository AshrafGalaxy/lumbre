"""Draw the altar card with native Streamlit text and a small candle header."""

import json

import streamlit as st

from lumbre.altar import AltarCard, download_name

_FLAMES = """
<div style="display:flex;justify-content:center;gap:28px;padding:8px 0 0;">
  <div style="width:12px;height:26px;border-radius:50% 50% 42% 42%;background:#f2c14e;"></div>
  <div style="width:16px;height:36px;border-radius:50% 50% 42% 42%;background:#ffb347;"></div>
  <div style="width:12px;height:26px;border-radius:50% 50% 42% 42%;background:#f2c14e;"></div>
</div>
<p style="text-align:center;color:#e0a15a;letter-spacing:0.22em;font-size:12px;margin:8px 0 0;">
  MARIGOLDS AND A FLAME
</p>
"""


def flames() -> str:
    return _FLAMES


def show_card(card: AltarCard) -> None:
    st.subheader(card.name)
    details = " · ".join(part for part in (card.relationship, card.years) if part)
    if details:
        st.caption(details)
    st.markdown(f"*{_literal(card.inscription)}*")
    st.markdown(_literal(card.remembrance))
    st.markdown("**As told**")
    st.markdown(_literal(card.memory))
    st.markdown("**Brought to the altar**")
    if card.offerings:
        st.markdown("\n".join(f"- {_literal(item)}" for item in card.offerings))
    else:
        st.markdown("Nothing named beyond the flowers and the flame.")
    if card.gaps:
        st.caption("Left unsaid: " + ", ".join(card.gaps) + ".")
    else:
        st.caption("Every place we asked about was filled.")
    st.caption(f"Lettered by {card.model}")
    payload = json.dumps(card.as_dict(), ensure_ascii=False, indent=2)
    st.download_button(
        "Save this altar",
        data=payload,
        file_name=download_name(card.name),
        mime="application/json",
        icon=":material/download:",
        on_click="ignore",
        width="content",
    )


def _literal(text: str) -> str:
    escaped = text
    for char in ("\\", "*", "_", "`", "[", "]"):
        escaped = escaped.replace(char, "\\" + char)
    return escaped
