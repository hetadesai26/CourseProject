import gensim
from gensim import corpora, models
from nltk.tokenize import RegexpTokenizer
from gensim.corpora.textcorpus import TextCorpus
from gensim.corpora.textcorpus import remove_short,remove_stopwords
import numpy as np
import itertools

def preprocessData():
    tokenizer = RegexpTokenizer(r'\w+')
    f = open("Data/BushGore.txt", "r")
    documents = []
    datedocument = {}
    i = 0
    for x in f:
        line = x
        dateline = line.split(":")
        document = dateline[1].lower()
        duplicate = documents.count(tokenizer.tokenize(document))
        
        arr = []
        date = dateline[0]
        if datedocument.get(date)!=None:
            arr = datedocument.get(date)
        arr.append(i)
        datedocument[date] = arr
        if duplicate == 0:
            if "bush" in document or "gore" in document:
                documents.append(tokenizer.tokenize(document))
                i=i+1
        
    dictionary = corpora.Dictionary(documents)
    #print(len(documents))
    corpus = [dictionary.doc2bow(remove_short(remove_stopwords(text),minsize = 2)) for text in documents]
    return corpus,datedocument,dictionary

def readStockPrice():
    goreNormalizedProbability = {}
    with open( 'Data/StockPrices.txt' ) as f:
        for line1, line2, line3 in itertools.zip_longest( *[f] * 3 ):
            dem = line1.split()
            rep = line3.split()
            denominator = float( dem[-1] ) + float( rep[-1] )
            date = dem[0]
            normProb = float( dem[-1] ) / denominator
            goreNormalizedProbability.update( {date: normProb} )
    return goreNormalizedProbability

def runLda(corpus,ntopics,dictionary):
    model = gensim.models.LdaModel(corpus, id2word=dictionary,
                               alpha='auto',
                               num_topics=ntopics,
                               passes=5)
    return model
    
def calculateTs(model,datedocument,number_topics,corpus):
    dates = datedocument.keys()
    doc_ids = []
    topics_str = []
    i = 0
    TS = np.zeros((len(dates),number_topics))
    i = 0
    for x in dates:
        doc_ids = datedocument.get(x)
        for k in doc_ids:
            topics_str = model.get_document_topics(corpus)[k]
            for y in topics_str:
                topic_index = y[0]
                topic_prob = y[1]
                TS[i][topic_index] = TS[i][topic_index] + topic_prob
        i = i + 1
    return TS
                      
def main():
    corpus,datedocument,dictionary = preprocessData()
    #print(len(corpus))
    #print(datedocument)
    goreNormProbability = readStockPrice()
    #print( goreNormProbability )
    number_topics = 10
    model = runLda(corpus,number_topics,dictionary)
    print(model.get_topics())
    print(model.print_topics())
    TS = calculateTs(model,datedocument,number_topics,corpus)
    print(TS)
    runGrangerTest()
    

if __name__ == "__main__":
    main()