from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib.auth.forms import SetPasswordForm
from django.core.paginator import Paginator
from .models import Student
from .forms import StudentForm, LoginForm, RegisterForm, ChangePasswordForm
from .serializers import StudentSerializer
from rest_framework.decorators import api_view


def login_view(request):
    if request.user.is_authenticated:
        return redirect('students')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('students')
            else:
                form.add_error(None, 'Invalid username or password.')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('students')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('students')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def home(request):
    data = {
        'title' : 'Python Full Stack Development',
        'instructor' : 'Gladden'
    }
    return render(request,'home.html',data)

@login_required(login_url='login')
def students_page(request):
    students_qs = Student.objects.order_by('id')
    query = request.GET.get('search')
    if query:
        students_qs = students_qs.filter(name__icontains=query) | students_qs.filter(course__icontains=query)

    # paginate results (10 per page)
    paginator = Paginator(students_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'students.html', {
        'students': page_obj,
        'query': query
    })


@login_required(login_url='login')
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students')
    else:
        form = StudentForm()
    return render(request,'add_student.html',{'form':form})


@login_required(login_url='login')
def delete_student(request,id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('students')


@login_required(login_url='login')
def edit_student(request,id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        course = request.POST.get('course')
        marks = request.POST.get('marks')

        try:
            if int(marks) > 100 or int(marks) < 0:
                return render(request, 'edit_student.html', {
                    'student': student,
                    'error': 'Marks must be between 0 and 100'
                })
        except (TypeError, ValueError):
            return render(request, 'edit_student.html', {
                'student': student,
                'error': 'Invalid marks value'
            })

        student.name = name
        student.age = age
        student.course = course
        student.marks = marks
        student.save()

        return redirect('students')

    return render(request, 'edit_student.html', {'student': student})


def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            user = users.first()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
            request.session['password_reset_link'] = link
            return redirect('password_reset_done')
        else:
            error = 'No account found with that email address.'
            return render(request, 'reset_password.html', {'error': error})
    return render(request, 'reset_password.html')


def password_reset_done(request):
    link = request.session.pop('password_reset_link', None)
    return render(request, 'reset_password_done.html', {'reset_link': link})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'reset_password_confirm.html', {'form': form})
    else:
        return render(request, 'reset_password_confirm.html', {'invalid': True})


def password_reset_complete(request):
    return render(request, 'reset_password_complete.html')


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('change_password_success')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required(login_url='login')
def change_password_success(request):
    return render(request, 'change_password_success.html')

# creating an api
@api_view(['GET'])
def student_api(request):
    students = Student.objects.all()
    serializer = StudentSerializer(students,many=True)
    return JsonResponse(serializer.data,safe=False)