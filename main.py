import requests
import time
import json
from bs4 import BeautifulSoup


def get_attribute_value(attribute_name, html_elements):
    result = [] # an array of all the values that each element has for attribute_name

    for element in html_elements:
        if attribute_name == "text":
            result.append(element.text)
            continue
        result.append(element[attribute_name])
    return result

# where keys is an array of ids / key values, and values is a dictionary of values for each id
def create_json_objects(keys, values, json_dict = {}):
    for i, key in enumerate(keys):
        json_dict[key] = {}
        for v in values:
            try:
                json_dict[key][v['id']] = v['values'][i]
            except Exception as e:
                print(type(e))
                print('ERROR IN CREATING JSON OBJECTS')
    return json_dict


# will get reviews from url and update and return d, a dictionary of all the results
def get_reviews_from_url(url, d={}, is_first_page=False):

    headers = {'user-agent': 'Mozilla/5.0'}
    t0 = time.time()
    page_response = requests.get(url, headers=headers)
    response_delay = time.time() - t0
    time.sleep(8 * response_delay)  # add a delay of 8 times the time it took for Glassdoor to send back a response
    page_content = BeautifulSoup(page_response.content, "html.parser")

    ratings = page_content.find_all("span", class_="value-title")
    review_pros = page_content.find_all("p", class_="pros")
    review_cons = page_content.find_all("p", class_="cons")
    dates = page_content.find_all("time", class_="date")

    reviews = page_content.find_all("li", class_=" empReview cf ")
    review_ids = [review["id"] for review in reviews]

    if is_first_page:
        for arr in (ratings, review_pros, review_cons, review_ids):
            arr.pop(0)

    if len(ratings) != len(review_cons):
        ratings.pop(0)

    parsed_dates = get_attribute_value('datetime', dates)
    parsed_ratings = get_attribute_value('title', ratings)
    parsed_pros = get_attribute_value('text', review_pros)
    parsed_cons = get_attribute_value('text', review_cons)

    d = create_json_objects(review_ids, [{'id':'rating', 'values': parsed_ratings}, {'id':'pros', 'values': parsed_pros}, {'id':'cons', 'values': parsed_cons}, {'id':'date', 'values': parsed_dates}], d)

    return d


def get_formatted_url(company_name, company_id, page_number=1):
    base_url = 'https://www.glassdoor.com/Reviews/'
    formatted_url = base_url + company_name + '-Reviews-E' + str(company_id) + '_P' + str(page_number) + '.htm'
    return formatted_url

def get_review_count_value(text):

    if 'k' in text:
        if '.' not in text:
            return 1000*float(text[:-1])
        i = 0
        thousands = ''
        while text[i] != '.':
            thousands += text[i]
            i+=1
        if text[i+1] == 'k':
            return float(thousands)*1000
        else:
            hundreds = text[i+1:-1]
            return (float(thousands)*1000 + float(hundreds)*100)
    else:
        return float(text)

# called to grab all the reviews of a given link
# returns a JSON like dictionary containing all the reviews, where key = review ID and value = rating, pros, cons, date
def get_all_reviews(url):

    headers = {'user-agent': 'Mozilla/5.0'}
    page_response = requests.get(url, headers=headers)
    page_content = BeautifulSoup(page_response.content, "html.parser")

    # we parse the HTML page content for the company name, company id, and total number of reviews

    id_div = page_content.find("div", id="EmpHero")
    company_id = id_div['data-employer-id']

    company_header = page_content.find("div", class_="header cell info")
    company_name = company_header.p.text

    review_HTML_element = page_content.find("a", class_="eiCell cell reviews active")
    total_review_count = get_review_count_value(review_HTML_element.find("span", class_="num h2").text)

    print('ORIGINAL TEXT', review_HTML_element.find("span", class_="num h2").text)
    print(total_review_count)
    company_dict = {}

    for i in range(1, int(total_review_count/10) + 1):
        print('currently getting page : ' + str(i))
        url = get_formatted_url(company_name, company_id, i)

        if i == 1:
            get_reviews_from_url(url, company_dict, True)
            continue

        get_reviews_from_url(url, company_dict)

    print('SUCCESSFULLY FINISHED MAKING JSON FOR' + str(company_name))
    return company_dict


