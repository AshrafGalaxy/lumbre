"""Altar page. The scribe lives in the lumbre package."""

import streamlit as st

from lumbre.altar import AltarInput
from lumbre.config import SPACE_URL, load_settings
from lumbre.inference import InferenceError, generate
from lumbre.render import flames, show_card
from lumbre.sample import EMPTY, EXAMPLE
from lumbre.scribe import ScribeError, compose

st.set_page_config(page_title="Lumbre", page_icon="🕯️", layout="wide")

for key, value in EMPTY.items():
    st.session_state.setdefault(key, value)
st.session_state.setdefault("card", None)
st.session_state.setdefault("example", False)

st.title("Lumbre")
st.markdown(
    "Write what you know about someone you want to remember. "
    "An open-weight model letters the card. "
    "Food, a song, and an object are placed only if you name them. "
    "A blank stays blank."
)

if st.button("Try a fictional altar", icon=":material/local_florist:"):
    for key, value in EXAMPLE.items():
        st.session_state[key] = value
    st.session_state.example = True
    st.session_state.card = None
    st.rerun()

if st.session_state.example and st.session_state.name == EXAMPLE["name"]:
    st.info(
        "Rosa Mendoza is fictional. She is here so the altar can be tried before a real name is written.",
        title="Fictional example",
    )

left, right = st.columns(2, gap="large")

with left:
    with st.form("altar"):
        st.text_input("Name", key="name")
        st.text_input(
            "How you knew them",
            key="relationship",
            help="Leave this blank if you do not want it on the card.",
        )
        st.text_input("Years", key="years", help="Leave this blank if you do not know.")
        st.text_area("A memory", key="memory", height=140)
        st.text_input(
            "Favorite food",
            key="food",
            help="Leave this blank and it will not be invented.",
        )
        st.text_input("A song or phrase", key="song")
        st.text_input("An object", key="object")
        submitted = st.form_submit_button(
            "Light the altar",
            type="primary",
            icon=":material/local_fire_department:",
            width="stretch",
        )

with right:
    st.html(flames())
    if submitted:
        try:
            altar = AltarInput.from_form(
                name=st.session_state.name,
                relationship=st.session_state.relationship,
                years=st.session_state.years,
                memory=st.session_state.memory,
                food=st.session_state.food,
                song=st.session_state.song,
                object=st.session_state.object,
            )
        except ValueError as exc:
            st.warning(str(exc), title="One more detail")
        else:
            st.session_state.example = altar.name == EXAMPLE["name"]
            settings = load_settings()
            try:
                with st.spinner("Lettering the card"):
                    st.session_state.card = compose(
                        altar,
                        lambda system, user: generate(system, user, settings),
                    )
            except (InferenceError, ScribeError) as exc:
                st.error(str(exc), title="The card was not lettered")
    if st.session_state.card:
        show_card(st.session_state.card)
    elif not submitted:
        st.caption("The card will appear here.")

settings = load_settings()
if settings.backend == "router":
    st.caption(
        f"Open model through the Hugging Face router: {settings.router_model}. "
        "Your note is sent for one reply and is not stored by Lumbre."
    )
else:
    st.caption(
        f"Open weights: {settings.active_model}. "
        "Your note is sent for one reply and is not stored by Lumbre. "
        f"Public altar: {SPACE_URL}"
    )
