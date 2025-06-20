# Streamlit MVP: Ontology-Based Dataset Mapper
import streamlit as st
import pandas as pd
import json
import networkx as nx
import matplotlib.pyplot as plt

# Load ontology
@st.cache_data
def load_orthopedic_ontology():
    with open("orthopedic_healthcare_ontology_v2.json") as f:
        return json.load(f)

ortho_ontology = load_orthopedic_ontology()

st.title("📊 Ontology-Based Mapping Tool")
st.markdown("Upload a claims dataset and visualize how it maps to the orthopedic healthcare ontology.")

# File upload
uploaded_file = st.file_uploader("Upload a sample claims dataset (CSV):")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data Preview:", df.head())

    found_entities = set()
    found_edges = set()

    # Extract lowercased column names from uploaded data
    columns = set(df.columns.str.lower())

    # Detect which relationships are represented in the data
    for rel in ortho_ontology['relationships']:
        from_node, to_node = rel['from'], rel['to']
        rel_cols = [col.lower() for col in rel.get('via_data_columns', [])]
        if any(col in columns for col in rel_cols):
            found_entities.add(from_node)
            found_entities.add(to_node)
            found_edges.add((from_node, to_node))

    # Build network graph
    st.markdown("### 🔍 Network Coverage in Uploaded Dataset")
    G = nx.DiGraph()
    for ent in {e['name'] for e in ortho_ontology['entities']}:
        color = 'lightgreen' if ent in found_entities else 'lightgray'
        G.add_node(ent, label=ent, color=color)

    for rel in ortho_ontology['relationships']:
        from_node, to_node = rel['from'], rel['to']
        color = 'green' if (from_node, to_node) in found_edges else 'gray'
        label = rel['type']
        G.add_edge(from_node, to_node, label=label, color=color)

    # Draw network
    pos = nx.spring_layout(G, seed=42)
    edge_colors = [G[u][v]['color'] for u, v in G.edges()]
    node_colors = [G.nodes[n]['color'] for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=edge_colors,
            node_size=2000, font_size=9, ax=ax)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
    st.pyplot(fig)

    st.success(f"✅ Matched {len(found_entities)} entities and {len(found_edges)} relationships to the uploaded data.")
