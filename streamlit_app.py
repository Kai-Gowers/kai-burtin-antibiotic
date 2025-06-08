import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import json

st.title("Penicillin Effectiveness Against Different Types of Bacteria")

st.markdown("""
Penicillin, one of the earliest antibiotics, has varying effectiveness across different bacteria.

This dashboard shows how effective it is against **Gram-positive** vs. **Gram-negative** bacteria, based on MIC values.

""")


with open("burtin.json") as f:
    data = pd.read_json(f)

df = data.melt(id_vars=["Bacteria", "Gram_Staining"],
               value_vars=["Penicillin", "Streptomycin", "Neomycin"],
               var_name="Antibiotic", value_name="MIC")

df["log_MIC"] = np.log10(df["MIC"])
df["Highlight"] = df["Antibiotic"].apply(lambda x: "Penicillin" if x == "Penicillin" else "Other")

gram_pos = df[df["Gram_Staining"] == "positive"]
gram_neg = df[df["Gram_Staining"] == "negative"]

ref_line_pos = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(
    strokeDash=[5, 5], color='blue', strokeWidth=2.5
).encode(x='x:Q')
ref_line_neg = ref_line_pos

arrows_pos = alt.Chart(pd.DataFrame({
    "text": ["←--- More Effective", "Less Effective ---→"],
    "x": [-2, 1.8],
    "y": [gram_pos["Bacteria"].iloc[0]] * 2
})).mark_text(align='center', baseline='bottom', fontSize=13, fontWeight="bold").encode(
    x='x:Q',
    y=alt.value(-15),
    text='text:N'
)

annotations_pos = alt.Chart(pd.DataFrame({
    "x": [-7.5],
    "text": ["✔ Penicillin is highly effective here"]
})).mark_text(
    fontSize=12,
    fontWeight='bold',
    color='green',
    align='left'
).encode(
    x='x:Q',
    y=alt.value(-40), 
    text='text:N'
)

arrows_neg = alt.Chart(pd.DataFrame({
    "text": ["←--- More Effective", "Less Effective ---→"],
    "x": [-1.3, 1.14],
    "y": [gram_neg["Bacteria"].iloc[0]] * 2
})).mark_text(align='center', baseline='bottom', fontSize=13, fontWeight="bold").encode(
    x='x:Q',
    y=alt.value(-15),
    text='text:N'
)

annotations_neg = alt.Chart(pd.DataFrame({
    "x": [3.4],
    "text": ["✘ Penicillin is ineffective here"]
})).mark_text(
    fontSize=12,
    fontWeight='bold',
    color='crimson',
    align='right'
).encode(
    x='x:Q',
    y=alt.value(-40), 
    text='text:N'
)

chart_pos = alt.Chart(gram_pos).mark_bar().encode(
    y=alt.Y("Bacteria:N", sort="-x", title=None),
    x=alt.X("log_MIC:Q", title="Log(MIC)", scale=alt.Scale(domain=[-8, 3])),
    color=alt.Color("Highlight:N",
                    scale=alt.Scale(domain=["Penicillin", "Other"], range=["crimson", "lightgray"]),
                    legend=alt.Legend(title="Antibiotic")),
    tooltip=["Bacteria", "Antibiotic", "MIC"]
).properties(
    title="Gram-Positive Bacteria",
    width=350,
    height=400
)

chart_neg = alt.Chart(gram_neg).mark_bar().encode(
    y=alt.Y("Bacteria:N", sort="-x", title=None),
    x=alt.X("log_MIC:Q", title="Log(MIC)", scale=alt.Scale(domain=[-3, 4])),
    color=alt.Color("Highlight:N",
                    scale=alt.Scale(domain=["Penicillin", "Other"], range=["crimson", "lightgray"]),
                    legend=None),
    tooltip=["Bacteria", "Antibiotic", "MIC"]
).properties(
    title="Gram-Negative Bacteria",
    width=350,
    height=400
)

final_chart = (chart_pos + arrows_pos + annotations_pos + ref_line_pos) | (chart_neg + arrows_neg + annotations_neg + ref_line_neg)
st.altair_chart(final_chart, use_container_width=True)

st.markdown("""
---
### Final Insight:

> Penicillin is **highly effective** against Gram-positive bacteria, but shows **very limited effectiveness** against Gram-negative strains due to their structural resistance.

""")

with st.expander("Learn More: What Are Gram-Positive and Gram-Negative Bacteria?"):
    st.markdown("""
    - **Gram-positive** bacteria have a thick peptidoglycan cell wall that readily absorbs antibiotics like Penicillin.
    - **Gram-negative** bacteria have an additional outer membrane that blocks many drugs, making them more resistant.
    
    These structural differences are why Gram-negative bacteria often require alternative or more potent antibiotics.
    """)

with st.expander("About MIC and Log(MIC)"):
    st.markdown("""
    - **MIC (Minimum Inhibitory Concentration)** measures the smallest amount of an antibiotic needed to inhibit visible bacterial growth.
    - We use `log(MIC)` to allow easier comparison across values that vary by 1000x or more.
    - A `log(MIC)` of 0 means an MIC of 1 — a useful clinical threshold between effective and ineffective.
    """)
