from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import urllib.parse

from .models import Tour, TourImage, Comment, UserProfile, CompanyTour

# --- Trang chủ ---
def home(request):
    tours = Tour.objects.all().order_by('-created_at')[:5]
    return render(request, 'tourapp/index.html', {'tours': tours})

# --- Auth ---
def login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            auth_login(request, user)
            return redirect(request.POST.get('next') or 'tourapp:home')
        return redirect('tourapp:login')
    return render(request, 'tourapp/login.html')

def register(request):
    if request.method == 'POST':
        if request.POST.get('password') != request.POST.get('confirm_password'):
            return render(request, 'tourapp/register.html', {'error': 'Mật khẩu không khớp'})
        if User.objects.filter(username=request.POST.get('username')).exists():
            return render(request, 'tourapp/register.html', {'error': 'Tên đăng nhập đã tồn tại'})
        User.objects.create_user(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password=request.POST.get('password')
        )
        return redirect('tourapp:login')
    return render(request, 'tourapp/register.html')

def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('tourapp:home')

# --- Trang Tour ---
def tour_list_page(request):
    return render(request, 'tourapp/tour_page.html', {'mode': 'all'})

@login_required
def wishlist_page(request):
    return render(request, 'tourapp/tour_page.html', {'mode': 'wishlist'})

@login_required
def api_tours(request):
    loved = request.GET.get('loved') == 'true'
    tours = request.user.loved_tours.all() if loved else Tour.objects.all()

    data = [{
        'id': t.id,
        'title': t.title,
        'price': float(t.price),
        'duration': f"{t.duration_day} ngày {t.duration_night} đêm",
        'image_url': t.images.first().image.url if t.images.exists() else '',
        'loved': request.user in t.loved.all()
    } for t in tours[:30]]

    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def love_tour(request, tour_id):
    request.user.loved_tours.add(get_object_or_404(Tour, id=tour_id))
    return JsonResponse({'status': 'loved'})

@csrf_exempt
@login_required
def unlove_tour(request, tour_id):
    request.user.loved_tours.remove(get_object_or_404(Tour, id=tour_id))
    return JsonResponse({'status': 'unloved'})

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    comments = tour.comments.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"/login/?next=/tour/{tour_id}/&content={request.POST.get('content', '')}")
        Comment.objects.create(tour=tour, user=request.user, content=request.POST.get('content'))
        return redirect('tourapp:tour_detail', tour_id=tour_id)

    return render(request, 'tourapp/tour_detail.html', {'tour': tour, 'comments': comments})


@login_required
def tour_comments_api(request, tour_id):
    comments = Comment.objects.filter(tour_id=tour_id).order_by('-id')
    paginator = Paginator(comments, 5)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return JsonResponse({
        'comments': [{
            'user': c.user.username,
            'content': c.content,
            'created': c.created.strftime('%Y-%m-%d %H:%M'),
            'id': c.id,
            'like_count': c.like.count()
        } for c in page_obj.object_list],
        'has_next': page_obj.has_next()
    })

