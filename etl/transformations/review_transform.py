import pandas as pd
import numpy as np

def transform_reviews(raw_reviews_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms reviews dataset into fact_reviews:
    1. Handles duplicate review IDs and multi-review orders via composite PK (review_id, order_id).
    2. Safely handles missing comment titles and text messages.
    3. Derives sentiment polarity heuristic and text lengths.
    4. Calculates response delay in hours.
    """
    rev = raw_reviews_df.copy()

    # Parse timestamps
    rev['review_creation_date'] = pd.to_datetime(rev['review_creation_date'], errors='coerce')
    rev['review_answer_timestamp'] = pd.to_datetime(rev['review_answer_timestamp'], errors='coerce')

    # Comment text indicators
    rev['has_comment_text'] = rev['review_comment_message'].notna() & (rev['review_comment_message'].str.strip() != '')
    rev['comment_length_chars'] = rev['review_comment_message'].fillna('').astype(str).str.len()

    # Sentiment heuristic based on review score (1-2: Negative, 3: Neutral, 4-5: Positive)
    rev['sentiment_label'] = np.where(
        rev['review_score'] >= 4, 'Positive',
        np.where(rev['review_score'] == 3, 'Neutral', 'Negative')
    )
    rev['sentiment_score'] = (rev['review_score'] / 5.0).round(4)

    # Response delay hours
    creation = rev['review_creation_date']
    answer = rev['review_answer_timestamp']
    rev['response_delay_hours'] = np.where(
        answer.notna() & creation.notna(),
        ((answer - creation).dt.total_seconds() / 3600.0).round(2),
        np.nan
    )

    # Clean duplicates on composite key (review_id, order_id)
    rev = rev.drop_duplicates(subset=['review_id', 'order_id'], keep='first')

    fact_reviews = pd.DataFrame({
        'review_id': rev['review_id'],
        'order_id': rev['order_id'],
        'review_score': rev['review_score'].astype(int),
        'review_comment_title': rev['review_comment_title'],
        'review_comment_message': rev['review_comment_message'],
        'has_comment_text': rev['has_comment_text'],
        'comment_length_chars': rev['comment_length_chars'],
        'sentiment_label': rev['sentiment_label'],
        'sentiment_score': rev['sentiment_score'],
        'review_creation_date': rev['review_creation_date'].dt.date,
        'review_answer_timestamp': rev['review_answer_timestamp'],
        'response_delay_hours': rev['response_delay_hours']
    })

    return fact_reviews
