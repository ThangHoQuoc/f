from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.core.paginator import Paginator
import json
from django.views.decorators.http import require_POST

from .models import CompanyTour, UserProfile, Tour, TourImage, Comment, PendingCompanyProfileEdit
# Create your views here.

def home(request):
    tours = Tour.objects.all().order_by('-created_at')[:5]
    return render(request, 'tourapp/index.html', {'tours': tours})
    return render(request, 'tourapp/index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')
        next_url = request.POST.get('next')
        content = request.POST.get('content')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # If next and content are present, post the comment
            if next_url and content:
                match = re.match(r'/tour/(\d+)/', next_url)
                if match:
                    tour_id = match.group(1)
                    tour = Tour.objects.get(id=tour_id)
                    Comment.objects.create(tour=tour, user=user, content=content)
            return redirect(next_url or 'home')
        return redirect('home')
    next_url = request.GET.get('next', '')
    content = request.GET.get('content', '')
    return render(request, 'tourapp/login.html', {'next': next_url, 'content': content})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'tourapp/register.html', {'error': 'Mật khẩu không khớp!'})
        try:
            User.objects.get(username=username)
            return render(request, 'tourapp/register.html', {'error': 'Tên đăng nhập đã tồn tại!'})
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            return redirect('login')
    return render(request, 'tourapp/register.html')

def logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return render(request, 'tourapp/index.html')

def tour_list(request):
    tours = Tour.objects.all()
    return render(request, 'tourapp/tour_list.html', {'tours': tours})

