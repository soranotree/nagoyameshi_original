from django.contrib import admin
from .models import Category, Restaurant, DiningTable, Reservation, Review, Favorite
admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(DiningTable)
admin.site.register(Reservation)
admin.site.register(Review)
# admin.site.register(ReviewReply)
admin.site.register(Favorite)