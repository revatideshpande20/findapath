# Streamlit MVP: Therapy Journey Mapper + Ontology Mapper
import streamlit as st
import pandas as pd
import json
import networkx as nx
import matplotlib.pyplot as plt

# Load ontology and journey steps
@st.cache_data
def load_mental_journey():
    return pd.read_csv("mental_health_journey_ontology_v2.csv")

@st.cache_data
def load_orthopedic_journey():
    return pd.read_csv("orthopedic_journey_steps.csv")

@st.cache_data
def load_orthopedic_ontology():
    with open("orthopedic_healthcare_ontology_v2.json") as f:
        return json.load(f)

mental_df = load_mental_journey()
ortho_df = load_orthopedic_journey()
ortho_ontology = load_orthopedic_ontology()

st.title("🧠 Find a Path: Healthcare Navigation Tool")
st.markdown("Helping you navigate your care journey — mental health, orthopedics, and now, data understanding.")

# User input
user_input = st.text_area("Describe your situation in detail (symptoms, confusion, what you're looking for, etc.):", height=150)

# Domain detection
@st.cache_data
def detect_domain(text):
    text = text.lower()
    if any(x in text for x in ["anxious", "numb", "unmotivated", "depressed", "therapist"]):
        return "mental_health"
    if any(x in text for x in ["knee", "joint", "limp", "mobility", "orthopedic", "bone", "pain"]):
        return "orthopedic"
    return "mental_health"  # default fallback

def infer_step(text, domain):
    text = text.lower()
    clarifications = []
    if domain == "mental_health":
        journey_df = mental_df
        step = 1
        if "doctor" in text or "pcp" in text or "therapist" in text:
            step = 2
        if "insurance" in text or "coverage" in text:
            step = max(step, 3)
        if "find" in text or "search" in text:
            step = max(step, 4)
        if "book" in text or "appointment" in text:
            step = max(step, 6)
    elif domain == "orthopedic":
        journey_df = ortho_df
        step = 1
        if "what kind of doctor" in text or "orthopedic" in text:
            step = 2
        if "insurance" in text or "uhc" in text:
            step = max(step, 3)
        if "referral" in text or "pcp" in text:
            step = max(step, 4)
        if "book" in text or "appointment" in text:
            step = max(step, 5)
    else:
        journey_df = mental_df
        step = 1

    row = journey_df[journey_df["Step ID"] == step].iloc[0]
    if row.get("Decision Required?") == "Yes":
        clar_q = str(row.get("Clarification Questions", "")).strip()
        if clar_q and clar_q.lower() != "nan":
            clarifications.append(clar_q)

    return step, clarifications, journey_df

# Journey mapping
if user_input:
    domain = detect_domain(user_input)
    step_id, questions, journey_df = infer_step(user_input, domain)
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
    if step_id < journey_df["Step ID"].max():
        next_row = journey_df[journey_df["Step ID"] == step_id + 1].iloc[0]
        st.markdown(f"**Next Step: {next_row['Step Name']}**")
        st.markdown(next_row['Description'])
    else:
        st.success("You're at the final step. Good luck!")

# Optional: view full journey map
with st.expander("🧭 View Full Journey Map"):
    st.markdown("**Mental Health Steps:**")
    for _, row in mental_df.iterrows():
        st.markdown(f"- **Step {row['Step ID']} - {row['Step Name']}**: {row['Description']}")

    st.markdown("**Orthopedic Steps:**")
    for _, row in ortho_df.iterrows():
        st.markdown(f"- **Step {row['Step ID']} - {row['Step Name']}**: {row['Description']}")

# Visualize orthopedic ontology with highlights from uploaded data
with st.expander("📊 Upload Claims Data to Map Real-World Coverage"):
    uploaded_file = st.file_uploader("Upload a sample claims dataset (CSV):")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:", df.head())

        found_entities = set()
        found_edges = set()

        # Map columns to ontology
        columns = set(df.columns.str.lower())

        for rel in ortho_ontology['relationships']:
            from_node, to_node = rel['from'], rel['to']
            rel_cols = [col.lower() for col in rel.get('via_data_columns', [])]
            if any(col in columns for col in rel_cols):
                found_entities.add(from_node)
                found_entities.add(to_node)
                found_edges.add((from_node, to_node))

        st.markdown("### Network Coverage in Uploaded Dataset")
        G = nx.DiGraph()
        for ent in {e['name'] for e in ortho_ontology['entities']}:
            color = 'lightgreen' if ent in found_entities else 'lightgray'
            G.add_node(ent, label=ent, color=color)

        for rel in ortho_ontology['relationships']:
            from_node, to_node = rel['from'], rel['to']
            color = 'green' if (from_node, to_node) in found_edges else 'gray'
            label = rel['type']
            G.add_edge(from_node, to_node, label=label, color=color)

        pos = nx.spring_layout(G, seed=42)
        edge_colors = [G[u][v]['color'] for u, v in G.edges()]
        node_colors = [G.nodes[n]['color'] for n in G.nodes()]

        fig, ax = plt.subplots(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=edge_colors, node_size=2000, font_size=9, ax=ax)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
        st.pyplot(fig)

        st.success(f"✅ Matched {len(found_entities)} entities and {len(found_edges)} relationships to the uploaded data.")
