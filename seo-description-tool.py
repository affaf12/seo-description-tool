# pip install streamlit textstat plotly pandas nltk

import streamlit as st
import re
import textstat
import plotly.graph_objects as go
import pandas as pd
import nltk
from nltk.corpus import stopwords
from collections import Counter

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# --- Function to score & optimize post ---
def post_score_advanced(content, target_keyword, max_length=300, platform="Generic"):
    words = content.split()
    word_count = len(words)
    
    # Keyword count & density
    keyword_count = len(re.findall(re.escape(target_keyword), content, flags=re.IGNORECASE))
    density = (keyword_count / word_count) * 100 if word_count else 0
    
    # Content length score
    content_length = len(content)
    if content_length < 50:
        length_score = 0
    elif content_length > max_length:
        length_score = 50
    else:
        length_score = 100
    
    # Keyword presence score
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
    
    # Condensed / optimized version
    condensed = content
    if content_length > max_length:
        if re.search(re.escape(target_keyword), content, flags=re.IGNORECASE):
            start_idx = content.lower().find(target_keyword.lower())
            end_idx = start_idx + max_length
            condensed = content[start_idx:end_idx].strip()
        else:
            condensed = content[:max_length-3] + "..."
    
    # Generate multiple optimized versions
    variants = [condensed]
    if density < 1:
        variants.append(condensed + f" Include '{target_keyword}' naturally in the first sentence.")
    if readability < 60:
        variants.append(condensed + " Rewrite some sentences for clarity and simplicity.")
    
    # Generate hashtags for LinkedIn/Threads
    hashtag_suggestions = []
    if platform in ["LinkedIn", "Threads"]:
        word_counts = Counter([w.lower().strip('.,!?') for w in words if w.lower() not in stop_words])
        top_words = [word for word, count in word_counts.most_common(10)]
        hashtag_suggestions = [f"#{w.replace(' ', '')}" for w in top_words if len(w) > 2]
        if target_keyword.lower() not in [w.lower() for w in top_words]:
            hashtag_suggestions.insert(0, f"#{target_keyword.replace(' ','')}")
    
    # Word frequency for heatmap
    word_freq = pd.Series([w.lower() for w in words]).value_counts()
    
    # Highlight missing keywords in content
    highlighted = content.replace(target_keyword, f"**{target_keyword}**")
    
    return total_score, density, content_length, readability, suggestions, word_freq, variants, hashtag_suggestions, highlighted

# --- Streamlit App ---
st.set_page_config(page_title="Pro Multi-Platform Post Optimizer", page_icon="📝", layout="wide")
st.title("🚀 Pro Multi-Platform Post Optimizer")

platform = st.radio("Select Platform", ["LinkedIn", "Threads", "Google Business"])
max_len = {"LinkedIn":1300, "Threads":500, "Google Business":1500}.get(platform, 300)

post_text = st.text_area(f"Enter your {platform} post text here", height=200)
target_keyword = st.text_input(f"Target Keyword for {platform}", value="Power BI Developer")

if st.button(f"Analyze & Optimize {platform} Post"):
    if not post_text.strip():
        st.warning("Please enter post text to analyze.")
    else:
        score, density, length, readability, suggestions, word_freq, variants, hashtags, highlighted = post_score_advanced(post_text, target_keyword, max_len, platform)
        
        # --- Main Results ---
        st.subheader(f"{platform} Post Analysis")
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
        
        # Highlight keyword in original post
        st.subheader("🔍 Highlighted Keyword in Original Post")
        st.markdown(highlighted)
        
        # Variants
        st.subheader("✏️ Optimized Post Variants")
        for i, v in enumerate(variants):
            st.info(f"Variant {i+1} ({len(v)} chars):\n\n{v}")
        
        # Hashtags
        if hashtags:
            st.subheader("💡 Suggested Hashtags")
            st.write(", ".join(hashtags))
        
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
