from django.contrib import admin

# Register your models here.

from .models import User, Category, Auction, Bids, Comment


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction)
admin.site.register(Bids)
admin.site.register(Comment)