from email import message
from urllib import request
from xml.etree.ElementTree import Comment
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError

from .models import Category, User, Auction, Bids, Comment


"""
    TODO : Create cathegory
    TODO : Create Watchlist
    TODO : Auction page
    TODO : Watchlist model
"""

def index(request):
    qs = Auction.objects.all()
    auctions = [{ "name" : i.name, 
             "description" : i.description,
             "user" : i.user.username, 
             "created_at" : i.created_at.strftime('%B, %d, %Y %I:%M %p'), 
             "image" : i.image.url,
             "price" : i.highest_bid(),
             "id" : i.pk } for i in qs]

    return render(request, "auctions/index.html", {
        "auctions" : auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
            
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listening(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            redirect = False
            create_without_image = False

            name = request.POST["name"]
            description = request.POST["description"]
            price = request.POST["price"]
            category = request.POST["category"]
            user = request.user.pk

            if not name:
                messages.error(request, "You need to offer a name!")
                redirect = True
            if not description:
                messages.error(request, "You need to offer a description!")
                redirect = True
            if not price:
                messages.error(request, "You need to offer a minimal price!")
                redirect = True

            if category == 0:
                category = None

            if redirect:
                return HttpResponseRedirect(reverse("index"))
            
            #Verify if has image
            image = None

            try:
                image = request.FILES["image"]
            except MultiValueDictKeyError:
                messages.info(request, "You haven't offer a image!")
                create_without_image = True
                

            #Items to find
            user = User.objects.filter(pk=user).first()

            category = Category.objects.filter(name=category).first()

            if create_without_image:
                listening = Auction.objects.create(name=name, price=price, description=description, category=category, user=user)
                listening.save()
            else:
                listening = Auction.objects.create(name=name, image=image,price=price, description=description, category=category, user=user)
                listening.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            print(request.user.password)
            categories = Category.objects.all()
            return render(request, "auctions/create.html", {
                "categories" : categories
            })
    else:
        return HttpResponseRedirect(reverse("index"))

def find(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':

            qs = Auction.objects.filter(pk=id).first()

            if not request.POST["bid"]:
                messages.error(request, "You need to expecify a price to a bid!")
                return HttpResponseRedirect(reverse('find', kwargs={'id': id}))

            bid = int(request.POST["bid"])

            if qs.user.pk == request.user.pk:
                messages.error(request, "You can't bid on your own auction!")
                return HttpResponseRedirect(reverse('find', kwargs={'id': id}))

            if bid <= qs.highest_bid():
                messages.error(request, "The bid is not high enough!")
                return HttpResponseRedirect(reverse('find', kwargs={'id': id}))

            

            new_bid = Bids.objects.create(price=bid, user=request.user, item=qs)
            return HttpResponseRedirect(reverse('find', kwargs={'id': id}))


        qs = Auction.objects.filter(pk=id).first()

        if qs is None:
            messages.error(request, "Auction not found!")
            return HttpResponseRedirect(reverse("index"))


        auction = {
            "name" : qs.name, 
            "description" : qs.description,
            "user" : qs.user.username, 
            "created_at" : qs.created_at.strftime('%B, %d, %Y %I:%M %p'), 
            "image" : qs.image.url,
            "price" : qs.highest_bid(),
            "id" : qs.pk,
            "n_bids" : qs.number_of_bids(),
            "category" : qs.category}

        # Find Comments

        comments = Comment.objects.filter(item= qs)

        # Find if your bid was the last

        return render(request, "auctions/auction.html", {
            "auction" : auction,
            "watchlist" : qs.user_in_watchlist(request.user.pk),
            "comments" : comments,
            "was_your_bid_the_last_bid" : qs.was_your_bid_the_last_bid(request.user.pk)
        })
    else:
        return HttpResponseRedirect(reverse("index"))

def categories(request):
    qs = Category.objects.all()
    return render(request, "auctions/category.html", {
        "categories" : qs
    })

def find_category(request, id):
    if not isinstance(id, int):
        return HttpResponseRedirect(reverse("index"))
    category = Category.objects.filter(pk=id).first()
    qs = Auction.objects.filter(category=category)
    auctions = [{ "name" : i.name, 
             "description" : i.description,
             "user" : i.user.username, 
             "created_at" : i.created_at.strftime('%B, %d, %Y %I:%M %p'), 
             "image" : i.image.url,
             "price" : i.highest_bid(),
             "id" : i.pk } for i in qs]
    return render(request, "auctions/find_category.html",{
        "auctions" : auctions
    })

def watch_list_page(request):
    if not request.user.is_authenticated:
        messages.error(request, "Sorry, you're not logged in!")
        return HttpResponseRedirect(reverse("index"))
    qs = Auction.objects.filter(users_watchlist__pk=request.user.pk)
    auctions = [{ "name" : i.name, 
             "description" : i.description,
             "user" : i.user.username, 
             "created_at" : i.created_at.strftime('%B, %d, %Y %I:%M %p'), 
             "image" : i.image.url,
             "price" : i.highest_bid(),
             "id" : i.pk } for i in qs]
    return render(request, "auctions/watchlist.html", {
        "auctions" : auctions
    })

def watch_list(request, id):
    if request.method == 'POST':

        if not request.user.is_authenticated:
            messages.error(request, "Wy are you doing this?")
            return HttpResponseRedirect(reverse("index"))

        auction = Auction.objects.filter(pk=id).first()
        user = User.objects.filter(pk=request.user.id).first()
        print(auction)
        print(user)
        if auction.user_in_watchlist(request.user.pk):
            print("Removeu")
            auction.users_watchlist.remove(user)
        else:
            print("Salvou")
            auction.users_watchlist.add(user)
        return HttpResponseRedirect(reverse('find', kwargs={'id': id}))

def add_comment(request, id):
    if request.method == 'POST':
        if not request.POST["comment"]:
            messages.error(request, "Need to inform a comment!")
            return HttpResponseRedirect(reverse('find', kwargs={'id': id}))
        
        auction = Auction.objects.filter(pk=id).first()
        user = User.objects.filter(pk=request.user.pk).first()

        comment = Comment.objects.create(user=user, item=auction, comment=request.POST["comment"])
        return HttpResponseRedirect(reverse('find', kwargs={'id': id}))