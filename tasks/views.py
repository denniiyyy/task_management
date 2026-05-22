from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomUser, Task, AuditLog
from .forms import RegisterForm, TaskForm, ProfileForm

def log_audit(user, action, request, details=''):
    AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=request.META.get('REMOTE_ADDR'),
        details=details
    )

def admin_required(user):
    return user.is_authenticated and user.role == 'admin'

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password')
            return render(request, 'tasks/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            log_audit(user, 'LOGIN_SUCCESS', request)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            log_audit(None, 'LOGIN_FAILED', request, f'Failed login attempt for {username}')
            messages.error(request, 'Invalid username or password')
    return render(request, 'tasks/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password') # Grab the second password
        
        # INTENTIONAL CRASH: Force a ValueError if they don't match
        if password != confirm_password:
            raise ValueError("CRITICAL AUTHENTICATION FAILURE: Password and Confirm Password do not match!")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'tasks/register.html', {'form': RegisterForm(request.POST)})
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='user'
        )
        log_audit(user, 'LOGIN_SUCCESS', request, 'User registered successfully')
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('dashboard')
        
    else:
        form = RegisterForm()
        
    return render(request, 'tasks/register.html', {'form': form})

"""
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'tasks/register.html', {'form': form})
            
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='user'
            )
            log_audit(user, 'LOGIN_SUCCESS', request, 'User registered successfully')
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})
"""
@login_required
def logout_view(request):
    log_audit(request.user, 'LOGOUT', request)
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(created_by=request.user)
    return render(request, 'tasks/dashboard.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            log_audit(request.user, 'TASK_CREATED', request, f'Task: {task.title}')
            messages.success(request, 'Task created successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user.role != 'admin' and task.created_by != request.user:
        messages.error(request, 'You do not have permission to view this task')
        return redirect('dashboard')
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user.role != 'admin' and task.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this task')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'TASK_UPDATED', request, f'Task: {task.title}')
            messages.success(request, 'Task updated successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user.role != 'admin' and task.created_by != request.user:
        messages.error(request, 'You do not have permission to delete this task')
        return redirect('dashboard')
    
    if request.method == 'POST':
        log_audit(request.user, 'TASK_DELETED', request, f'Task: {task.title}')
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('dashboard')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def profile_view(request):
    return render(request, 'tasks/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'PROFILE_UPDATED', request)
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'tasks/profile_edit.html', {'form': form})

@login_required
@user_passes_test(admin_required)
def audit_log_view(request):
    logs = AuditLog.objects.all().order_by('-timestamp')[:100]
    return render(request, 'tasks/audit_log.html', {'logs': logs})

@login_required
@user_passes_test(admin_required)
def manage_users(request):
    users = CustomUser.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        user = get_object_or_404(CustomUser, id=user_id)
        old_role = user.role
        user.role = new_role
        user.save()
        log_audit(request.user, 'ROLE_CHANGED', request, f'User {user.username}: {old_role} -> {new_role}')
        messages.success(request, f'User {user.username} role updated to {new_role}')
        return redirect('manage_users')
    return render(request, 'tasks/manage_users.html', {'users': users})