"""Interactive results dashboard; run with `streamlit run app/dashboard.py`."""

from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Singhbhum Prospectivity Workbench", layout="wide")
st.title("Singhbhum Mineral Prospectivity Workbench")
st.caption("Exploratory anomaly prioritization — not deposit confirmation.")

result_path = Path(
    st.sidebar.text_input("Results CSV", "data/processed/anomaly_results.csv")
)
if not result_path.is_file():
    st.info("Run the analysis pipeline first, then select anomaly_results.csv.")
    st.stop()

data = pd.read_csv(result_path)
st.metric("Locations analysed", len(data))
st.metric("Anomalies", int(data["is_anomaly"].sum()))

with st.sidebar:
    only_anomalies = st.checkbox("Show anomalies only", value=False)
    candidate_limit = st.slider("Candidate rows", 10, min(200, len(data)), min(50, len(data)))

display = data[data["is_anomaly"]].copy() if only_anomalies else data.copy()
display = display.nsmallest(candidate_limit, "candidate_rank")
st.map(display.rename(columns={"latitude": "lat", "longitude": "lon"}))

st.subheader("Priority candidates")
st.dataframe(display, use_container_width=True, hide_index=True)

st.subheader("PCA view")
st.scatter_chart(display, x="PC1", y="PC2", color="is_anomaly")
