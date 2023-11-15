# BERT模型差異與特徵向量調整 

## 專案概述

探討HuggingFace實現的TFBertModel與TFBertForSequenceClassification之間的差異，以及如何使用TFBertModel並自行串接分類器實現特定的特徵向量。

## 模型差異

- **TFBertModel：**
  - 實現了BERT模型，但沒有串接分類器。

- **TFBertForSequenceClassification：**
  - 在BERT模型輸出之後，串接了一個分類器。

## base code -1

- **情感分析範例：**
  - [sentiment_analysis_using_TFBertForSequenceClassification.py](example/sentiment_analysis_using_TFBertForSequenceClassification.py)
  - 使用TFBertForSequenceClassification進行SST-2影評文本集的分類工作。

## base code -2

- **更改TFBertForSequenceClassification內訓練其分類器的輸入向量：**
  - [更改TFBertForSequenceClassification內訓練其分類器的輸入向量.py](example/更改TFBertForSequenceClassification內訓練其分類器的輸入向量.py) 
  - 提供了兩種調整特徵向量的方法：
    - a) 使用輸入樣本的所有輸出hidden_state vectors的平均作為特徵向量。
    - b) 使用輸入樣本的第2個輸出hidden_state vector作為特徵向量。

## Task

使用TFBertModel，自行串接二元分類器，implement上述兩種特徵向量的調整：

a) 使用輸入樣本的所有輸出hidden_state vectors的平均作為特徵向量。

b) 使用輸入樣本的第2個輸出hidden_state vector作為特徵向量。
