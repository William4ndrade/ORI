import sys
import nltk
from nltk.corpus import stopwords
import string

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('mac_morpho')
nltk.download("rslp")
StopWordsInPortuguese = stopwords.words('portuguese')
punctuation = list(string.punctuation) + ['..', '...']


class File:

    def __init__(self, fileName, text, length, id):
        self.id = id
        self.FileName = fileName
        self.Text = text
        self.length = length
        self.token = self.TokenizeText()
        self.RadicalsIndex = dict()
        self.tokenIndex = dict()
        self.Radicals = self.ExtractRadicals()

    def TokenizeText(self):
        return [t for t in nltk.word_tokenize(self.Text) if
                      t.lower() not in StopWordsInPortuguese and t not in punctuation]

    def ExtractRadicals(self):
        current_list = list()
        extract = nltk.stem.RSLPStemmer()
        for x in self.token:
            current_list.append(extract.stem(x))
        return current_list


def ReadBase():
    if len(sys.argv) > 1:
        f = open(sys.argv[1], 'r')
        f.close()
        return f.read().split('\n')
    else:
        raise Exception("Preencha o path da base de pesquisa")


class FilesHandler:
    def __init__(self):
        self.BasePath = 'Resources/base_samba/base_samba'
        self.Extractor =  nltk.stem.RSLPStemmer()
        self.FilesInPath = list()
        self.ReadAllFiles()
        self.AllTokens = self.GetAllTokens()
        self.Radicals = self.GetAllRadicals()
        self.InvertedIndexToken = self.GetInvertedIndexFromToken()
        self.SetRadicalIndex()
       # self.GenerateIndexFile()

    def ReadBase(self):
        if len(sys.argv) > 1:
            f = open(sys.argv[1], 'r')
            return f.read().split('\n')
        else:
            raise Exception("Preencha o path da base de pesquisa")

    def ReadFile(self, fileName, id):
        f = open(self.BasePath + '/' + fileName, 'r')
        text = f.read()
        self.FilesInPath.append(File(fileName, text, len(text), id))

    def ReadAllFiles(self):
        for y, x in enumerate(self.ReadBase()):
            self.ReadFile(x, y+1)

    def GetAllTokens(self):
        all_tokens = set()
        for x in self.FilesInPath:
            [all_tokens.add(t) for t in x.token]
        return all_tokens

    def SetRadicalIndex(self):
        for x in self.FilesInPath:
            for y in self.Radicals:
                count = 0
                if y in x.Radicals:
                    count = x.Radicals.count(y)
                x.RadicalsIndex[y] = count

    def GetInvertedIndexFromToken(self):
        current = dict()
        for y in self.AllTokens:
            current_file = set()
            for x in self.FilesInPath:
                if y in x.token:
                    current_file.add(x.FileName)
            current[y] = current_file
        return current

    def GetAllRadicals(self):
        current = set()
        for x in self.AllTokens:
           r = self.Extractor.stem(x)
           current.add(r)
        return current

    def PrintFiles(self):
        for x in self.FilesInPath:
            print({
                "id": x.id,
                "filename": x.FileName,
                "index": x.RadicalsIndex
            })

    def GenerateIndexFile(self):
        to_file = ''
        for r in self.Radicals:
            to_file += r + ': '
            for file in self.FilesInPath:
                if file.RadicalsIndex[r] > 0:
                    to_file += f'{file.id},{file.RadicalsIndex[r]} '
            to_file += '\n'
        f = open('./Resources/indice.txt', 'w')
        f.write(to_file)
        f.close()
        self.PrintFiles()


class QueryInterpreter:

    def __init__(self):
        self.InvertedIndexToken = FilesHandler().InvertedIndexToken

    def find(self, q):
        query = q.split(' ')
        result = []
        special_chars = ['|', '&']
        for x in range(len(query)):
            if query[x] in special_chars:
                antes = x - 1
                depois = x + 1
                if query[x] == '&':
                    result.append(self.AND(query[antes], query[depois]))
                elif query[x] == '|':
                    result.append(self.OR(query[antes], query[depois]))
        print(result)



    def AND(self, a, b):
        current_a = self.InvertedIndexToken.get(a)
        current_b = self.InvertedIndexToken.get(b)
        return current_a.intersection(current_b)

    def OR(self, a, b):
        current_a = self.InvertedIndexToken.get(a)
        current_b = self.InvertedIndexToken.get(b)
        return current_a.union(current_b)

    def NOT(self, a):
        values = set([t.pop() for t in self.InvertedIndexToken.values()])
        current_a = self.InvertedIndexToken.get(a.replace('!', ''))
        return values.difference(current_a)










QueryInterpreter().find('samba & amor & nao')
