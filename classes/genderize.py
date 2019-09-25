# !/usr/bin/python
# -*- coding: utf-8 -*-

from utils import is_in
from itertools import chain
from nltk import word_tokenize
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer

# ambiguous or often allegorically used terms
EXCLUDE_TERMS = ['god', 'animal', 'model']

TERMS_FEMALE = ['female', 'woman']
TERMS_MALE = ['male', 'man']

CODE_FEMALE, CODE_MALE = '31A72', '31A71'


def _filter_synset(term, not_terms, synsets):
    for synset, gloss, lemmas in synsets:
        if (
                is_in(term, gloss) or
                is_in(term, lemmas)
        ) and not (
                is_in(not_terms, gloss) or
                is_in(not_terms, lemmas)
        ):
            yield synset, gloss, lemmas


def _get_hypernyms(synset):
    hypernyms = synset.hyponyms()

    if len(hypernyms) > 0:
        for synset in hypernyms:
            yield from _get_hypernyms(synset)
            yield synset


def _query_synset(synset_name):
    synset = wordnet.synset(synset_name)

    for synset in _get_hypernyms(synset):
        gloss = word_tokenize(synset.definition().lower())

        if not is_in(['informal', 'slang', 'gossip'], gloss):
            lemmas = [
                lemma.replace('_', ' ').lower()
                for lemma in synset.lemma_names()
            ]

            yield synset, gloss, lemmas


def _get_lemmas(synsets):
    lemmas = [lemmas for _, _, lemmas in synsets]

    return set(chain.from_iterable(lemmas))


def _get_person_lemmas(terms, not_terms):
    synsets = _filter_synset(
        terms, not_terms, _query_synset('person.n.01')
    )

    lemmas = _get_lemmas(synsets).difference(
        _get_lemmas(_query_synset('animal.n.01'))
    )

    lemmas.update(terms)  # add pre-specified terms

    return lemmas


def get_females():
    return _get_person_lemmas(TERMS_FEMALE, TERMS_MALE)


def get_males():
    return _get_person_lemmas(TERMS_MALE, TERMS_FEMALE)


def get_anti(code):
    if code == CODE_FEMALE:
        return CODE_MALE
    elif code == CODE_MALE:
        return CODE_FEMALE


class Genderize:
    _females = get_females()
    _males = get_males()

    def __init__(self, document):
        self.terms = [
            WordNetLemmatizer().lemmatize(word)
            for word in word_tokenize(document)
        ]

        self.code = self._get_code()

    def _is_female(self):
        if is_in(self.terms, self._females) and not \
                is_in(self.terms, TERMS_MALE):
            return True

        return False

    def _is_male(self):
        if is_in(self.terms, self._males) and not \
                is_in(self.terms, TERMS_FEMALE):
            return True

        return False

    def _get_code(self):
        if not is_in(self.terms, EXCLUDE_TERMS):
            if self._is_female():
                return CODE_FEMALE
            elif self._is_male():
                return CODE_MALE
