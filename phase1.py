import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
import pandas as pd


# updates true_label_list and raw_review_list
def get_review_data(reviews, true_label_list, raw_reviews):

    for review_id in reviews:
        pros = reviews[review_id]['pros']
        cons = reviews[review_id]['cons']
        true_label_list.append(1)
        true_label_list.append(0)
        raw_reviews.append(pros)
        raw_reviews.append(cons)

    return


def get_tf_idf(unlabeled_raw_pros_cons):
    vectorizer = TfidfVectorizer(stop_words='english', min_df=4, max_df=0.8)
    data = vectorizer.fit_transform(unlabeled_raw_pros_cons)
    print(type(data), data.shape)
    return data

def apply_svd(data):
    svd = TruncatedSVD(n_components=200)
    data = svd.fit_transform(data)
    print(data.shape)
    return data

def apply_k_means(X):
    kmeans = KMeans(init='k-means++', n_clusters=2, n_init=100)
    y_predicted = kmeans.fit_predict(X)
    return y_predicted


def init():

    with open('small_company_reviews.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    small_company_reviews = json.loads(data)

    with open('large_company_reviews.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    large_company_reviews = json.loads(data)

    for company in [small_company_reviews, large_company_reviews]:
        for c in company:
            print('currently on company: ', c)
            true_labels = []
            unlabeled_raw_pros_cons = []
            reviews = company[c]

            # first, grab all the pros / cons text and the true labels
            get_review_data(reviews, true_labels, unlabeled_raw_pros_cons)

            # second, apply tf-idf to format the strings
            data = get_tf_idf(unlabeled_raw_pros_cons)

            # third, scale down data to be more manageable
            scaled_data = apply_svd(data)

            # fourth, make the predictions using k-means
            predictions = apply_k_means(scaled_data)

            # fifth, check the accuracy of the predictions to the true-labels
            print(set(zip(predictions, true_labels)))
            print(pd.Series(list(zip(predictions, true_labels))).value_counts())
            print()


# init()

# currently on company:  Square
# <class 'scipy.sparse.csr.csr_matrix'> (784, 846)
# (784, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    372
# (0, 1)    249
# (1, 1)    143
# (0, 0)     20
# dtype: int64
#
# currently on company:  Lululemon
# <class 'scipy.sparse.csr.csr_matrix'> (2762, 1300)
# (2762, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    1359
# (1, 1)     818
# (0, 1)     563
# (0, 0)      22
# dtype: int64
#
# currently on company:  Workday
# <class 'scipy.sparse.csr.csr_matrix'> (1852, 1526)
# (1852, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    891
# (1, 1)    540
# (0, 1)    386
# (0, 0)     35
# dtype: int64
#
# currently on company:  Etsy
# <class 'scipy.sparse.csr.csr_matrix'> (264, 257)
# (264, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    127
# (0, 1)     84
# (1, 1)     48
# (0, 0)      5
# dtype: int64
#
# currently on company:  Shopify
# <class 'scipy.sparse.csr.csr_matrix'> (582, 582)
# (582, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    280
# (1, 1)    211
# (0, 1)     80
# (0, 0)     11
# dtype: int64
#
# currently on company:  Grubhub
# <class 'scipy.sparse.csr.csr_matrix'> (820, 710)
# (820, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    396
# (0, 1)    247
# (1, 1)    163
# (0, 0)     14
# dtype: int64
#
# currently on company:  Netflix
# <class 'scipy.sparse.csr.csr_matrix'> (1618, 1468)
# (1618, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (0, 0)    793
# (0, 1)    434
# (1, 1)    375
# (1, 0)     16
# dtype: int64
#
# currently on company:  PayPal
# <class 'scipy.sparse.csr.csr_matrix'> (5266, 2324)
# (5266, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (0, 0)    2524
# (0, 1)    1882
# (1, 1)     751
# (1, 0)     109
# dtype: int64
#
# currently on company:  Ulta
# <class 'scipy.sparse.csr.csr_matrix'> (7854, 2581)
# (7854, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (0, 0)    3893
# (1, 1)    2119
# (0, 1)    1808
# (1, 0)      34
# dtype: int64
#
# currently on company:  Facebook
# <class 'scipy.sparse.csr.csr_matrix'> (3156, 1788)
# (3156, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    1542
# (1, 1)    1002
# (0, 1)     576
# (0, 0)      36
# dtype: int64
#
# currently on company:  Apple
# <class 'scipy.sparse.csr.csr_matrix'> (25520, 5430)
# (25520, 200)
# {(0, 1), (1, 0), (0, 0), (1, 1)}
# (1, 0)    12612
# (1, 1)     8717
# (0, 1)     4043
# (0, 0)      148
# dtype: int64