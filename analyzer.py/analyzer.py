
import os
import google.generativeai as genai
from urllib.parse import urlparse
from serpapi import GoogleSearch
from textblob import TextBlob
from newspaper import Article
import spacy
from PIL import Image
import io
from langdetect import detect, LangDetectException

# --- Configure APIs ---
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model for spaCy...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

try:
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
except Exception as e:
    print(f"Could not configure Gemini API: {e}")

# --- Language Detection ---
def detect_language(text):
    try:
        return detect(text[:500])
    except LangDetectException:
        return 'en'

# --- Text Analysis Functions ---
def get_article_details(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {'text': article.text, 'title': article.title, 'authors': article.authors}
    except Exception:
        return None

def analyze_text_sentiment(text, lang='en'):
    if lang != 'en': return {'polarity': 'N/A', 'subjectivity': 'N/A'}
    if not text: return {'polarity': 0, 'subjectivity': 0}
    analysis = TextBlob(text)
    return {'polarity': round(analysis.sentiment.polarity, 2), 'subjectivity': round(analysis.sentiment.subjectivity, 2)}

def calculate_reading_time(text):
    if not text: return 0
    word_count = len(text.split())
    reading_time = round(word_count / 200)
    return max(1, reading_time)

def extract_named_entities(text, lang='en'):
    if lang != 'en': return {'message': 'This analysis is only available for English articles.'}
    if not text: return {}
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "LOC"]:
            if ent.label_ not in entities: entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
    for label, items in entities.items():
        entities[label] = sorted(list(set(items)))
    return entities

def perform_global_cross_reference(article_title):
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key: return {'error': 'Search API key is not configured.'}
    params = {"q": article_title, "api_key": api_key, "engine": "google", "num": 10}
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        cross_references = []
        found_domains = set()
        if 'organic_results' in results:
            for res in results['organic_results']:
                if 'title' in res and 'link' in res:
                    domain = urlparse(res['link']).netloc.replace('www.', '')
                    if domain not in found_domains:
                        cross_references.append({'title': res['title'], 'link': res['link'], 'source': domain})
                        found_domains.add(domain)
                if len(cross_references) >= 4: break
        return {'references': cross_references}
    except Exception:
        return {'error': 'Failed to perform global search.'}

def get_gemini_analysis(text):
    if not genai.get_model('models/gemini-1.5-flash'): return "Gemini API is not configured."
    
    prompt = f"""
    You are an expert news analyst. Your task is to provide a "Deep Dive" into the following article text.
    First, identify the primary language of the text. Then, conduct your analysis based on the following criteria, presenting your findings in the same language as the article:
    1.  **Objectivity & Bias:** Is the language neutral or emotionally charged? Does it seem to favor one side?
    2.  **Writing Style:** What is the tone (e.g., formal, informal, persuasive, informative)?
    3.  **Confidence Level:** Based on the language and tone, how credible does this article feel? (e.g., High, Medium, Low).

    Present your final analysis as a single, concise paragraph.

    Article Text:
    ---
    {text[:4000]} 
    ---
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        if response.prompt_feedback.block_reason:
            return f"AI analysis was blocked by the safety filter. Reason: {response.prompt_feedback.block_reason.name}"
            
        return response.text
    except Exception as e:
        print(f"ERROR during Gemini API call: {e}")
        return "The AI analysis could not be completed at this time. Check the worker console for details."
