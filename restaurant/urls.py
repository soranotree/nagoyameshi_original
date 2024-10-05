from django.urls import path

from . import views

urlpatterns = [
  path("", views.TopPageView.as_view(), name="top_page"),
  path("company/", views.CompanyView.as_view(), name="company_page"),
  path("terms/", views.TermsView.as_view(), name="terms_page"),
  path("restaurant-detail/<int:pk>/", views.RestaurantDetailView.as_view(), name="restaurant_detail"),
  path("restaurant-list/", views.RestaurantListView.as_view(), name="restaurant_list"),
  path("favorite-list/", views.FavoriteListView.as_view(), name="favorite_list"),
  path("favorite-delete/", views.favorite_delete, name="favorite_delete"),
  path('reservation-create/<int:pk>/', views.ReservationCreateView.as_view(), name="reservation_create"),
  path("reservation-list/", views.ReservationListView.as_view(), name="reservation_list"),
  path('reservation-delete', views.reservation_delete, name='reservation_delete'),
  path('review-list/<int:pk>/', views.ReviewListView.as_view(), name="review_list"),
  path('review-create/<int:pk>/', views.ReviewCreateView.as_view(), name="review_create"),
  path('review-update/<int:pk>/', views.ReviewUpdateView.as_view(), name="review_update"),
  path('review-delete', views.review_delete, name='review_delete'),
  path("restaurant-list-2/<int:pk>/", views.RestaurantListView2.as_view(), name="restaurant_list_2"),
  path("restaurant-create/<int:pk>/", views.RestaurantCreateView.as_view(), name="restaurant_create"),
  path("restaurant-update/<int:pk>/", views.RestaurantUpdateView.as_view(), name="restaurant_update"),
  ]