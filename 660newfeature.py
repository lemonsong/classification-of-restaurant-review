
"""
A simple script that demonstrates how we classify textual data with sklearn.
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn import svm 
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix
from numpy import array
import re
import pylab as pl
from nltk.stem.porter import *
import nltk.stem

def loadLexicon(fname):
    newLex=set()
    lex_conn=open(fname)
    for line in lex_conn:
        newLex.add(line.strip())
    lex_conn.close()
    return newLex

posLex=loadLexicon('positive-words.txt')
negLex=loadLexicon('negative-words.txt')
negationTerms=loadLexicon('negation.txt')
numberpos=loadLexicon('numberpositive.txt')
numberneg=loadLexicon('numbernegative.txt')
english_stemmer = nltk.stem.SnowballStemmer('english')
# combine CountVectorizer with english_stemmer
class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))

# if a sentence contains 'but', just remain the 'but' part
def changebutsentence(review):#review is a line of review, str type
    sentences=review.strip().split('.')
    review1=""
    for sentence in sentences:
        parts=sentence.split('but')
        but=str(parts[len(parts)-1])
        review1=review1+but
    return review1
  
# if a sentence begin with 'if', delete the part containing if  
def changeifsentence(review):#review is a line of review, str type
    sentences=review.strip().split('.')
    review2=""
    for sentence in sentences:
        if sentence[0:2]=="if":
            parts=sentence.split(',')
            ifpart=str(parts[len(parts)-1])
        else:
            ifpart=sentence
        review2=review2+ifpart
    return review2
    
# check not+(a+b+)neg/pos
def changenotwords(words):#words is a list of words, list type
    for i in range(0,len(words)):
        if i<(len(words)-2):      
            if words[i] in negationTerms:
                if words[i+1] in posLex:
                    words[i]='terrible'
                    del words[i+1]
                elif words[i+1] in negLex:
                    words[i]='amazing'
                    del words[i+1]
                elif i<(len(words)-3):
                    if len(words[i+1])<5 and words[i+2] in posLex:
                        words[i]='terrible'
                        del words[i+1:i+3]
                    elif len(words[i+1])<5 and words[i+2] in negLex:
                        words[i]='amazing'
                        del words[i+1:i+3]
                    elif i<(len(words)-4):
                        if len(words[i+2])<5 and words[i+3] in posLex:
                            words[i]='terrible'
                            del words[i+1:i+4]
                        elif len(words[i+2])<5 and words[i+3] in negLex:
                            words[i]='amazing'
                            del words[i+1:i+4]
    return words
    

def changenumwords(words):#words is a list of words, list type
    for i in range(0,len(words)-2):
        # change number+star(s)
        if words[i+1] in ['star','stars']:
            if words[i] in ['1','2','one','two','no']:
                words[i+1]='terrible'
            elif words[i] in ['4','5','four','five']:
                words[i+1]='amazing'
        # change numer+certain words, eg.minutes, napkin,club...
        try:
            changetonum=int(words[i])
            if words[i+1] in numberpos:
                words[i+1]='numberpositive'
            elif words[i+1] in numberneg:
                words[i+1]='numbernegative'
        except ValueError:
            continue
        
    return words


def loadReviews(fname):
    reviews=[]
    polarities=[]
    new_train=[]
    f=open(fname)
    negnum=0
    posnum=0
    length=0
    for line in f:
        review,rating=line.strip().split('\t')
        review=review.lower()
        # change $ to dollardollar
        #review=re.sub('\d+\$',"dollardollar",review) 
        #review=re.sub('\$\d+',"dollardollar",review)
        review_feature=review.strip().split()
        for word in review_feature:
            if word in negLex:
                negnum=negnum+1
            elif word in posLex:
                posnum=posnum+1
        length=len(review_feature)
        new_train.append(str(negnum)+' '+str(posnum)+' '+str(length))
        
        review=changeifsentence(changebutsentence(review))
        words=review.strip().split()
        words=changenumwords(changenotwords(words))
        new=' '.join(words)
        reviews.append(new)
        polarities.append(int(rating))
    f.close()
    
    return reviews,polarities,new_train



rev_train,pol_train,newfeature_train=loadReviews('ot_train20000another copy 2.txt')
rev_test,pol_test,newfeature_test=loadReviews('testFile4.txt')
        
 
counter = CountVectorizer(min_df=1,ngram_range=(1, 2)) #(1,6)is best, for convenience, choose 1,3
#counter = StemmedCountVectorizer(min_df=1,ngram_range=(1, 3)) #(1,6)is best, for convenience, choose 1,3
transformer = TfidfTransformer()

counts_train = counter.fit_transform(rev_train)
transformed_train = transformer.fit_transform(counts_train)

counts_test=counter.transform(rev_test)
transformed_test=transformer.transform(counts_test)

counts_newfeature=counter.transform(newfeature_train)
transformed_newfeature=transformer.transform(counts_newfeature)



clf1=LogisticRegression()
clf2=MultinomialNB(alpha=0.01)
clf3=KNeighborsClassifier(n_neighbors=35,metric='euclidean')
clf4=LogisticRegression()
clf5=MultinomialNB(alpha=0.01)

#clf2=MultinomialNB(alpha=0.01)
#clf3=KNeighborsClassifier(n_neighbors=8,metric='euclidean')

clfs=[clf1,clf2,clf3,clf4,clf5]


for i in range(0,3):
    clfs[i].fit(transformed_train,pol_train)
for i in range(3,5):
    clfs[i].fit(transformed_newfeature,pol_train)
    
c1=clfs[0].predict(transformed_test)
c2=clfs[1].predict(transformed_test)
c3=clfs[2].predict(transformed_test)
c4=clfs[3].predict(transformed_newfeature)
c5=clfs[4].predict(transformed_newfeature)
n=0

fst=[]
for i in range(0,len(pol_test)):
    sts=[]
    sts.append(c1[i])
    sts.append(c2[i])
    sts.append(c3[i])
    sts.append(c4[i])
    sts.append(c5[i])

    
    if sts.count(0)>sts.count(1):
        fst.append(0)
    else:
        fst.append(1)
    
    if fst[i] is pol_test[i]:
        n=n+1

facc= (n*100*1.0/len(fst))

print 'ACCURACY:\t',str(facc)+'%'
print 'PREDICTED:\t',array(fst)
print 'CORRECT:\t', array(pol_test)
