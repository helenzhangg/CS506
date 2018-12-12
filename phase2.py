import nltk
import json
from textblob import TextBlob

'''

For each company, we will determine the sentiment of up to 500 of their reviews and add their polarity score, and update a count
Create a dictionary such that:
key = # of stars, value = {"review count": int, "polarity scores": int}
at the end, to find the average return polarity scores / review count 

Goal: find the average polarity score associated with a star rating 

'''

def get_review_polarity_score(review):
    pros_polarity_score = TextBlob(review['pros']).polarity
    cons_polarity_score = TextBlob(review['cons']).polarity
    return (pros_polarity_score + cons_polarity_score) * .5


# where company_reviews is a dictionary of all the reviews with key = id
def get_company_polarity_scores(company_reviews, d):

    limit = max(500, len(company_reviews))
    count = 0
    for k,v in company_reviews.items():
        if count >= limit: break
        score = get_review_polarity_score(company_reviews[k])
        star_rating = company_reviews[k]['rating']
        d[int(float(star_rating))]['review_count'] +=1
        d[int(float(star_rating))]['polarity_score'] += score
        count+=1

    return d

# where d is the dict with all the scores for each star rating
def get_average_scores(d):

    for rating in d:
        d[rating]['average_score'] = d[rating]['polarity_score'] / d[rating]['review_count']

    return d

def init():
    d = {}

    for i in range(1,6):
        d[i] = {}
        d[i]['review_count'] = 0
        d[i]['polarity_score'] = 0.0

    with open('small_company_reviews.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    small_company_reviews = json.loads(data)

    with open('large_company_reviews.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    large_company_reviews = json.loads(data)

    for company in small_company_reviews:
        get_company_polarity_scores(small_company_reviews[company], d)

    for company in large_company_reviews:
        get_company_polarity_scores(large_company_reviews[company], d)

    get_average_scores(d)
    print('RESULT HERE:', d)
    return


# adds the polarity score to each review and writes the results into a new doc
# need this updated dict for phase 3
def update_review_polarity_scores():
    # get_review_polarity_score

    with open('small_company_reviews.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    small_company_reviews = json.loads(data)

    updated_dict_small_companies = {}   # this dict includes the polarity score

    with open('large_company_reviews.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    large_company_reviews = json.loads(data)

    updated_dict_large_companies = {}   # this dict includes the polarity score


    for group in [small_company_reviews, large_company_reviews]:
        for c in group:
            print('CURRENTLY ON COMPANY: ',c)
            for review in group[c]:
                group[c][review]['polarity_score'] = get_review_polarity_score(group[c][review])
                if group == small_company_reviews:
                    if c not in updated_dict_small_companies:
                        updated_dict_small_companies[c] = {}
                    updated_dict_small_companies[c][review] = group[c][review]
                else:
                    if c not in updated_dict_large_companies:
                        updated_dict_large_companies[c] = {}
                    updated_dict_large_companies[c][review] = group[c][review]

    f1 = open("small_company_reviews_polarity_scores.txt", "w+")
    f1.write(json.dumps(updated_dict_small_companies))
    f1.close()

    f1 = open("large_company_reviews_polarity_scores.txt", "w+")
    f1.write(json.dumps(updated_dict_large_companies))
    f1.close()

    return


update_review_polarity_scores()

# RESULT HERE: {1: {'review_count': 1765, 'polarity_score': 468.8436637284275, 'average_score': 0.26563380381214025}, 2: {'review_count': 2273, 'polarity_score': 814.727823507667, 'average_score': 0.3584372298757884}, 3: {'review_count': 4651, 'polarity_score': 1947.9523991615251, 'average_score': 0.4188244246745915}, 4: {'review_count': 7604, 'polarity_score': 3504.1687242375597, 'average_score': 0.46083228882661226}, 5: {'review_count': 8946, 'polarity_score': 4654.197614079766, 'average_score': 0.5202545958059206}}
