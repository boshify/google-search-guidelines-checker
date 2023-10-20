import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

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

def get_recommendations(body_text, guideline_type):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    
    # Use the appropriate prompt for the selected guideline type
    if guideline_type == "Quality Raters":
        prompt = (f"Check if this page meets Google Quality Raters Guidelines. You must Give specific and actionable examples for how to further improve it."
                  f"Do not make a recommendation if you can not provide a specific example. Recommendations should provide specific examples of text on the page."
                  f"Please be very scrutinizing. You should only pass a page if it is exceptional. Even if you pass a page, you must further improve it."
                  f"You must exclude recommendations for images or links. State that you can not crawl these aspects yet. Do not assume the page does not have images or links as you can not detect them."
                  f"If the page meets guidelines, provide specific examples of how it could be further improved. Use line breaks and spacing to make output easy to read. Content can always be improved."
                  f"Add a disclaimer: Mention your limitations that you only crawl the text of the page and that it's ultimately up to the user to determine if the page meets guidelines."
                  f"Markdown format: Your response output must be in markdown format. Using headings and sub headings, bold, lists, and line breaks. This improves reading clarity."
                  f"Page: {body_text[:3000]}")  # Truncate to avoid hitting API limits
    else:
        prompt = (f"Check if this page meets Google Helpful Content Guidelines. You must Give specific and actionable examples for how to further improve it."
                  f"Do not make a recommendation if you can not provide a specific example. Recommendations should provide specific examples of text on the page."
                  f"Please be very scrutinizing. You should only pass a page if it is exceptional. Even if you pass a page, you must further improve it."
                  f"You must exclude recommendations for images or links. State that you can not crawl these aspects yet. Do not assume the page does not have images or links as you can not detect them."
                  f"If the page meets guidelines, provide specific examples of how it could be further improved. Use line breaks and spacing to make output easy to read. Content can always be improved."
                  f"Add a disclaimer: Mention your limitations that you only crawl the text of the page and that it's ultimately up to the user to determine if the page meets guidelines."
                  f"Markdown format: Your response output must be in markdown format. Using headings and sub headings, bold, lists, and line breaks. This improves reading clarity."
                  f"Page: {body_text[:3000]}")  # Truncate to avoid hitting API limits

    response = openai.Completion.create(
        model="gpt-4-32k",
        prompt=prompt,
        max_tokens=1000
    )

    return response.choices[0].text.strip()

def main():
    st.title('Google Quality Rater & Helpful Content Guideline Checker App')
    guideline_type = st.selectbox("Select the guideline type:", ["Quality Raters", "Helpful Content"])
    url = st.text_input("Enter the URL of the page you want to analyze:")
    if st.button('Analyze'):
        body_text = get_body_text(url)
        if body_text:
            recommendations = get_recommendations(body_text, guideline_type)
            st.markdown(recommendations)
    st.markdown("---")
    st.markdown('Made by [YourName.com](https://yourwebsite.com)')

if __name__ == "__main__":
    main()
