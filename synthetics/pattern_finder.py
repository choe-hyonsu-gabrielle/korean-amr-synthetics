from synthetics.main import load_corpus
from synthetics.finders.bigram import BigramPatternFinder


if __name__ == '__main__':
    # macOS: '/Users/choe.hyonsu.gabrielle/modu-corenlp-essential/layers-complete/*/*.json'

    search_space = 'D:/Corpora & Language Resources/modu-corenlp/layers-complete/*/*.json'
    corpus = load_corpus(data_files=search_space)

    finder = BigramPatternFinder(corpus)