test = True
# ('Amazon', 'https://www.glassdoor.com/Reviews/Amazon-Reviews-E6036.htm'),
# ('AMD', 'https://www.glassdoor.com/Reviews/AMD-Reviews-E15.htm'), taken out because it's too large
# ('Netflix', 'https://www.glassdoor.com/Reviews/Netflix-Reviews-E11891.htm')
large_companies = [
    ('PayPal', 'https://www.glassdoor.com/Reviews/PayPal-Reviews-E9848.htm'),
    ('Ulta', 'https://www.glassdoor.com/Reviews/Ulta-Beauty-Reviews-E9466.htm'),
    ('Facebook', 'https://www.glassdoor.com/Reviews/Facebook-Reviews-E40772.htm'),
    ('Apple', 'https://www.glassdoor.com/Reviews/Apple-Reviews-E1138.htm')
]


small_companies = [
    ('Square','https://www.glassdoor.com/Reviews/Square-Reviews-E422050.htm'),
    ('Lululemon', 'https://www.glassdoor.com/Reviews/lululemon-Reviews-E42589.htm'),
    ('Workday', 'https://www.glassdoor.com/Reviews/Workday-Reviews-E197851.htm'),
    ('Etsy', 'https://www.glassdoor.com/Reviews/Etsy-Reviews-E42751.htm'),
    ('Shopify', 'https://www.glassdoor.com/Reviews/Shopify-Reviews-E675933.htm'),
    ('Grubhub', 'https://www.glassdoor.com/Reviews/Grubhub-Reviews-E419089.htm')
]
if test:
    large_company_reviews = {}
    small_company_reviews = {}

    for c in small_companies:
        company_name = c[0]
        result = get_all_reviews(c[1])
        small_company_reviews[company_name] = result

    f = open("small_company_reviews.txt", "w+")
    f.write(json.dumps(small_company_reviews))
    f.close()
    print('finished small company reviews')


    f1 = open("large_company_reviews.txt", "a")
    for c in large_companies:
        company_name = c[0]
        result = get_all_reviews(c[1])
        large_company_reviews[company_name] = result
        f1.write(json.dumps({company_name: result}))
        f1.write("\n")

    f1.close()
    print('finished large company reviews')


'''
Large Companies:

Netflix: https://www.glassdoor.com/Reviews/Netflix-Reviews-E11891.htm
AMD: https://www.glassdoor.com/Reviews/AMD-Reviews-E15.htm
Amazon: https://www.glassdoor.com/Reviews/Amazon-Reviews-E6036.htm
Apple: https://www.glassdoor.com/Reviews/Apple-Reviews-E1138.htm
Facebook: https://www.glassdoor.com/Reviews/Facebook-Reviews-E40772.htm

PayPal: https://www.glassdoor.com/Reviews/PayPal-Reviews-E9848.htm
Ulta: https://www.glassdoor.com/Reviews/Ulta-Beauty-Reviews-E9466.htm

Small Companies:
Square: https://www.glassdoor.com/Reviews/Square-Reviews-E422050.htm
Lululemon: https://www.glassdoor.com/Reviews/lululemon-Reviews-E42589.htm
Workday: https://www.glassdoor.com/Reviews/Workday-Reviews-E197851.htm
Etsy: https://www.glassdoor.com/Reviews/Etsy-Reviews-E42751.htm
Shopify: https://www.glassdoor.com/Reviews/Shopify-Reviews-E675933.htm

Grubhub: https://www.glassdoor.com/Reviews/Grubhub-Reviews-E419089.htm



'''