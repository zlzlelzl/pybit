# %%
import pandas as pd
from sklearn.datasets import load_breast_cancer
import numpy as np
import mglearn
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.datasets import make_moons

# X, y = make_classification(n_samples=1000, n_features=4,
#                            n_informative=2, n_redundant=0,
#                            random_state=0, shuffle=False)
# X, y = make_moons(n_samples=1000,
#                   noise=0.1,
#                   #   , n_features=4,
#                   #   n_informative=2,
#                   #   n_redundant=0,
#                   random_state=1, shuffle=False)
# model = RandomForestClassifier(n_estimators=5, max_depth=2, random_state=0)
# model.fit(X, y)
# RandomForestClassifier(...)
# print(clf.predict([[0, 0]]))
# 모델 학습

# 결정 경계 시각화
# 다섯 개의 결정트리 결정 경계
# fig, axes = plt.subplots(2, 3, figsize=(20, 10))
# for i, (ax, tree) in enumerate(zip(axes.ravel(), model.estimators_)):
#     ax.set_title("tree {}".format(i))
#     mglearn.plots.plot_tree_partition(X, y, tree, ax=ax)

# # 랜덤포레스트로 만들어진 결정경계
# axes[-1, -1].set_title("Random forest")
# mglearn.plots.plot_2d_separator(
#     model, X, fill=True, alpha=0.5, ax=axes[-1, -1])
# mglearn.discrete_scatter(X[:, 0], X[:, 1], y)

# %%
# plt.plot(y)
# # %%
# clf
# # %%
# a, b = [], []
# for i in X:
#     a.append(i[0])
#     b.append(i[1])

# plt.scatter(a, b)
# 데이터 로드
X, y = make_moons(n_samples=1000, noise=0.25, random_state=3)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=42)

# X가 xy좌표, y가 True False

# 모델 학습
model = RandomForestClassifier(n_estimators=5, random_state=0)
model.fit(X_train, y_train)


# 결정 경계 시각화
# 다섯 개의 결정트리 결정 경계
fig, axes = plt.subplots(2, 3, figsize=(20, 10))
for i, (ax, tree) in enumerate(zip(axes.ravel(), model.estimators_)):
    ax.set_title("tree {}".format(i))
    mglearn.plots.plot_tree_partition(X, y, tree, ax=ax)

len(X)
# # 랜덤포레스트로 만들어진 결정경계
# axes[-1, -1].set_title("Random forest")
# mglearn.plots.plot_2d_separator(
#     model, X, fill=True, alpha=0.5, ax=axes[-1, -1])
# mglearn.discrete_scatter(X[:, 0], X[:, 1], y)


# %%

cancer = load_breast_cancer()

x_train, x_test, y_train, y_test = train_test_split(cancer.data, cancer.target,
                                                    stratify=cancer.target, random_state=0)

# %%
x_train, x_test, y_train, y_test
# %%
# cancer은 메타데이터, data는 pandas, shape는 x,y길이
n_feature = cancer.data.shape[1]

score_n_tr_est = []
score_n_te_est = []
score_m_tr_mft = []
score_m_te_mft = []

# n_estimators와 mat_features는 모두 0보다 큰 정수여야 하므로 1부터 시작합니다.
for i in np.arange(1, n_feature+1):
    params_n = {'n_estimators': i, 'max_features': 'auto',
                'n_jobs': -1}  # **kwargs parameter
    params_m = {'n_estimators': 10, 'max_features': i, 'n_jobs': -1}

    forest_n = RandomForestClassifier(**params_n).fit(x_train, y_train)
    forest_m = RandomForestClassifier(**params_m).fit(x_train, y_train)

    score_n_tr = forest_n.score(x_train, y_train)
    score_n_te = forest_n.score(x_test, y_test)
    score_m_tr = forest_m.score(x_train, y_train)
    score_m_te = forest_m.score(x_test, y_test)

    score_n_tr_est.append(score_n_tr)
    score_n_te_est.append(score_n_te)
    score_m_tr_mft.append(score_m_tr)
    score_m_te_mft.append(score_m_te)

index = np.arange(len(score_n_tr_est))
plt.plot(index, score_n_tr_est, label='n_estimators train score',
         color='lightblue', ls='--')  # ls: linestyle
plt.plot(index, score_m_tr_mft, label='max_features train score',
         color='orange', ls='--')
plt.plot(index, score_n_te_est,
         label='n_estimators test score', color='lightblue')
plt.plot(index, score_m_te_mft, label='max_features test score', color='orange')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),
           ncol=2, fancybox=True, shadow=False)  # fancybox: 박스모양, shadow: 그림자
plt.xlabel('number of parameter', size=15)
plt.ylabel('score', size=15)

plt.show()

n_feature = cancer.data.shape[1]
index = np.arange(n_feature)

forest = RandomForestClassifier(n_estimators=100, n_jobs=-1)
forest.fit(x_train, y_train)
plt.barh(index, forest.feature_importances_, align='center')
plt.yticks(index, cancer.feature_names)
plt.ylim(-1, n_feature)
plt.xlabel('feature importance', size=15)
plt.ylabel('feature', size=15)
plt.show()
# %%
