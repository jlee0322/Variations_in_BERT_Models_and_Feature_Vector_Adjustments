# -*- coding: utf-8 -*-
"""sentiment_analysis_自己實現分類class_可用平均或自定義token.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VNtiiOJh27CoUAKswGwUXR2Ym-I8qucN
"""

!pip install transformers

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from transformers import (
    BertTokenizer,
    TFBertMainLayer,
    TFBertPreTrainedModel,    
)

tf.random.set_seed(42)


#讀入SST-2影評文本集, 並對輸入文字序列進行預處理

data_source = "https://github.com/clairett/pytorch-sentiment-classification/raw/master/data/SST2/train.tsv"
df = pd.read_csv(data_source, delimiter="\t", header=None)
df.rename(columns={0: "reviews", 1: "label"}, inplace=True)


smaller_batch = df[:2000]

label_series = smaller_batch["label"]

model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)

tokenized = smaller_batch["reviews"].apply(
    (lambda review: tokenizer.encode(review, add_special_tokens=True))
)


max_len = np.max([len(tokenized_review) for tokenized_review in tokenized])
min_len = np.min([len(tokenized_review) for tokenized_review in tokenized])
avg_len = np.mean([len(tokenized_review) for tokenized_review in tokenized])
print("The length of the longest review:", max_len)
print("The length of the shortest review:", min_len)
print("The average length of all the reviews:", avg_len)

shortest_reviews = [
    tokenized_review for tokenized_review in tokenized if len(tokenized_review) == min_len
]
print(shortest_reviews, "\n")
for review in shortest_reviews:
    print(tokenizer.convert_ids_to_tokens(review, skip_special_tokens=False))

padded_ids = np.array([i + [0] * (max_len - len(i)) for i in tokenized.values])
attention_mask = np.where(padded_ids != 0, 1, 0)


label = label_series.to_numpy()
label = to_categorical(label, num_classes=2)


#更改TFBertForSequenceClassification類別其內訓練分類器所使用的輸入向量
#使用輸入樣本的所有輸出hidden_state vectors的平均作為特徵向量

class TFBertForSequenceClassification(TFBertPreTrainedModel):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.bert = TFBertMainLayer(config, name="bert")
        self.dropout = tf.keras.layers.Dropout(config.hidden_dropout_prob)
        self.classifier = tf.keras.layers.Dense(config.num_labels)

    def call(self, inputs, **kwargs):
        outputs = self.bert(inputs, **kwargs)
        last_hidden_state = outputs.last_hidden_state
        # 平均特徵
        pooled_output = tf.math.reduce_mean(last_hidden_state, axis=1)  
        # print("pooled_output.shape", pooled_output.shape)  # batch_size * 768

        pooled_output = self.dropout(
            pooled_output, training=kwargs.get("training", False)
        )
        logits = self.classifier(pooled_output)
        
        return {'logits': logits}



model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=5e-5),
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    metrics=["accuracy"],
)


#inputs = (padded_ids, attention_mask)
#history = model.fit(inputs, label, batch_size=32, epochs=10, validation_split=0.2)

inputs = (padded_ids, attention_mask) 
outputs = {'logits': label}

history = model.fit(inputs, outputs, batch_size=32, epochs=10, validation_split=0.2 )

# %%
plt.figure(figsize=(8, 5))
plt.plot(history.history["accuracy"], label="acc")
plt.plot(history.history["val_accuracy"], label="val_acc")
plt.grid(True)
plt.xlabel("Epochs")
plt.ylabel("Acc")
plt.title("Reduce mean")
plt.legend()
plt.show()


#-----------------------------------------------------------------------------

#更改TFBertForSequenceClassification類別其內訓練分類器所使用的輸入向量
#使用輸入樣本的 第token_index個 輸出hidden_state vector作為特徵向量
 
class TFBertForSequenceClassification(TFBertPreTrainedModel):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.token_index = 0  # token_index:0 代表[CLS] token
        self.bert = TFBertMainLayer(config, name="bert")
        self.dropout = tf.keras.layers.Dropout(config.hidden_dropout_prob)
        self.classifier = tf.keras.layers.Dense(config.num_labels)

    def call(self, inputs, **kwargs):
        outputs = self.bert(inputs, **kwargs)
        last_hidden_state = outputs.last_hidden_state
        # 取[CLS] token特徵
        pooled_output = last_hidden_state[:, self.token_index]
        # print("pooled_output.shape", pooled_output.shape)  # batch_size * 768

        pooled_output = self.dropout(
            pooled_output, training=kwargs.get("training", False)
        )
        logits = self.classifier(pooled_output)
        
        return {'logits': logits}


model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased")
model.token_index = 2 # 在130行預設是[CLS] token, 我們可以在這裡改為其它的

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=5e-5),
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    metrics=["accuracy"],
)


#inputs = (padded_ids, attention_mask)
#history = model.fit(inputs, label, batch_size=32, epochs=10, validation_split=0.2)

inputs = (padded_ids, attention_mask) 
outputs = {'logits': label}

history = model.fit(inputs, outputs, batch_size=32, epochs=10, validation_split=0.2 )

# %%
plt.figure(figsize=(8, 5))
plt.plot(history.history["accuracy"], label="acc")
plt.plot(history.history["val_accuracy"], label="val_acc")
plt.grid(True)
plt.xlabel("Epochs")
plt.ylabel("Acc")
plt.title("[CLS]")
plt.legend()
plt.show()