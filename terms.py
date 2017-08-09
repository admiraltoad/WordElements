import json
import random
import os, sys

class SequenceDied(Exception):
    pass
class SequenceCached(Exception):
    pass
class AttemptsExpired(Exception):
    pass
class AttemptsExpired(Exception):
    pass

class TermsManager():
    def __init__(self):
        self.filePath = os.path.join(os.path.dirname(sys.argv[0]), "data.json")
        self.data = {}
        self.cache = []
        self.load()

    def load(self):
        with open(self.filePath, 'r') as file:
            self.data = json.load(file)

    def save(self):
        with open(self.filePath, 'w') as file:
            json.dump(self.data, file)

    def terms(self):
        return list(self.data.keys())

    def links(self, term):
        try:
            return self.data[term]
        except:
            return []

    def add(self, term, link):
        if term not in self.terms():
            self.data[term] = [link]
        else:
            if link not in self.data[term]:
                self.data[term].append(link)

    def delete(self, term, link=None):
        if term in self.data:
            if not link:
                del self.data[term]
                for _, links in self.data.items():
                    if term in links:
                        links.remove(term)
            else:
                self.data[term].remove(link)
                if not self.data[term]:
                    del self.data[term]

    def sequence(self, length=4, attempts=3000, skipCached=True, addToCache=True):
        attempt = 0
        while attempt < attempts:
            attempt += 1
            seq = []   
            terms = self.terms()
            while len(seq) < length:     
                if not terms:
                    break     
                seq.append(terms[random.randint(0, len(terms) - 1)])
                terms = [term for term in self.links(seq[-1]) if term not in seq]
                if len(seq) < length - 1:
                    terms = [term for term in terms if term in self.terms()]
            if len(seq) < length:
                continue
            if skipCached and seq in self.cache:
                continue
            if addToCache and seq not in self.cache:
                self.cache.append(seq)
            return seq
        raise AttemptsExpired()

if __name__ == '__main__':   
    print(sys.argv)