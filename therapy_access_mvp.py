# Streamlit MVP: Mental Health Journey Mapper
import streamlit as st
import pandas as pd
import openai
import os

# Load ontology CSV
@st.cache_data
def load_journey():
    return pd.read_csv("mental_health_journey_ontology.csv")

journey_df = load_journey()

# Title
st.title("🧠 Therapy Access Journey Helper")
st.markdown("Helping you navigate the confusing process of finding mental health care")

# Input
user_input = st.text_area("Describe your situation (e.g. what's bothering you, what you're unsure about, insurance details)", height=150)

# Simple GPT-style mapping logic
@st.cache_data
def map_input_to_step(text):
    keywords = {
        "anxious": 1,
        "overwhelmed": 1,
        "insurance": 3,
        "cigna": 3,
        "find therapist": 4,
        "can't find": 4,
        "no availability": 5,
        "booking": 6,
        "appointment": 6,
        "forms": 7,
        "first session": 8
    }
    matched = [step for word, step in keywords.items() if word in text.lower()]
    if matched:
        return max(set(matched), key=matched.count)
    return 1

if user_input:
    step_id = map_input_to_step(user_input)
    row = journey_df[journey_df["Step ID"] == step_id].iloc[0]

    st.subheader("📍 You are here in your journey")
    st.markdown(f"**Step {row['Step ID']}: {row['Step Name']}**")
    st.markdown(f"**What this means:** {row['Description']}")
    st.markdown(f"**Estimated time:** {row['Estimated Time']}")
    st.markdown(f"**Common challenges:** {row['Stuck Points']}")
    st.markdown(f"**Helpful resources:** {row['Resources']}")

    st.subheader("➡️ What to do next")
    if step_id < 8:
        next_row = journey_df[journey_df["Step ID"] == step_id + 1].iloc[0]
        st.markdown(f"**Next Step: {next_row['Step Name']}**")
        st.markdown(next_row['Description'])
    else:
        st.success("You're at the final step. Good luck with your session!")

# Optionally display full journey
with st.expander("🧭 View Full Journey Map"):
    for _, row in journey_df.iterrows():
        st.markdown(f"**Step {row['Step ID']} - {row['Step Name']}**: {row['Description']} → _{row['Estimated Time']}_")
