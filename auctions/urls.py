from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listening, name="create"),
    path("category", views.categories, name="categories"),
    path("category/<int:id>", views.find_category, name="find_category"),
    path("auction/<int:id>", views.find, name="find"),
    path("watchlist/", views.watch_list_page, name="watchlist_page"),
    path("watchlist/<int:id>", views.watch_list, name="watchlist"),
    path("addcomment/<int:id>", views.add_comment, name="addcomment"),
]
