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
    
    url = st.text_input("Enter the URL of the page you want to analyze:")
    
    if st.button('Analyze'):
        with st.spinner('Analyzing...'):
            body_text = get_body_text(url)
            if body_text:
                # Analyze for Quality Raters
                recommendations1 = get_recommendations(body_text, "Quality Raters")
                st.markdown(f"**Recommendations based on Quality Raters Guidelines for {url}**")
                st.markdown(f'<div style="border:2px solid #F0F2F6; padding:10px; border-radius:10px; margin-bottom: 10px;">{recommendations1}</div>', unsafe_allow_html=True)
                
                # Analyze for Helpful Content
                recommendations2 = get_recommendations(body_text, "Helpful Content")
                st.markdown(f"**Recommendations based on Helpful Content Guidelines for {url}**")
                st.markdown(f'<div style="border:2px solid #F0F2F6; padding:10px; border-radius:10px; margin-bottom: 10px;">{recommendations2}</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown('Made by [YourName.com](https://yourwebsite.com)')

if __name__ == "__main__":
    main()
