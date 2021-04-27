from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
# Authentication
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

# form and models
from account.models import Profile
from account.forms import ProfileForm, SingUpForm

#messages api
from django.contrib import messages


def sign_up(request):
    form = SingUpForm()
    if request.method == 'POST':
        form = SingUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account created successfully! you can login to your account.")
            return HttpResponseRedirect(reverse('account:login'))
    context = {
        'form': form
    }
    return render(request, 'account/signup.html', context)


def login_user(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Shopping Unlimited with 25% Off")
                return HttpResponseRedirect(reverse('store:index'))
    context = {
        'form': form
    }
    return render(request, 'account/login.html', context)


@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "Login to your account.")
    return HttpResponseRedirect(reverse('store:index'))


@login_required
def user_profile(request):
    profile = Profile.objects.get(user=request.user)

    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Data updated successfully")
            form = ProfileForm(instance=profile)
    context = {
        'form': form
    }
    return render(request, 'account/change_profile.html', context)













