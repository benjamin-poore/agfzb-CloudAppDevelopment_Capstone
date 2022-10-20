import requests
import json
import os
# import related models here
from requests.auth import HTTPBasicAuth

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions


from .models import CarDealer, DealerReview


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters

        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                params=kwargs)
        print(response)
    except:
        print("Network exception occurred")
        status_code = response.status_code
        print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


def post_request(url, json_payload, **kwargs):

    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("Network exception occurred")
        status_code = response.status_code
        print("With status {} ".format(status_code))
    return response
    # Create a get_dealers_from_cf method to get dealers from a cloud function


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    dealers = get_request(url)
    if dealers:
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(response):
    results = []
    if "data" in response:
        reviews = response["data"]["docs"]

        for review in reviews:
            # Get its content in `doc` object
            review_doc = review
            sentiment = analyze_review_sentiments(review_doc["review"])
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(
                dealership=review_doc.get("dealership"),
                name=review_doc.get("name"),
                purchase=review_doc.get("purchase", False),
                review=review_doc.get("review"),
                purchase_date=review_doc.get("purchase_date"),
                car_make=review_doc.get("car_make"),
                car_model=review_doc.get("car_model"),
                car_year=review_doc.get("car_model"),
                sentiment=sentiment, id=review_doc.get("_id")
            )
            results.append(review_obj)

    return results


# def get_dealer_by_id_from_cf(url, dealerId):
def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    response = get_request(f'{url}/?dealerId={dealerId}')
    return response

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text


def analyze_review_sentiments(dealer_review):
    params = dict()
    params["text"] = dealer_review
    params["version"] = "2019-07-12"
    params["features"] = "sentiment"
    params["return_analyzed_text"] = False

    try:
        # api_key = os.environ.get("WATSON_API_KEY")
        api_key = "uBQ0exzBG3DuEkmUjv0NL_uOXq_SErxJJIDRcX-FCaVj"
        # url = os.environ.get("WATSON_URL")
        url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/b8bc8b35-eee6-421e-abd6-92d4d2452077"
        authenticator = IAMAuthenticator(
            api_key)
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            version='2022-04-07',
            authenticator=authenticator)

        natural_language_understanding.set_service_url(url)

        response = natural_language_understanding.analyze(
            text=dealer_review,
            features=Features(
                entities=EntitiesOptions(
                    emotion=False, sentiment=True, limit=1),
                keywords=KeywordsOptions(emotion=False, sentiment=True,
                                         limit=1)),
            language="en"
        ).get_result()

        return (response["keywords"][0]["sentiment"]["label"])

    except:
        print("Network exception occured in get_request()")
