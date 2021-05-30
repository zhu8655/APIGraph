import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import keras
import keras_metrics as km
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from keras.preprocessing.text import Tokenizer
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import SpatialDropout1D
from mlxtend.plotting import plot_confusion_matrix

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
import numpy as np
from sklearn.metrics import recall_score,accuracy_score
from sklearn.metrics import precision_score,f1_score
from keras.optimizers import Adam,SGD,sgd
from keras.models import load_model

from sklearn.neighbors import KNeighborsClassifier


dirName = "base"
typeName = "Adware"


malware_calls_df = pd.read_csv("calls_" + dirName + ".zip",
                                compression="zip",
                                sep="\t",
                                names=["API_Calls"])
malware_labels_df = pd.read_csv("types.zip",
                                compression="zip",
                                sep="\t",
                                names=["API_Labels"])
malware_calls_df["API_Calls"] = malware_calls_df.API_Calls.apply(
    lambda x: " ".join(x.split(",")))


malware_calls_df["API_Labels"] = malware_labels_df.API_Labels
malware_calls_df["API_Labels"] = malware_calls_df.API_Labels.apply(
    lambda x: 1 if x == typeName else 0)

##########################################################################

max_words = 800
max_len = 100

X = malware_calls_df.API_Calls
Y = malware_calls_df.API_Labels.astype('category').cat.codes

tok = Tokenizer(num_words=max_words)
tok.fit_on_texts(X)
print('Found %s unique tokens.' % len(tok.word_index))
X = tok.texts_to_sequences(X.values)
X = sequence.pad_sequences(X, maxlen=max_len)
print('Shape of data tensor:', X.shape)

X_train, X_test, Y_train, Y_test = train_test_split(X,
                                                    Y,
                                                    test_size=0.25)

##########################################################################

print('########## ' + dirName + "/" + typeName + ' ##########')

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, Y_train)

y_test_pred0 = knn.predict(X_test)

fpr, tpr, thresholds_keras = roc_curve(Y_test, y_test_pred0)
auc_val = auc(fpr, tpr)
print("AUC : ", auc_val)
plt.figure()
plt.plot([0, 1], [0, 1], 'k--')
plt.plot(fpr, tpr, label='(AUC = {:.3f})'.format(auc_val))
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('ROC curve')
plt.legend(loc='best')
plt.show()