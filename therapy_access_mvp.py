# Streamlit MVP: Therapy Journey Mapper v2
import streamlit as st
import pandas as pd

# Load the updated ontology CSV
@st.cache_data
def load_journey():
    return pd.read_csv("mental_health_journey_ontology_v2.csv")

journey_df = load_journey()

# Title
st.title("🧠 Find a Path: Mental Health Navigation Tool")
st.markdown("Helping you navigate the complex journey to finding mental health care in the U.S.")

# User input
user_input = st.text_area("Describe your situation in detail (symptoms, confusion, what you're looking for, etc.):", height=150)

# Inference function with logic for ambiguity and branching
def infer_step_and_questions(text):
    text = text.lower()
    step = 1
    clarifications = []

    if any(x in text for x in ["unmotivated", "numb", "angry", "depressed"]):
        step = 1

    if "what kind of doctor" in text or "pcp" in text or "therapist" in text:
        step = 2

    if "insurance" in text or "uhc" in text or "coverage" in text:
        step = max(step, 3)

    if "find" in text and "doctor" in text or "search" in text:
        step = max(step, 4)

    if "book" in text or "appointment" in text:
        step = max(step, 6)

    row = journey_df[journey_df["Step ID"] == step].iloc[0]
    if row["Decision Required?"] == "Yes" and row["Clarification Questions"]:
        clarifications.append(row["Clarification Questions"])

    return step, clarifications

# Main logic
if user_input:
    step_id, questions = infer_step_and_questions(user_input)
    row = journey_df[journey_df["Step ID"] == step_id].iloc[0]

    st.subheader("📍 You are here in your journey")
    st.markdown(f"**Step {row['Step ID']}: {row['Step Name']}**")
    st.markdown(f"**What this means:** {row['Description']}")
    st.markdown(f"**Estimated time:** {row['Estimated Time']}")
    st.markdown(f"**Common challenges:** {row['Stuck Points']}")
    st.markdown(f"**Helpful resources:** {row['Resources']}")

    if questions:
        st.warning("🔍 To better guide you, we need more info:")
        for q in questions:
            st.markdown(f"- {q}")

    st.subheader("➡️ What to do next")
    if step_id < 8:
        next_row = journey_df[journey_df["Step ID"] == step_id + 1].iloc[0]
        st.markdown(f"**Next Step: {next_row['Step Name']}**")
        st.markdown(next_row['Description'])
    else:
        st.success("You're at the final step. Good luck with your session!")

# Optional: display full journey map
with st.expander("🧭 View Full Journey Map"):
    for _, row in journey_df.iterrows():
        st.markdown(f"**Step {row['Step ID']} - {row['Step Name']}**: {row['Description']} → _{row['Estimated Time']}_")
