from langdetect import detect
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')


def process_text(text):
    """
    Detect language, tokenize, remove stopwords,
    and return important keywords.
    """

    # Language detection
    lang = detect(text)

    # Tokenization
    tokens = word_tokenize(text.lower())

    # Stopword removal (English only for simplicity)
    if lang == "en":
        stop_words = set(stopwords.words("english"))
        tokens = [word for word in tokens if word not in stop_words]

    return lang, tokens
