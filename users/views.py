from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView, DetailView, FormView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from .models import User, DriverLicenseVerification, UserBalance
from .forms import (
    UserRegistrationForm, UserProfileUpdateForm, CustomPasswordChangeForm,
    DriverLicenseVerificationForm, AdminVerificationForm, BalanceAddForm
)

class UserRegistrationView(CreateView):
    """View for user registration"""
    form_class = UserRegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Account created successfully! You can now log in.')
        return super().form_valid(form)

class UserProfileView(LoginRequiredMixin, UpdateView):
    """View for user profile"""
    model = User
    form_class = UserProfileUpdateForm
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated!')
        return super().form_valid(form)

@login_required
def change_password_view(request):
    """View for changing user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

class DriverLicenseVerificationCreateView(LoginRequiredMixin, CreateView):
    """View for creating a driver license verification request"""
    model = DriverLicenseVerification
    form_class = DriverLicenseVerificationForm
    template_name = 'driver_verification_form.html'
    success_url = reverse_lazy('verification-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Your driver license verification request has been submitted!')
        return super().form_valid(form)

class DriverLicenseVerificationListView(LoginRequiredMixin, ListView):
    """View for listing user's driver license verification requests"""
    model = DriverLicenseVerification
    template_name = 'driver_verification_list.html'
    context_object_name = 'verifications'
    
    def get_queryset(self):
        return DriverLicenseVerification.objects.filter(user=self.request.user)

class AdminVerificationListView(UserPassesTestMixin, ListView):
    model = DriverLicenseVerification
    template_name = 'admin_verification_list.html'
    context_object_name = 'verifications'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_verifications'] = DriverLicenseVerification.objects.filter(status='pending').order_by('-created_at')
        context['approved_verifications'] = DriverLicenseVerification.objects.filter(status='approved').order_by('-created_at')
        context['rejected_verifications'] = DriverLicenseVerification.objects.filter(status='rejected').order_by('-created_at')
        return context

class AdminVerificationUpdateView(UserPassesTestMixin, UpdateView):
    """Admin view for updating a verification request"""
    model = DriverLicenseVerification
    form_class = AdminVerificationForm
    template_name = 'admin_verification_detail.html'
    success_url = reverse_lazy('admin-verification-list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        verification = form.save()
        
        # If verification is approved, update user status
        if verification.status == 'approved':
            user = verification.user
            user.is_verified_driver = True
            user.save()
            messages.success(self.request, f'Driver verification for {user.username} approved!')
        elif verification.status == 'rejected':
            messages.info(self.request, f'Driver verification for {verification.user.username} rejected.')
            
        return super().form_valid(form)

@login_required
def user_balance_view(request):
    """View for displaying and adding to user balance"""
    # Get or create user balance
    balance, created = UserBalance.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = BalanceAddForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            balance.amount += amount
            balance.save()
            messages.success(request, f'Successfully added {amount} to your balance!')
            return redirect('balance')
    else:
        form = BalanceAddForm()
    
    return render(request, 'balance.html', {
        'balance': balance,
        'form': form
    })