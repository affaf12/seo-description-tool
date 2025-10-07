# Install required packages first:
# pip install streamlit textstat plotly pandas

import streamlit as st
import re
import textstat
import plotly.graph_objects as go
import pandas as pd

# --- SEO Scoring Function ---
def seo_score(description, target_keyword):
    words = description.split()
    word_count = len(words)
    keyword_count = len(re.findall(r'\b{}\b'.format(re.escape(target_keyword)), description, flags=re.IGNORECASE))
    
    # Keyword density
    density = (keyword_count / word_count) * 100 if word_count else 0
    
    # Meta description length score
    meta_length = len(description)
    if meta_length < 50:
        meta_score = 0
    elif meta_length > 160:
        meta_score = 50
    else:
        meta_score = 100
    
    # Keyword presence score
    keyword_score = 100 if density >= 1 else 50  # minimum 1% density
    
    # Readability score (Flesch-Kincaid Reading Ease)
    readability = textstat.flesch_reading_ease(description)
    
    # Headings check (H1-H6)
    headings = re.findall(r'<h[1-6]>.*?</h[1-6]>', description, flags=re.IGNORECASE)
    heading_score = 100 if headings else 50
    
    # Overall SEO score (weighted)
    seo_total_score = int((meta_score*0.3 + keyword_score*0.3 + heading_score*0.2 + min(readability, 100)*0.2))
    
    # Suggestions
    suggestions = []
    if density < 1:
        suggestions.append(f"Increase keyword '{target_keyword}' usage (at least 1%).")
    if meta_length < 50:
        suggestions.append("Meta description too short (<50 chars).")
    if meta_length > 160:
        suggestions.append("Meta description too long (>160 chars).")
    if not headings:
        suggestions.append("Add headings (H1-H6) for better SEO structure.")
    if readability < 60:
        suggestions.append("Improve readability (aim for Flesch Reading Ease ≥ 60).")
    
    # Determine score color
    if seo_total_score >= 80:
        color = "green"
    elif seo_total_score >= 50:
        color = "yellow"
    else:
        color = "red"
    
    # Word frequency for heatmap
    word_freq = pd.Series([w.lower() for w in words]).value_counts()
    
    return seo_total_score, density, meta_length, readability, suggestions, color, word_freq

# --- Streamlit App ---
st.set_page_config(page_title="SEO Description Scorer", page_icon="📝", layout="centered")
st.title("📝 SEO Description Scorer")
st.write("Paste your meta description or text below to get an SEO score, readability, keyword analysis, and interactive visual insights.")

description = st.text_area("Enter your description here", height=150)
target_keyword = st.text_input("Target Keyword", value="Power BI Developer")

if st.button("Analyze SEO"):
    if not description.strip():
        st.warning("Please enter a description to analyze.")
    else:
        score, density, length, readability, suggestions, color, word_freq = seo_score(description, target_keyword)
        
        st.subheader("SEO Analysis Results")
        st.markdown(f"**SEO Score:** <span style='color:{color};font-weight:bold'>{score}/100</span>", unsafe_allow_html=True)
        st.write(f"**Keyword Density:** {round(density,2)}%")
        st.write(f"**Meta Length:** {length} characters")
        st.write(f"**Readability (Flesch Reading Ease):** {round(readability,2)}")
        
        if suggestions:
            st.warning("Suggestions:")
            for s in suggestions:
                st.write(f"- {s}")
        else:
            st.success("✅ Looks good! No major SEO issues detected.")
        
        # --- Visualizations ---
        st.subheader("📊 SEO Visual Insights")
        
        # Keyword Density Gauge
        fig_density = go.Figure(go.Indicator(
            mode="gauge+number",
            value=density,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Keyword Density (%)"},
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 1], 'color': "red"},
                    {'range': [1, 3], 'color': "yellow"},
                    {'range': [3, 10], 'color': "green"}
                ],
            }
        ))
        st.plotly_chart(fig_density, use_container_width=True)
        
        # Meta Length Gauge
        fig_length = go.Figure(go.Indicator(
            mode="gauge+number",
            value=length,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Meta Description Length"},
            gauge={
                'axis': {'range': [0, 200]},
                'bar': {'color': "purple"},
                'steps': [
                    {'range': [0, 50], 'color': "red"},
                    {'range': [50, 160], 'color': "green"},
                    {'range': [160, 200], 'color': "yellow"}
                ],
            }
        ))
        st.plotly_chart(fig_length, use_container_width=True)
        
        # Readability Gauge
        fig_read = go.Figure(go.Indicator(
            mode="gauge+number",
            value=readability,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Readability Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "orange"},
                'steps': [
                    {'range': [0, 60], 'color': "red"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
            }
        ))
        st.plotly_chart(fig_read, use_container_width=True)
        
        # Keyword Occurrences Bar Chart (SEO Heatmap)
        st.subheader("🔑 Keyword Occurrences (Mini SEO Heatmap)")
        fig_word = go.Figure([go.Bar(
            x=word_freq.index,
            y=word_freq.values,
            marker_color=['red' if w.lower() == target_keyword.lower() else 'blue' for w in word_freq.index]
        )])
        fig_word.update_layout(
            xaxis_title="Words",
            yaxis_title="Occurrences",
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig_word, use_container_width=True)