def tour_detail(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    comments = tour.comments.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Pass next and content as query params
            login_url = f"/login/?next=/tour/{tour_id}/&content={request.POST.get('content', '')}"
            return redirect(login_url)

        content = request.POST.get('content')
        Comment.objects.create(tour=tour, user=request.user, content=content)
        return redirect('tour_detail', tour_id=tour.id)

    return render(request, 'tourapp/tour_detail.html', {'tour': tour, 'comments': comments})


def tour_comments_api(request, tour_id):
    page = int(request.GET.get('page', 1))
    per_page = 5
    tour = Tour.objects.get(id=tour_id)
    comments = tour.comments.all().order_by('-id')
    paginator = Paginator(comments, per_page)
    page_obj = paginator.get_page(page)
    comments_data = [
        {
            'user': c.user.username,
            'content': c.content,
            'created': c.created.strftime('%Y-%m-%d %H:%M'),
            'id': c.id,
            'like_count': c.like.count()  # This line ensures like count is sent
        }
        for c in page_obj.object_list
    ]
    return JsonResponse({
        'comments': comments_data,
        'has_next': page_obj.has_next()
    })
    
    
@login_required
def wishlist(request):
    user = request.user
    loved_tours = user.loved_tours.all()
    return render(request, 'tourapp/tour_list.html', {'loved_tours': loved_tours})

@login_required
@require_POST
def love_tour(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    request.user.loved_tours.add(tour)
    return JsonResponse({'status': 'ok', 'message': 'Tour loved!'})

@login_required
@require_POST
def unlove_tour(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    request.user.loved_tours.remove(tour)
    return JsonResponse({'status': 'ok', 'message': 'Tour un-loved!'})

def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile = UserProfile.objects.get(id=user.id)

    return render(request, 'tourapp/user_profile.html', {'user': user, 'profile': profile})


@login_required
def user_booked_tours_api(request):
    user = request.user
    tours = user.booked_tours.all()
    data = []
    for tour in tours:
        first_img = tour.images.first()
        data.append({
            'name': tour.title,
            'image': first_img.image.url if first_img else None
        })
    return JsonResponse({'booked_tours': data})

@login_required
def edit_profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile = UserProfile.objects.get(user=user)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')

        if username:
            user.username = username
        if email:
            user.email = email
        if phonenumber:
            profile.phonenumber = phonenumber
        user.save()
        
        if bio:
            profile.bio = bio
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.save()

        return redirect('profile', user_id=user.id)

    return render(request, 'tourapp/edit_profile.html', {'user': user, 'profile': profile})


@login_required
def like_comment(request, tour_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.like.add(request.user)
    return JsonResponse({'status': 'ok', 'message': 'Comment liked!', 'like_count': comment.like.count()})

@login_required
def unlike_comment(request, tour_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.like.remove(request.user)
    return JsonResponse({'status': 'ok', 'message': 'Comment unliked!', 'like_count': comment.like.count()})

@login_required
def delete_comment(request, tour_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.user == request.user:
        comment.delete()
        return JsonResponse({'status': 'ok', 'message': 'Comment deleted!'})
    return JsonResponse({'status': 'error', 'message': 'You can only delete your own comments.'}, status=403)


@login_required
def become_companion(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        facebook_link = request.POST.get('facebook_link')

        company = CompanyTour.objects.create(
            user=request.user,
            company_name=company_name,
            phone_number=phone_number,
            email=email,
            address=address,
            facebook_link=facebook_link
        )
        # After creation, user waits for admin verification
        return render(request, 'tourapp/not_verified.html', {'company': company})

    return render(request, 'tourapp/become_companion.html')

@login_required
def company_profile(request, company_id):
    company = CompanyTour.objects.get(id=company_id)
    # Only allow access if admin_verified is True
    if not company.companyprofile.admin_verified:
        return render(request, 'tourapp/not_verified.html', {'company': company})
    posted_tours = company.tours.all()
    return render(request, 'tourapp/company_profile.html', {'company': company, 'posted_tours': posted_tours})

@login_required
def edit_company_profile(request, company_id):
    company = CompanyTour.objects.get(id=company_id)
    # Only allow edit if admin_verified is True
    if not company.companyprofile.admin_verified:
        return render(request, 'tourapp/not_verified.html', {'company': company})
    
    if request.method == 'POST':
        # Store changes in PendingCompanyProfileEdit
        pending, created = PendingCompanyProfileEdit.objects.get_or_create(company=company)
        pending.company_name = request.POST.get('company_name', company.company_name)
        pending.phone_number = request.POST.get('phone_number', company.phone_number)
        pending.email = request.POST.get('email', company.email)
        pending.address = request.POST.get('address', company.address)
        pending.facebook_link = request.POST.get('facebook_link', company.facebook_link)
        if 'profile_picture' in request.FILES:
            pending.profile_picture = request.FILES['profile_picture']
        pending.save()
        return render(request, 'tourapp/edit_pending.html', {'company': company})
    return render(request, 'tourapp/edit_company_profile.html', {'company': company})

@login_required
def upload_tour(request, company_id):
    company = CompanyTour.objects.get(id=company_id)
    if not company.companyprofile.admin_verified:
        return render(request, 'tourapp/not_verified.html', {'company': company})
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration_day = request.POST.get('duration_day')
        duration_night = request.POST.get('duration_night')
        tour = Tour.objects.create(
            title=title,
            description=description,
            created_by=company.user,
            price=price,
            duration_day=duration_day,
            duration_night=duration_night
        )
        company.tours.add(tour)
        return redirect('company_profile', company_id=company.id)
    return render(request, 'tourapp/upload_tour.html', {'company': company})


@login_required
def upload_tour_image(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    images = tour.images.all()  
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            TourImage.objects.create(tour=tour, image=image)
            return redirect('upload_tour_image', tour_id=tour.id) 
    return render(request, 'tourapp/upload_tour_image.html', {'tour': tour, 'images': images})

@login_required
@csrf_exempt
def upload_tour_image_api(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            TourImage.objects.create(tour=tour, image=image)
    images = tour.images.all()
    images_data = [{'id': img.id, 'url': img.image.url} for img in images]
    return JsonResponse({'images': images_data})

@login_required
def tour_images_api(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    images = tour.images.all()
    images_data = [{'id': img.id, 'url': img.image.url} for img in images]
    return JsonResponse({'images': images_data})

@login_required
def edit_tour_details(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    if request.method == 'POST':
        tour.title = request.POST.get('title', tour.title)
        tour.description = request.POST.get('description', tour.description)
        tour.price = request.POST.get('price', tour.price)
        tour.duration_day = request.POST.get('duration_day', tour.duration_day)
        tour.duration_night = request.POST.get('duration_night', tour.duration_night)
        tour.save()
        return redirect('tour_detail', tour_id=tour.id)
    return render(request, 'tourapp/edit_tour_details.html', {'tour': tour})


@login_required
@require_POST
def delete_tour(request, tour_id, image_id):
    tour = Tour.objects.get(id=tour_id)
    image = TourImage.objects.get(id=image_id, tour=tour)
    image.delete()
    return JsonResponse({'status': 'ok'})