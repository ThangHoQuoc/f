from django.contrib import admin
from django.contrib.auth.models import User
from .models import CompanyTour, UserProfile, CompanyProfile, Tour, TourImage, Comment
# Register your models here.


admin.site.register(CompanyTour)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username',)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(CompanyProfile)

class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'price', 'duration_day', 'duration_night')
    search_fields = ('title', 'created_by__username')
    list_filter = ('created_at',)
admin.site.register(Tour, TourAdmin)

class TourImageAdmin(admin.ModelAdmin):
    list_display = ('tour', 'image')
    search_fields = ('tour__title',)
admin.site.register(TourImage, TourImageAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('tour', 'user', 'created_at')
    search_fields = ('tour__title', 'user__username')
    list_filter = ('created_at',)
admin.site.register(Comment, CommentAdmin)
