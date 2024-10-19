from newspaper import Article
import re
import pandas as pd 



def clean_text(raw_text):
    """
    Cleans the input text by removing unnecessary spaces, line breaks, 
    and special characters.
    
    Args:
    raw_text (str): The raw input text to clean.
    
    Returns:
    str: The cleaned text.
    """
    # Remove extra spaces and new lines
    cleaned_text = re.sub(r'\s+', ' ', raw_text.strip())
    
    # Optionally, remove special characters (leave only alphanumeric characters and punctuation)
    cleaned_text = re.sub(r'[^\w\s,.?!]', '', cleaned_text)
    
    return cleaned_text


# Function to fetch and extract the title and body of an article
def extract_article_content(url, givenTitle):
    try:
        
        article = Article(url)
        article.download()
        article.parse()

        # Extract title and body
        title = article.title

        if title!=givenTitle:
            return None, f"Error Title mismatch, not searched article."
        body_text = clean_text(article.text)

        return  body_text
    except Exception as e:
        return  f"Error fetching article content: {str(e)}"
    
def table_to_string(df):
    return df.to_string(index=True)