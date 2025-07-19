from django.urls import path
from . import views
 
appname = "tourapp"
urlpatterns = [
    path("", views.home, name="home"),
    
    #authentication paths
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),

    #tour paths
    path("tours/", views.tour_list, name="tour_list"),
    path("tour/<int:tour_id>/", views.tour_detail, name="tour_detail"),
    path("tour/<int:tour_id>/comment/", views.tour_detail, name="tour_comment"),
    
    #wishlist paths
    path("wishlist/", views.wishlist, name="wishlist"),
    path("tour/<int:tour_id>/love/", views.love_tour, name="love_tour"),
    path("tour/<int:tour_id>/unlove/", views.unlove_tour, name="unlove_tour"),
    
    #user profile paths
    path("profile/<int:user_id>/", views.user_profile, name="profile"),
    path("profile/<int:user_id>/edit/", views.edit_profile, name="edit_profile"),
    
    #company paths
    path("become_companion/", views.become_companion, name="become_companion"),
    path("company/<int:company_id>/", views.company_profile, name="company_profile"),
    path("company/<int:company_id>/edit/", views.edit_company_profile, name="edit_company_profile"),
    
    #comment paths
    path("tour/<int:tour_id>/comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    path("tour/<int:tour_id>/comment/<int:comment_id>/unlike/", views.unlike_comment, name="unlike_comment"),
    path("tour/<int:tour_id>/comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    
    #tour image paths
    path("tour/upload/", views.upload_tour, name="upload_tour"),
    path("tour/<int:tour_id>/image/upload/", views.upload_tour_image, name="upload_tour_image"),
    path("tour/<int:tour_id>edit-details/", views.edit_tour_details, name="edit_tour_details"),
    path('api/tour/<int:tour_id>/upload-image/', views.upload_tour_image_api, name='upload_tour_image_api'),
    path('api/tour/<int:tour_id>/images/', views.tour_images_api, name='tour_images_api'),
    path('api/tour/<int:tour_id>/delete-image/<int:image_id>/', views.delete_tour, name='delete_tour_image_api'),
    #api paths
    path("api/user/booked-tours/", views.user_booked_tours_api, name="user_booked_tours_api"),
    path("tour/<int:tour_id>/comments/", views.tour_comments_api, name="tour_comments_api"),
    
    # booking paths
    path("tour/<int:tour_id>/book/", views.book_tour, name="book_tour"),
    path('payment/', views.payment_view, name='payment_view'),
]