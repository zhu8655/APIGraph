# 基于API知识图谱的恶意软件家族分类技术的研究与实现

## Reference

* APIGraph：https://github.com/seclab-fudan/APIGraph

* 数据集：https://github.com/ocatak/malware_api_class

* 分类器：https://github.com/ocatak/lstm_malware_detection

## 环境配置

* python 3.6
* TensorFlow 1.x
* selenium
* chromeWebDriver

## 代码结构 && 执行顺序

* `sele_entity.py`：爬虫程序
* `get_entity.py`：预处理获取所有实体
* `get_releation.py`：预处理获取所有关系
* `transE.py`：嵌入表达
* `clusterEmbedding.py`：KMeans聚类
* `gen_dataset.py`：生成ApiGraph增强数据集
* `LSTM.py`：LSTM分类器
* `knn_svm.py`：基础分类器

## Note

原数据集较大未加入本仓库中，详细见Reference