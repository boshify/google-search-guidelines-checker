import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Extract text content from the given URL
def get_body_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join([tag.text for tag in soup.find_all(['p', 'div', 'span'])])
    except requests.RequestException as e:
        st.warning(f"Failed to crawl {url}. Error: {e}")
        return None

# Analyze the extracted text content based on the selected guideline
def analyze_page(body_text, guideline_type):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    
    if guideline_type == "Quality Raters":
        prompt = (f"Please start by reading this document: Google Quality Rater Guidelines\n\n"
                  f"Next, read my article here: {body_text[:3000]}\n\n"
                  f"Based strictly on the guidelines or the principals outlined in the first document, analyze this article in terms of the depth and detail of the content, "
                  f"the demonstration of expertise and credibility, and how well it fulfills the user's intent. Provide a list of specific action points for potential improvements. "
                  f"Please exclude any generic SEO advice. Output your response in markdown format.")
    else:  # For "Helpful Content" guideline.
        prompt = (f"Please start by reading this document: Google Helpful Content Guidelines\n\n"
                  f"Next, read my article here: {body_text[:3000]}\n\n"
                  f"Based strictly on the guidelines or the principals outlined in the first document, analyze this article in terms of the relevance, clarity, and utility of its content. "
                  f"Identify areas where the content can be made more helpful for users. Provide specific action points for potential improvements. "
                  f"Please exclude any generic SEO advice. Output your response in markdown format.")

    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=1000
    )
    
    return response.choices[0].text.strip()

def main():
    st.title('Google Quality Rater & Helpful Content Guideline Checker App')

    # Input URL
    url = st.text_input('Enter the URL of the page you want to analyze:')
    
    if url:
        body_text = get_body_text(url)
        
        if body_text:
            st.write("Analysis based on Google Quality Raters Guidelines:")
            quality_raters_analysis = analyze_page(body_text, "Quality Raters")
            st.markdown(quality_raters_analysis)

            st.write("Analysis based on Google Helpful Content Guidelines:")
            helpful_content_analysis = analyze_page(body_text, "Helpful Content")
            st.markdown(helpful_content_analysis)

if __name__ == '__main__':
    main()
