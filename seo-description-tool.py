# pip install streamlit textstat plotly pandas

import streamlit as st
import re
import textstat
import plotly.graph_objects as go
import pandas as pd

# --- SEO / Post Scoring Function ---
def post_score(content, target_keyword, max_length=300):
    words = content.split()
    word_count = len(words)
    
    # Keyword count
    keyword_count = len(re.findall(re.escape(target_keyword), content, flags=re.IGNORECASE))
    density = (keyword_count / word_count) * 100 if word_count else 0
    
    # Content length
    content_length = len(content)
    if content_length < 50:
        length_score = 0
    elif content_length > max_length:
        length_score = 50
    else:
        length_score = 100
    
    # Keyword presence
    keyword_score = 100 if density >= 1 else 50
    
    # Readability
    readability = textstat.flesch_reading_ease(content)
    
    # Overall score
    total_score = int((length_score*0.3 + keyword_score*0.3 + min(readability,100)*0.4))
    
    # Suggestions
    suggestions = []
    if density < 1:
        suggestions.append(f"Increase keyword '{target_keyword}' usage (≥1%).")
    if content_length > max_length:
        suggestions.append(f"Content too long (> {max_length} chars). Consider condensing.")
    if readability < 60:
        suggestions.append("Improve readability (aim Flesch Reading Ease ≥60).")
    
    # Condensed version if too long
    condensed = content if content_length <= max_length else content[:max_length-3] + "..."
    
    # Word frequency for heatmap
    word_freq = pd.Series([w.lower() for w in words]).value_counts()
    
    return total_score, density, content_length, readability, suggestions, word_freq, condensed

# --- Streamlit App ---
st.set_page_config(page_title="Multi-Platform Post Optimizer", page_icon="📝", layout="wide")
st.title("📝 Multi-Platform Post Optimizer")

# --- Platforms Tabs ---
platform = st.radio("Select Platform", ["LinkedIn", "Threads", "Google Business"])

if platform == "LinkedIn":
    max_len = 1300  # LinkedIn post max length
elif platform == "Threads":
    max_len = 500  # Threads/X post length
else:
    max_len = 1500  # Google Business recommendation

post_text = st.text_area(f"Enter your {platform} post text here", height=200)
target_keyword = st.text_input(f"Target Keyword for {platform}", value="Power BI Developer")

if st.button(f"Analyze {platform} Post"):
    if not post_text.strip():
        st.warning("Please enter post text to analyze.")
    else:
        score, density, length, readability, suggestions, word_freq, condensed = post_score(post_text, target_keyword, max_len)
        
        # --- Results ---
        st.subheader(f"{platform} Post Analysis Results")
        st.write(f"**Score:** {score}/100")
        st.write(f"**Keyword Density:** {round(density,2)}%")
        st.write(f"**Length:** {length} characters (Max recommended: {max_len})")
        st.write(f"**Readability:** {round(readability,2)} Flesch Reading Ease")
        
        if suggestions:
            st.warning("Suggestions:")
            for s in suggestions:
                st.write(f"- {s}")
        else:
            st.success("✅ Looks good!")
        
        if length > max_len:
            st.error(f"⚠️ Post exceeds recommended length! Consider using condensed version below.")
            st.info(f"Suggested Condensed Post ({len(condensed)} chars):\n\n{condensed}")
        
        # --- Visuals ---
        st.subheader("Keyword Occurrences Heatmap")
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
