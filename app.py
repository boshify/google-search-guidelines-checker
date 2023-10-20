import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
from io import BytesIO

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

def analyze_questions(body_text, guideline_type, questions):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    if guideline_type == "Quality Raters":
        guideline_content = quality_rater_guidelines
    else:
        guideline_content = helpful_content_guidelines

    prompt = (f"Please start by reading this document: {guideline_content}\n\n"
              f"Next, read my article here: {body_text[:3000]}\n\n"
              f"Based strictly on the guidelines or the principals outlined in the first document, analyze the following aspects:\n\n")
    
    for question in questions:
        prompt += f"**{question}**\n\n"
    
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
    run_analysis = st.button("Get Report")
    
    if run_analysis:
        progress_bar = st.progress(0)
        st.write("Fetching and analyzing page content...")

        body_text = get_body_text(url)
        progress_bar.progress(50)
        
        if body_text:
            st.write("Analysis based on Google Quality Raters Guidelines:")
            analysis = analyze_questions(body_text, "Quality Raters", quality_rater_questions)
            st.markdown(analysis)

            progress_bar.progress(100)

if __name__ == '__main__':
    quality_rater_guidelines = """Your Quality Rater Guidelines content here"""

    quality_rater_questions = [
        "Determine the primary purpose of the page.",
        "Ensure the purpose serves visitors' genuine interests.",
        "Verify the page provides beneficial content aligned with its purpose.",
        "Distinguish Main Content (MC), Supplementary Content (SC), and Advertisements (Ads).",
        "Assess the quality and relevance of Main Content.",
        "Ensure Supplementary Content enhances user experience without detracting from Main Content.",
        "Check that Advertisements are clearly marked and unobtrusive.",
        "Determine if the page contains YMYL information (related to health, finance, safety, or well-being).",
        "Ensure YMYL content is accurate, trustworthy, and backed by expertise (E-A-T).",
        "Evaluate the expertise, authoritativeness, and trustworthiness of content creators.",
        "Confirm the content creator possesses deep knowledge of the subject matter.",
        "Identify who is responsible for the website.",
        "Verify authorship information is present.",
        "Include contact details if applicable.",
        "Assess the website and content creator's reputation.",
        "Consider user reviews, expert recommendations, news articles, and awards.",
        "Verify expertise through real-life experiences.",
        "Ensure the main heading or page title provides an accurate summary of the content.",
        "Avoid exaggeration or sensationalism in headings or titles.",
        "Does the content genuinely serve visitors' interests?",
        "Is the content produced for quality or primarily for search engine rankings?",
        "Does excessive automation impact content quality?",
        "Does the content add substantial value or merely summarize others' work?",
        "Is the content created based on trends or tailored to the audience's needs?",
        "Does the content leave users feeling like they need to search again to get better information?",
        "Does your content actually answer the question it promised to answer?",
        "Will someone reading your content leave feeling like they've had a satisfying experience and learned enough about a topic to help achieve their goal?",
        "Does the content provide substantial value when compared to other pages in search results?",
        "Does the content provide original information, reporting, research, or analysis?",
        "Does the content provide a substantial, complete, or comprehensive description of the topic?",
        "Does the content provide insightful analysis or interesting information that is beyond the obvious?",
        "If the content draws on other sources, does it avoid simply copying or rewriting those sources, and instead provide substantial additional value and originality?",
        "Does the main heading or page title provide a descriptive, helpful summary of the content?",
        "Does the main heading or page title avoid exaggeration or being shocking in nature?",
        "Is this the sort of page you'd want to bookmark, share with a friend, or recommend?",
        "Would you expect to see this content in or referenced by a printed magazine, encyclopedia, or book?",
        "Is it self-evident to your visitors who authored your content, do pages carry a byline, where one might be expected?",
        "Do bylines lead to further information about the author or authors involved, giving background about them and the areas they write about?",
        "If automation is used to substantially generate content, Is the use of automation, including AI-generation, self-evident to visitors through disclosures or in other ways?",
        "Are you providing background about how automation or AI-generation was used to create content (in case it was)?",
        "Are you explaining why automation or AI was seen as useful to produce content (in case it was)?",
        "Does the content present information in a way that makes you want to trust it, such as clear sourcing, evidence of the expertise involved, background about the author or the site that publishes it, such as through links to an author page or a site's About page?",
        "If someone researched the site producing the content, would they come away with an impression that it is well-trusted or widely-recognized as an authority on its topic?",
        "Is this content written by an expert or enthusiast who demonstrably knows the topic well?",
        "Is the content free from easily-verified factual errors?",
        "Does your content clearly demonstrate first-hand expertise and a depth of knowledge (for example, expertise that comes from having actually used a product or service, or visiting a place)?",
        "Is the content free from spelling or stylistic issues?",
        "Was the content produced well, or does it appear sloppy or hastily produced?"
    ]

    main()
