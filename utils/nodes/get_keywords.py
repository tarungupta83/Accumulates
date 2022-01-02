import os

from keybert import KeyBERT

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def get_keywords(text: str, quantity: int):
    model = KeyBERT("distilbert-base-nli-mean-tokens")
    keywords = model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        use_maxsum=True,
        use_mmr=True,
        diversity=0.7,
        top_n=quantity,
    )
    return [i[0] for i in keywords]


if __name__ == "__main__":
    text = """Although there are already many methods available for keyword generation (e.g., Rake, YAKE!, TF-IDF, etc.) I wanted to create a very basic, but powerful method for extracting keywords and keyphrases. This is where KeyBERT comes in! Which uses BERT-embeddings and simple cosine similarity to find the sub-phrases in a document that are the most similar to the document itself. First, document embeddings are extracted with BERT to get a document-level representation. Then, word embeddings are extracted for N-gram words/phrases. Finally, we use cosine similarity to find the words/phrases that are the most similar to the document. The most similar words could then be identified as the words that best describe the entire document. KeyBERT is by no means unique and is created as a quick and easy method for creating keywords and keyphrases. Although there are many great papers and solutions out there that use BERT-embeddings (e.g., 1, 2, 3, ), I could not find a BERT-based solution that did not have to be trained from scratch and could be used for beginners (correct me if I'm wrong!). Thus, the goal was a pip install keybert and at most 3 lines of code in usage.To diversity the results, we take the 2 x top_n most similar words/phrases to the document. Then, we take all top_n combinations from the 2 x top_n words and extract the combination that are the least similar to each other by cosine similarity."""

    print(get_keywords(text))
