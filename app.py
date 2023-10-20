import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

def get_body_text(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join([tag.text for tag in soup.find_all(['p', 'div', 'span'])])
    except requests.RequestException as e:
        st.warning(f"Failed to crawl {url}. Error: {e}")
        return None

def get_recommendations(body_text, guideline_type):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    # The prompt remains largely the same, with slight variations based on guideline type
    prompt = (f"Check if this page meets Google {guideline_type} Guidelines. [... similar conditions ...] "
              f"Page: {body_text[:3000]}")
    
    response = openai.Completion.create(
        model="gpt-3.5-turbo-16k",
        prompt=prompt,
        max_tokens=16385
    )
    
    return response.choices[0].text.strip()

def main():
    st.title('Google Quality Rater & Helpful Content Guideline Checker App')
    
    guideline_type = st.selectbox("Select the guideline type:", ["Quality Raters", "Helpful Content"])
    
    url1 = st.text_input("Enter the URL of the first page you want to analyze:")
    url2 = st.text_input("Enter the URL of the second page you want to analyze:")
    
    if st.button('Analyze'):
        with st.spinner('Analyzing...'):
            # Analyze the first URL
            body_text1 = get_body_text(url1)
            if body_text1:
                recommendations1 = get_recommendations(body_text1, guideline_type)
                st.markdown(f"**Recommendations for {url1}**")
                st.markdown(f'<div style="border:2px solid #F0F2F6; padding:10px; border-radius:10px; margin-bottom: 10px;">{recommendations1}</div>', unsafe_allow_html=True)
            
            # Analyze the second URL
            body_text2 = get_body_text(url2)
            if body_text2:
                recommendations2 = get_recommendations(body_text2, guideline_type)
                st.markdown(f"**Recommendations for {url2}**")
                st.markdown(f'<div style="border:2px solid #F0F2F6; padding:10px; border-radius:10px; margin-bottom: 10px;">{recommendations2}</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown('Made by [YourName.com](https://yourwebsite.com)')

if __name__ == "__main__":
    main()
