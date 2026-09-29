"""Duplicate detection and claim similarity analysis service.
Identifies whether incoming claims match previously verified reports
to prevent redundant analysis, detect viral misinformation clusters,
and track recurrence across geographic hotspots.
"""
import re
from typing import Tuple, Optional, Dict, Any, List
from services.db import get_all_reports

def normalize_text(text: str) -> str:
    """Normalize text by lowercasing, removing special chars and excessive whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return " ".join(text.split())

def _jaccard_similarity(text1: str, text2: str) -> float:
    """Fallback word-level Jaccard similarity metric."""
    words1 = set(normalize_text(text1).split())
    words2 = set(normalize_text(text2).split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

def check_duplicate_claim(
    input_text: str,
    threshold: float = 0.70,
    existing_reports: Optional[List[Dict[str, Any]]] = None
) -> Tuple[bool, float, Optional[Dict[str, Any]], int]:
    """
    Check if the incoming input_text is a duplicate or near-duplicate of an existing report.
    
    Returns:
        (is_duplicate, max_similarity, best_match_dict, cluster_count)
    """
    clean_input = normalize_text(input_text)
    if not clean_input:
        return False, 0.0, None, 0

    if existing_reports is None:
        try:
            existing_reports = get_all_reports()
        except Exception:
            existing_reports = []

    if not existing_reports:
        return False, 0.0, None, 0

    corpus = [normalize_text(r.get("input_text", "")) for r in existing_reports]
    
    best_similarity = 0.0
    best_match = None
    cluster_count = 0

    # Try TF-IDF cosine similarity first if scikit-learn is present
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        all_texts = [clean_input] + corpus
        vectorizer = TfidfVectorizer(ngram_range=(1, 1), stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        for idx, sim in enumerate(similarities):
            # Hybrid blend: TF-IDF cosine similarity + token Jaccard similarity
            j_sim = _jaccard_similarity(clean_input, corpus[idx])
            hybrid_sim = max(float(sim), j_sim)
            if hybrid_sim >= 0.50:
                cluster_count += 1
            if hybrid_sim > best_similarity:
                best_similarity = hybrid_sim
                best_match = existing_reports[idx]
    except Exception:
        # Graceful fallback to Jaccard similarity if scikit-learn is unavailable
        for idx, ref_text in enumerate(corpus):
            sim = _jaccard_similarity(clean_input, ref_text)
            if sim >= 0.50:
                cluster_count += 1
            if sim > best_similarity:
                best_similarity = sim
                best_match = existing_reports[idx]

    is_duplicate = best_similarity >= threshold
    return is_duplicate, round(best_similarity, 3), best_match, cluster_count
