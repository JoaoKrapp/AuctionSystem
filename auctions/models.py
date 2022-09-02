from email.policy import default
from statistics import mode
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return f"{self.username}"

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

class Auction(models.Model):
    """This class represents a auction in the database
    """
    name = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images', default="/images/default/image.png")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="auctions", default=None, null=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name="auctions", default=None, blank=True, null=True)
    users_watchlist = models.ManyToManyField(User, related_name="watchlist")

    

    def number_of_bids(self):
        qs = Bids.objects.filter(item=self.id).count()
        return qs

    def user_in_watchlist(self, user_pk : int) :
        list_of_ids = [i.pk for i in self.users_watchlist.all()]
        return user_pk in list_of_ids

    def highest_bid(self):
        qs = Bids.objects.filter(item=self.id)
        qslist = [i.price for i in qs]
        if qslist == []:
            return self.price
        else:
            return max(qslist)

    def was_your_bid_the_last_bid(self, user_id : int):
        bids = Bids.objects.filter(price=self.highest_bid()).first()
        if not bids:
            return False
        return bids.user.pk == user_id

    def __str__(self) -> str:
        return f"{self.name}"


class Bids(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="bids")
    item = models.ForeignKey(to=Auction, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} bid into {self.item} for ${self.price}"

class Comment(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="comments")
    item = models.ForeignKey(to=Auction, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=512)

    def __str__(self) -> str:
        return f"{self.comment}"
