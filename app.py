import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import PyPDF2
from io import BytesIO

def download_and_read_pdf(url):
    response = requests.get(url)
    response.raise_for_status()

    with BytesIO(response.content) as open_pdf_file:
        reader = PyPDF2.PdfReader(open_pdf_file)
        content = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            content += page.extract_text()
    return content

quality_rater_guidelines = download_and_read_pdf("https://github.com/boshify/google-search-guidelines-checker/raw/main/searchqualityevaluatorguidelines.pdf")
helpful_content_guidelines = download_and_read_pdf("https://github.com/boshify/google-search-guidelines-checker/raw/main/Google%20Helpful%20Content%20Guidelines.pdf")

def download_and_read_pdf(url):
    response = requests.get(url)
    response.raise_for_status()

    with BytesIO(response.content) as open_pdf_file:
        reader = PyPDF2.PdfReader(open_pdf_file)
        content = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            content += page.extract_text()
    return content

quality_rater_guidelines = download_and_read_pdf("https://github.com/boshify/google-search-guidelines-checker/raw/main/searchqualityevaluatorguidelines.pdf")
helpful_content_guidelines = download_and_read_pdf("https://github.com/boshify/google-search-guidelines-checker/raw/main/Google%20Helpful%20Content%20Guidelines.pdf")

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

def analyze_page(body_text, guideline_type):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    
    if guideline_type == "Quality Raters":
        guideline_content = quality_rater_guidelines
    else:
        guideline_content = helpful_content_guidelines
    
    prompt = (f"Please start by reading this document: {guideline_content}\n\n"
              f"Next, read my article here: {body_text[:3000]}\n\n")
    
    if guideline_type == "Quality Raters":
        prompt += (f"Based strictly on the guidelines or the principals outlined in the first document, analyze this article in terms of the depth and detail of the content, "
                   f"the demonstration of expertise and credibility, and how well it fulfills the user's intent. Provide a list of specific action points for potential improvements. "
                   f"Please exclude any generic SEO advice. Output your response in markdown format.")
    else:
        prompt += (f"Based strictly on the guidelines or the principals outlined in the first document, analyze this article in terms of the relevance, clarity, and utility of its content. "
                   f"Identify areas where the content can be made more helpful for users. Provide specific action points for potential improvements. "
                   f"Please exclude any generic SEO advice. Output your response in markdown format.")
    
    # Adjust the call to the OpenAI API to use the chat endpoint
    messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    
    return response.choices[0].message['content'].strip()

def analyze_question(body_text, guideline_type, question):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    if guideline_type == "Quality Raters":
        guideline_content = quality_rater_guidelines
    else:
        guideline_content = helpful_content_guidelines

    prompt = (f"Please start by reading this document: {guideline_content}\n\n"
              f"Next, read my article here: {body_text[:3000]}\n\n"
              f"Based strictly on the guidelines or the principals outlined in the first document, analyze this aspect:\n\n"
              f"**{question}**\n\n")
    
    # Adjust the call to the OpenAI API to use the chat endpoint
    messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    
    return response.choices[0].message['content'].strip()

def main():
    st.title('Google Quality Rater & Helpful Content Guideline Checker App')

    url = st.text_input('Enter the URL of the page you want to analyze:')
    
    if url:
        progress_bar = st.progress(0)
        st.write("Fetching and analyzing page content...")

        body_text = get_body_text(url)
        progress_bar.progress(50)
        
        if body_text:
            if st.checkbox("Comprehensive Web Page Quality Review Checklist"):
                checklist_questions = [
                    "Determine the primary purpose of the page.",
                    "Ensure the purpose serves visitors' genuine interests.",
                    "Verify the page provides beneficial content aligned with its purpose.",
                    # Add all other questions from the checklist here
                ]

                for question in checklist_questions:
                    st.write(f"Analysis for: {question}")
                    analysis = analyze_question(body_text, "Quality Raters", question)
                    st.markdown(analysis)
                    
                progress_bar.progress(100)

if __name__ == '__main__':
    main()
