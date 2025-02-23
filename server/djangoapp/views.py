from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .models import CarModel

from django.urls import reverse

from .restapis import get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, get_dealers_from_cf, post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# `login_request` view to handle sign in request


def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        print(username)
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            print("not post")
            # If not, return to login page again
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# `logout_request` view to handle sign out request


def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    redirect_path = reverse("djangoapp:index")
    return redirect(redirect_path)


# `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/poore_djangoserver-space/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        print(dealerships)
        # Return a list of dealer short name
        context['dealership_list'] = dealerships

        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):


def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/poore_djangoserver-space/default/get-reviews"
        # Get dealers from the URL
        dealerships = get_dealer_by_id_from_cf(url, dealer_id)

        # dealer_reviews = ' '.join(
        #     [dealership.review for dealership in dealerships])
        # print(dealer_names)
        # Return a list of dealer short name
        reviews = get_dealer_reviews_from_cf(dealerships)
        context["reviews"] = reviews
        context['dealer_id'] = dealer_id
        print(context)
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.method == "GET":
        context["dealer_id"] = dealer_id
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/poore_djangoserver-space/dealership-package/get-dealership"
        dealerships = get_dealers_from_cf(url)
        dealership = next(filter(lambda x: x.id == dealer_id, dealerships))
        context["dealership"] = dealership
        context["cars"] = CarModel.objects.all().filter(dealer_id=dealer_id)
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/poore_djangoserver-space/default/reviews"
        if request.user.is_authenticated:
            review = dict()
            review["time"] = datetime.utcnow().isoformat()
            review["dealership"] = dealer_id
            review["name"] = request.POST["username"]

            review["review"] = request.POST["content"]
            review["purchase_date"] = request.POST["purchasedate"]
            review["purchase"] = request.POST.get("purchasecheck")

            if request.POST.get('car'):
                car = CarModel.objects.get(id=request.POST['car'])
                if car:
                    review['car_make'] = car.make.name
                    review['car_model'] = car.name
                    review['car_year'] = car.year.strftime("%Y")

            json_payload = dict()
            json_payload["review"] = review

            response = post_request(url, json_payload, dealer_id=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)


# self.car_make = car_make
# self.car_model = car_model
# self.car_year = car_year
# self.sentiment = sentiment