# --- Bình luận: like, unlike, delete ---
@login_required
def like_comment(request, tour_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.like.add(request.user)
    return JsonResponse({'like_count': comment.like.count()})

@login_required
def unlike_comment(request, tour_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.like.remove(request.user)
    return JsonResponse({'like_count': comment.like.count()})

@login_required
def delete_comment(request, tour_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.delete()
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'unauthorized'}, status=403)

# --- Hồ sơ người dùng ---
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    return render(request, 'tourapp/user_profile.html', {'user': user, 'profile': profile})

@login_required
def edit_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        profile.phonenumber = request.POST.get('phonenumber', profile.phonenumber)
        profile.bio = request.POST.get('bio', profile.bio)
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
        user.save()
        profile.save()
        return redirect('tourapp:profile', user_id=user.id)
    return render(request, 'tourapp/edit_profile.html', {'user': user, 'profile': profile})

# --- Companion / công ty ---
@login_required
def become_companion(request):
    if request.method == 'POST':
        CompanyTour.objects.create(
            user=request.user,
            company_name=request.POST.get('company_name'),
            phone_number=request.POST.get('phone_number'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            facebook_link=request.POST.get('facebook_link'),
        )
        return render(request, 'tourapp/not_verified.html')
    return render(request, 'tourapp/become_companion.html')

@login_required
def company_profile(request, company_id):
    company = get_object_or_404(CompanyTour, id=company_id)
    if not company.companyprofile.admin_verified:
        return render(request, 'tourapp/not_verified.html', {'company': company})
    return render(request, 'tourapp/company_profile.html', {'company': company, 'posted_tours': company.tours.all()})

@login_required
def edit_company_profile(request, company_id):
    company = get_object_or_404(CompanyTour, id=company_id)
    if request.method == 'POST':
        profile = company.companyprofile
        profile.company_name = request.POST.get('company_name', profile.company_name)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.email = request.POST.get('email', profile.email)
        profile.address = request.POST.get('address', profile.address)
        profile.facebook_link = request.POST.get('facebook_link', profile.facebook_link)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        return redirect('tourapp:company_profile', company_id=company_id)
    return render(request, 'tourapp/edit_company_profile.html', {'company': company})

# --- Tour: Upload, chỉnh sửa, hình ảnh ---
@login_required
def upload_tour(request):
    if request.method == 'POST':
        tour = Tour.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            duration_day=request.POST.get('duration_day'),
            duration_night=request.POST.get('duration_night'),
            created_by=request.user
        )
        return redirect('tourapp:tour_detail', tour_id=tour.id)
    return render(request, 'tourapp/upload_tour.html')

@login_required
def upload_tour_image(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    if request.method == 'POST' and request.FILES.get('image'):
        TourImage.objects.create(tour=tour, image=request.FILES['image'])
    return render(request, 'tourapp/upload_tour_image.html', {'tour': tour, 'images': tour.images.all()})

@login_required
def edit_tour_details(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    if request.method == 'POST':
        tour.title = request.POST.get('title', tour.title)
        tour.description = request.POST.get('description', tour.description)
        tour.price = request.POST.get('price', tour.price)
        tour.duration_day = request.POST.get('duration_day', tour.duration_day)
        tour.duration_night = request.POST.get('duration_night', tour.duration_night)
        tour.save()
        return redirect('tourapp:tour_detail', tour_id=tour.id)
    return render(request, 'tourapp/edit_tour_details.html', {'tour': tour})

# --- API ảnh ---
@login_required
@csrf_exempt
def upload_tour_image_api(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    if request.method == 'POST' and request.FILES.get('image'):
        TourImage.objects.create(tour=tour, image=request.FILES['image'])
    return JsonResponse({'images': [{'id': img.id, 'url': img.image.url} for img in tour.images.all()]})

@login_required
def tour_images_api(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    return JsonResponse({'images': [{'id': img.id, 'url': img.image.url} for img in tour.images.all()]})

@login_required
@require_POST
def delete_tour(request, tour_id, image_id):
    tour = get_object_or_404(Tour, id=tour_id)
    image = get_object_or_404(TourImage, id=image_id, tour=tour)
    image.delete()
    return JsonResponse({'status': 'ok'})

# --- Đặt tour ---
@login_required
def book_tour(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    company = getattr(tour.created_by, 'companytour', None)
    if not company or not company.bank or not company.bank_account_number:
        return render(request, 'tourapp/pay.html', {
            'qr_url': '',
            'tour_title': tour.title,
            'amount': tour.price,
            'qr_data': '⚠️ Thiếu thông tin ngân hàng công ty.'
        })

    bank_code_map = {
        'MB Bank': 'mb', 'ACB': 'acb', 'Vietcombank': 'vcb',
        'Techcombank': 'tcb', 'TPBank': 'tpb', 'BIDV': 'bidv', 'VietinBank': 'ctg',
    }
    bank_code = bank_code_map.get(company.bank)
    if not bank_code:
        return render(request, 'tourapp/pay.html', {
            'qr_url': '',
            'tour_title': tour.title,
            'amount': tour.price,
            'qr_data': f'⚠️ Ngân hàng \"{company.bank}\" chưa hỗ trợ VietQR.'
        })

    qr_url = (
        f"https://img.vietqr.io/image/{bank_code}-{company.bank_account_number}-qr_only.png"
        f"?amount={int(tour.price)}"
        f"&addInfo={urllib.parse.quote(f'Thanh toan tour {tour.title}')}"
        f"&accountName={urllib.parse.quote(company.company_name)}"
    )

    return render(request, 'tourapp/pay.html', {
        'qr_url': qr_url,
        'tour_title': tour.title,
        'amount': tour.price,
        'qr_data': f"{company.company_name} - {company.bank_account_number} ({company.bank})"
    })
