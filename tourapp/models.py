from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Phone number validator
phone_regex = RegexValidator(
    regex=r'^\d+$',
    message="Phone number must be entered in digits only (positive numbers)."
)

def user_avatar_upload_path(instance, filename):
    return f"useravt/{instance.user.id}/{filename}"

def company_logo_upload_path(instance, filename):
    return f"companylogo/{instance.company.id}/{filename}"

def tour_image_upload_path(instance, filename):
    return f"tour/{instance.tour.id}/{filename}"

# Create your models here.
class CompanyTour(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    phone_number = models.CharField(
        max_length=10, blank=True, null=True,
        validators=[phone_regex]
    )
    email = models.EmailField()
    address = models.TextField()
    facebook_link = models.URLField(blank=True, null=True)
    tours = models.ManyToManyField('Tour', related_name='company_tours', blank=True)
    bank = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.company_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phonenumber = models.CharField(
        max_length=10, blank=True, null=True,
        validators=[phone_regex]
    )
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to=user_avatar_upload_path, blank=True, null=True)
    

    def __str__(self):
        return self.user.username
    
class CompanyProfile(models.Model):
    company = models.OneToOneField(CompanyTour, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to=company_logo_upload_path, blank=True, null=True)
    follow = models.ManyToManyField(User, related_name='followed_companies', blank=True)
    admin_verified = models.BooleanField(default=False)


    def __str__(self):
        return self.company.company_name

class PendingCompanyProfileEdit(models.Model):
    company = models.OneToOneField(CompanyTour, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='pending_company_pictures/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Tour(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    loved = models.ManyToManyField(User, related_name='loved_tours', blank=True)
    duration_day = models.PositiveIntegerField(help_text='Duration in days')
    duration_night = models.PositiveIntegerField(help_text='Duration in nights')
    def __str__(self):
        return self.title
    
    @property
    def first_image_url(self):
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return None

class TourImage(models.Model):
    tour = models.ForeignKey(Tour, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=tour_image_upload_path)

    def __str__(self):
        return f'Image for {self.tour.title}'
class Comment(models.Model):
    tour = models.ForeignKey(Tour, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.tour.title}'
    
class Booking(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_people = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Booking by {self.user.username} for {self.tour.title}'
