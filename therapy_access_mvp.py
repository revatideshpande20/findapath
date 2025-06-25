# 📁 Phase 1: Ontology and Schema Setup

# File: orthopedic_healthcare_ontology.json

ontology = {
    "entities": [
        {"name": "Patient", "attributes": ["patient_id", "dob", "insurance_id"], "type": "entity"},
        {"name": "Provider", "attributes": ["provider_id", "npi", "specialty"], "type": "entity"},
        {"name": "Payer", "attributes": ["payer_id", "plan_name"], "type": "entity"},
        {"name": "Facility", "attributes": ["facility_id", "location", "type"], "type": "entity"},
        {"name": "Claim", "attributes": ["claim_id", "date", "diagnosis", "procedure_code"], "type": "entity"}
    ],
    "relationships": [
        {"from": "Patient", "to": "Provider", "type": "consults_with", "via_data_columns": ["provider_id"]},
        {"from": "Patient", "to": "Payer", "type": "covered_by", "via_data_columns": ["insurance_id", "payer_id"]},
        {"from": "Patient", "to": "Facility", "type": "visits", "via_data_columns": ["facility_id"]},
        {"from": "Patient", "to": "Claim", "type": "submits", "via_data_columns": ["claim_id"]},
        {"from": "Claim", "to": "Provider", "type": "rendered_by", "via_data_columns": ["provider_id"]},
        {"from": "Claim", "to": "Facility", "type": "occurred_at", "via_data_columns": ["facility_id"]},
        {"from": "Claim", "to": "Payer", "type": "billed_to", "via_data_columns": ["payer_id"]}
    ]
}

# Save as JSON manually or via:
import json
with open("orthopedic_healthcare_ontology.json", "w") as f:
    json.dump(ontology, f, indent=2)

# 📁 Phase 2: Streamlit + Network Graph
# File: ontology_mapper_app.py

import streamlit as st
import pandas as pd
import json
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🧠 Ontology-Based Data Mapper for Orthopedic Claims")

@st.cache_data

def load_ontology():
    with open("orthopedic_healthcare_ontology.json") as f:
        data = json.load(f)
        return data

ontology = load_ontology()

uploaded_file = st.file_uploader("Upload a healthcare dataset (CSV)")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Sample Data", df.head())

    columns = set(df.columns.str.lower())
    found_entities = set()
    found_edges = set()

    for rel in ontology['relationships']:
        from_node = rel['from']
        to_node = rel['to']
        rel_cols = [c.lower() for c in rel['via_data_columns']]
        if any(col in columns for col in rel_cols):
            found_entities.update([from_node, to_node])
            found_edges.add((from_node, to_node))

    G = nx.DiGraph()
    for ent in [e['name'] for e in ontology['entities']]:
        color = 'lightgreen' if ent in found_entities else 'lightgray'
        G.add_node(ent, color=color)

    for rel in ontology['relationships']:
        f, t = rel['from'], rel['to']
        color = 'green' if (f, t) in found_edges else 'gray'
        G.add_edge(f, t, label=rel['type'], color=color)

    pos = nx.spring_layout(G, seed=42)
    node_colors = [G.nodes[n]['color'] for n in G.nodes()]
    edge_colors = [G[u][v]['color'] for u, v in G.edges()]
    edge_labels = nx.get_edge_attributes(G, 'label')

    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw(G, pos, node_color=node_colors, edge_color=edge_colors, with_labels=True, node_size=2000, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, ax=ax)
    st.pyplot(fig)

# 📁 Phase 3: Validation Rules (simple version)
    st.subheader("⚠️ Validation Check")
    missing_cols = set()
    for rel in ontology['relationships']:
        for col in rel['via_data_columns']:
            if col.lower() not in columns:
                missing_cols.add(col)
    if missing_cols:
        st.error(f"Missing required columns: {sorted(missing_cols)}")
    else:
        st.success("All required columns for detected relationships are present.")

# 📁 Phase 4 (Optional): Natural Language Interface
    st.subheader("🔎 Ask a question (beta, local parsing only)")
    question = st.text_input("E.g., Which facilities are most visited?")
    if question:
        if "facility" in question.lower():
            st.write(df["facility_id"].value_counts().head())
        elif "provider" in question.lower():
            st.write(df["provider_id"].value_counts().head())
        else:
            st.warning("This prototype only supports 'facility' or 'provider' questions.")
