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

epochsize = 10
useNewModel = False
saveModel = False

dirNames = ["base", "apigraph"]
typeNames = [
    "Spyware", "Downloader", "Trojan", "Worms", "Adware", "Dropper", "Virus",
    "Backdoor"
]

for dirName in dirNames:

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

    for typeName in typeNames:
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

        le = LabelEncoder()
        Y_train_enc = le.fit_transform(Y_train)
        Y_train_enc = np_utils.to_categorical(Y_train_enc)

        Y_test_enc = le.transform(Y_test)
        Y_test_enc = np_utils.to_categorical(Y_test_enc)

        ##########################################################################


        def malware_model(act_func="softsign"):
            model = Sequential()
            model.add(Embedding(max_words, 300, input_length=max_len))
            model.add(SpatialDropout1D(0.1))
            model.add(
                LSTM(32,
                     dropout=0.1,
                     recurrent_dropout=0.1,
                     return_sequences=True,
                     activation=act_func))
            model.add(
                LSTM(32,
                     dropout=0.1,
                     activation=act_func,
                     return_sequences=True))
            model.add(LSTM(32, dropout=0.1, activation=act_func))
            model.add(Dense(128, activation=act_func))
            model.add(Dropout(0.1))
            model.add(Dense(256, activation=act_func))
            model.add(Dropout(0.1))
            model.add(Dense(128, activation=act_func))
            model.add(Dropout(0.1))
            model.add(Dense(1, name='out_layer', activation="linear"))
            return model

        if useNewModel:
            model = malware_model()
            model.compile(
                loss='mse',
                optimizer="adam",
                metrics=['accuracy',
                         km.f1_score(),
                         km.binary_recall()])
        else:
            model = keras.models.load_model(
                "./" + dirName + "/" + typeName + '_model_.h5',
                custom_objects={
                    "binary_f1_score": km.f1_score(),
                    "binary_recall": km.binary_recall()
                })

        print('########## ' + dirName + "/" + typeName + ' ##########')
        # print(model.summary())

        # filepath = "lstm-malware-model.hdf5"
        # model.load_weights(filepath)

        # history = model.fit(
        #     X_train,
        #     Y_train,
        #     batch_size=1024,
        #     epochs=epochsize,  # TODO
        #     validation_data=(X_test, Y_test),
        #     verbose=1)

        ##########################################################################

        # y_test_pred = model.predict_classes(X_test)
        # cm = confusion_matrix(Y_test, y_test_pred)

        # plot_confusion_matrix(conf_mat=cm,
        #                       show_absolute=True,
        #                       show_normed=True,
        #                       colorbar=True)
        # # plt.savefig("./" + dirName + "/" + typeName + "_confusion_matrix.png")
        # plt.show()

        # ##########################################################################

        # plt.plot(history.history['accuracy'])
        # plt.plot(history.history['val_accuracy'])
        # plt.title('model accuracy')
        # plt.ylabel('accuracy')
        # plt.xlabel('epoch')
        # plt.legend(['train', 'test'], loc='upper left')
        # plt.grid()
        # # plt.savefig("./" + dirName + "/" + typeName + "_accuracy.png")
        # # plt.show()

        # plt.plot(history.history['loss'])
        # plt.plot(history.history['val_loss'])
        # plt.title('model loss')
        # plt.ylabel('loss')
        # plt.xlabel('epoch')
        # plt.legend(['train', 'test'], loc='upper left')
        # plt.grid()
        # # plt.savefig("./" + dirName + "/" + typeName + "_loss.png")
        # # plt.show()

        # if saveModel:
        #     model.save("./" + dirName + "/" + typeName + '_model_.h5')

        y_test_pred0 = model.predict(X_test)

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