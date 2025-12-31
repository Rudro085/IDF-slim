import re
from collections import Counter
from itertools import chain
from difflib import SequenceMatcher
import json

# Common English stopwords to exclude
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
    'of', 'on', 'or', 'that', 'the', 'to', 'was', 'will', 'with', 'you', 'your', 'this', 'these',
    'those', 'am', 'have', 'had', 'do', 'does', 'did', 'should', 'could', 'would', 'may', 'might',
    'must', 'can', 'about', 'after', 'before', 'between', 'into', 'through', 'during', 'above',
    'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
}

def extract_phrases(text, ngram_range=(1, 2)):
    """Return a list of normalized n-grams from a transaction details string."""
    
    text = text.lower()
    # Remove multiple spaces but keep special characters like '/', '-', etc.
    # Only remove punctuation that doesn't form part of meaningful phrases
    text = re.sub(r'[^\w\s/-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    tokens = [token for token in text.split() if token and token not in STOPWORDS]
    
    # Generate n-grams (1 = single word, 2 = two-word phrase, etc.)
    ngrams = []
    for n in range(ngram_range[0], ngram_range[1]+1):
        ngrams += [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    return ngrams

def get_frequent_phrases(statement, min_count=5):
    """Get frequent phrases with hierarchy - remove subphrases that are included in longer phrases."""
    counter = Counter()
    
    # First, collect all phrases and their frequencies
    for txn in statement.data:
        phrases = extract_phrases(txn.details)
        # Use set to avoid double-counting same phrase in one detail
        for phrase in set(phrases):
            counter[phrase] += 1
    
    # Filter by minimum count
    frequent = {phrase: count for phrase, count in counter.items() if count >= min_count}
    
    # Create a sorted list of phrases by length (longest first)
    phrases_by_length = sorted(frequent.keys(), key=lambda x: len(x.split()), reverse=True)
    
    # Remove subphrases
    final_phrases = {}
    for phrase in phrases_by_length:
        phrase_words = phrase.split()
        is_subphrase = False
        
        # Check if this phrase is a subphrase of any longer phrase we're keeping
        for longer_phrase in final_phrases.keys():
            longer_words = longer_phrase.split()
            # Check if all words of current phrase appear consecutively in longer phrase
            for i in range(len(longer_words) - len(phrase_words) + 1):
                if longer_words[i:i+len(phrase_words)] == phrase_words:
                    # Check if they appear exactly as a subphrase (not partial matches)
                    subphrase = ' '.join(longer_words[i:i+len(phrase_words)])
                    if subphrase == phrase:
                        is_subphrase = True
                        break
            if is_subphrase:
                break
        
        if not is_subphrase:
            final_phrases[phrase] = frequent[phrase]
    
    return final_phrases

def search_transactions(statement, phrase, threshold=0.9, ngram_range=(1, 3)):
    """Fuzzy-search transactions in `statement` for `phrase`.

    Returns a list of tuples `(txn, score)` sorted by descending score. `score` is
    a similarity between 0 and 1; transactions with score >= `threshold` are returned.

    - `statement` is expected to have an iterable `data` attribute of transactions
      where each transaction exposes a `details` string attribute.
    - `phrase` is the user search phrase (string).
    - `ngram_range` controls phrase-granularity to compare against (1 = unigrams).
    """

    if not phrase or not hasattr(statement, 'data'):
        return []

    # Normalize the search phrase - keep special characters for exact matching
    phrase_norm = phrase.lower().strip()
    # Remove extra spaces but keep the original formatting
    phrase_norm = re.sub(r'\s+', ' ', phrase_norm)
    
    results = []
    for txn in statement.data:
        text = getattr(txn, 'details', str(txn) if txn is not None else '')
        text_norm = text.lower()
        text_norm = re.sub(r'\s+', ' ', text_norm).strip()
        
        # Extract phrases from transaction text
        candidates = extract_phrases(text, ngram_range=ngram_range)
        best_score = 0.0
        
        # First try exact substring matching
        if phrase_norm in text_norm:
            best_score = 1.0
        else:
            # Fall back to fuzzy matching
            for cand in candidates:
                # Sequence similarity on normalized text (without special char removal)
                seq = SequenceMatcher(None, phrase_norm, cand).ratio()
                
                # Token overlap with stopwords removed
                phrase_tokens = set([t for t in phrase_norm.split() if t not in STOPWORDS])
                cand_tokens = set([t for t in cand.split() if t not in STOPWORDS])
                tok_overlap = 0.0
                if phrase_tokens or cand_tokens:
                    tok_overlap = len(phrase_tokens & cand_tokens) / len(phrase_tokens | cand_tokens)
                
                # Weighted score - you can adjust these weights
                score = 0.5 * seq + 0.5 * tok_overlap
                if score > best_score:
                    best_score = score

        if best_score >= threshold:
            results.append((txn, round(best_score, 4)))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)

    # Build JSON-serializable output using txn.to_json() when available
    output = []
    for txn, score in results:
        txn_json = None
        to_json_fn = getattr(txn, 'to_json', None)
        if callable(to_json_fn):
            try:
                txn_json = to_json_fn()
            except Exception:
                txn_json = str(txn)
        else:
            txn_json = str(txn)

        output.append({
            'transaction': txn_json,
            'score': score,
        })

    return json.dumps(output)

def search_transactions_db(db_conn_or_cursor, request_id, statement_id, phrase, threshold=0.6, ngram_range=(1, 3)):
    """Search the `transactions` DB table for a fuzzy match on `phrase`.

    Parameters:
    - `db_conn_or_cursor`: a DB connection (has `cursor()`) or an existing cursor.
    - `request_id`, `statement_id`: filter values for the query.
    - `phrase`: search phrase.
    - `threshold`: minimum score (0-1) to include a row.
    - `ngram_range`: passed to `extract_phrases`.

    Returns a JSON string: list of objects {transaction: <dict>, score: <float>}.
    """

    if not phrase:
        return json.dumps([])

    # Prepare cursor
    close_cursor = False
    if hasattr(db_conn_or_cursor, 'cursor'):
        cursor = db_conn_or_cursor.cursor()
        close_cursor = True
    else:
        cursor = db_conn_or_cursor

    try:
        cursor.execute(
            """SELECT * FROM `transactions` WHERE `request_id` = %s AND `statement_id` = %s""",
            (request_id, statement_id)
        )

        cols = [c[0] for c in cursor.description] if cursor.description else []

        results = []
        # Keep original formatting for search
        phrase_norm = phrase.lower().strip()
        phrase_norm = re.sub(r'\s+', ' ', phrase_norm)
        
        for row in cursor:
            row_dict = dict(zip(cols, row)) if cols else {str(i): v for i, v in enumerate(row)}
            details = row_dict.get('details', '') or ''
            details_norm = details.lower()
            details_norm = re.sub(r'\s+', ' ', details_norm).strip()

            best_score = 0.0
            
            # Try exact substring match first
            if phrase_norm in details_norm:
                best_score = 1.0
            else:
                # Fall back to phrase-based fuzzy matching
                candidates = extract_phrases(details, ngram_range=ngram_range)
                for cand in candidates:
                    seq = SequenceMatcher(None, phrase_norm, cand).ratio()
                    phrase_tokens = set([t for t in phrase_norm.split() if t not in STOPWORDS])
                    cand_tokens = set([t for t in cand.split() if t not in STOPWORDS])
                    tok_overlap = 0.0
                    if phrase_tokens or cand_tokens:
                        tok_overlap = len(phrase_tokens & cand_tokens) / len(phrase_tokens | cand_tokens)
                    score = 0.5 * seq + 0.5 * tok_overlap
                    if score > best_score:
                        best_score = score

            if best_score >= threshold:
                results.append((row_dict, round(best_score, 4)))

        # sort and build final JSON
        results.sort(key=lambda x: x[1], reverse=True)
        out = []
        for row_dict, score in results:
            out.append({
                'transaction': row_dict,
                'score': score,
            })

        return json.dumps(out)
    finally:
        if close_cursor:
            try:
                cursor.close()
            except Exception:
                pass

def extract_meaningful_phrases(statement, min_count=3, min_length=2):
    """Alternative approach: Extract meaningful phrases that represent distinct categories.
    
    This function tries to identify phrases that are meaningful categories by:
    1. Looking at phrase frequency
    2. Filtering out stopwords-heavy phrases
    3. Prioritizing phrases with business meaning
    """
    counter = Counter()
    
    for txn in statement.data:
        # Extract with larger ngram range to capture more context
        phrases = extract_phrases(txn.details, ngram_range=(2, 4))
        for phrase in set(phrases):
            # Skip phrases that are mostly stopwords
            words = phrase.split()
            non_stopwords = [w for w in words if w not in STOPWORDS]
            if len(non_stopwords) >= min_length:
                counter[phrase] += 1
    
    # Filter by minimum count
    frequent = {phrase: count for phrase, count in counter.items() if count >= min_count}
    
    # Sort by frequency and length
    sorted_phrases = sorted(frequent.items(), key=lambda x: (-x[1], -len(x[0].split())))
    
    # Filter out subphrases
    final_phrases = {}
    for phrase, count in sorted_phrases:
        phrase_words = phrase.split()
        is_subphrase = False
        
        for kept_phrase in final_phrases.keys():
            kept_words = kept_phrase.split()
            # Check if this phrase is completely contained in a kept phrase
            if len(phrase_words) < len(kept_words):
                # Try to find consecutive match
                for i in range(len(kept_words) - len(phrase_words) + 1):
                    if kept_words[i:i+len(phrase_words)] == phrase_words:
                        is_subphrase = True
                        break
            if is_subphrase:
                break
        
        if not is_subphrase:
            final_phrases[phrase] = count
    
    return final_phrases