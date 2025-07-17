# tasks.py

from urllib.parse import urlparse
from analyzer import (
    get_article_details, analyze_text_sentiment, calculate_reading_time, 
    extract_named_entities, perform_global_cross_reference, get_gemini_analysis,
    detect_language
)
from celery_worker import celery_app
from app import db, Source

@celery_app.task
def run_analysis(url):
    """The main analysis task for URLs, now language-aware."""
    analysis_result = {}
    domain = urlparse(url).netloc.replace('www.', '')
    analysis_result['domain'] = domain
    source_info = Source.query.filter_by(domain=domain).first()
    analysis_result['source_check'] = f"{source_info.rating} (Bias: {source_info.bias})" if source_info else "Source not in our list. Use caution."
    
    details = get_article_details(url)
    if not details or not details['text']: 
        return {'error': 'Could not extract article content. Please ensure it is a valid article URL.'}
    
    analysis_result.update(details)
    text_content = details['text']
    lang = detect_language(text_content)
    analysis_result['language'] = lang
    
    analysis_result['sentiment'] = analyze_text_sentiment(text_content, lang=lang)
    analysis_result['reading_time'] = calculate_reading_time(text_content)
    analysis_result['named_entities'] = extract_named_entities(text_content, lang=lang)
    analysis_result['cross_references'] = perform_global_cross_reference(details['title']) if details['title'] else {'error': 'Article title not found.'}
    analysis_result['gemini_analysis'] = get_gemini_analysis(text_content)
    
    db.session.remove()
    return analysis_result
