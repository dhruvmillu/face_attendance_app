from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout,login, models 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from profiles.models import Profile, Log
from django import forms
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import base64
import face_recognition
from .forms import ProfileForm, UserRegistrationForm
import os
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.conf import settings
from django.forms.models import model_to_dict
from zoneinfo import ZoneInfo

from datetime import datetime, timedelta

class MyLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class MyLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        # Check if the 'next' parameter is included in the request
        if 'next' in self.request.GET:
            # If 'next' is present, use the default behavior of the LoginView
            return super().form_valid(form)
        else:
            # If 'next' is not present, redirect to the dashboard
            login(self.request, form.get_user())
            return redirect('dashboard')
        
def findUser(request):
    # do something
    photo = request.POST.get('key')
    format, imgstr = photo.split(';base64,')
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr), name=f'student.{ext}')
    img = face_recognition.load_image_file(data)            
    print("successfully loaded image")
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)[0]
    images = Profile.objects.all().values_list('photo','user_id',"id")
    
    # search user with matching photo
    encodings=[]
    for image in images:
        path = os.path.join(settings.MEDIA_ROOT,image[0])
        print(path)
        encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(path))[0])
    matches = face_recognition.compare_faces(encodings, face_encodings,tolerance=0.7)
    print(matches)
    if True in matches:
            index = matches.index(True)
            user_id = images[index][1]
            user = User.objects.get(id=user_id)
            dt = datetime.now(tz=ZoneInfo("Asia/Kolkata")) 
            dtl = dt - timedelta(hours=1)
            user_dict = {'username':user.username,'first_name':user.first_name,'last_name':user.last_name,'email':user.email,'id':user_id,'pid':images[index][2]}
            lg = Log.objects.filter(profile_id=images[index][2],created_at__gte=dtl)
            print("log",lg,len(lg), dt > dtl)
            att = len(lg) == 0 
            print("attendance",att)
            print("found user", user_dict)
            return JsonResponse({'success': True,'user':user_dict,'attendance':att})
    else:
            print("user not found")
            return JsonResponse({'success': False})
        
class AttendanceForm(forms.Form):
    image = forms.CharField(widget=forms.HiddenInput())
    profile = forms.CharField(widget=forms.HiddenInput())
    is_correct = forms.BooleanField(widget=forms.HiddenInput())
    pid = forms.CharField(widget=forms.HiddenInput())
        
def attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('image'):
                photo = form.cleaned_data.get('image')
                dt = datetime.now(tz=ZoneInfo("Asia/Kolkata")) 
                format, imgstr = photo.split(';base64,')
                ext = format.split('/')[-1]
                savestr = f'{dt.year}-{dt.month}-{dt.day}-{dt.hour}-{dt.minute}-{dt.second}'
                data = ContentFile(base64.b64decode(imgstr), name=f'{savestr}.{ext}')
                profile = get_object_or_404(Profile,user_id=form.cleaned_data.get('profile'))
                print("\n\n",profile,"profile found")
                log = Log.objects.create(profile=profile, image=data, is_correct=True)
                print(data.name)
                
                
            
            
    form = AttendanceForm()
    context= {'form':form}
    return render(request, 'attendance.html', context)
        
@login_required
def dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    logs = Log.objects.filter(profile=profile)
    data = {}
    for log in logs:
        dt = datetime.fromtimestamp(log.created_at.timestamp())
        date = str(dt.date())
        if date not in data:
            data[date] = []
        data[date].append([str(dt.time())[:-7],"Present"])
    print(data)
    return render(request, 'dashboard.html',{'user':request.user,'profile':profile,'attendance':data})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})



@login_required
def edit_profile(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        profile = None
    print(profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('photo'):
                print("photo exists")
                photo = form.cleaned_data.get('photo')
                print(photo)
                format, imgstr = photo.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'{request.user.first_name}.{ext}')
                
                
                print(request.user.first_name)
                
                if profile:
                    print("profile exists")
                    profile.bio = form.cleaned_data.get('bio')
                    profile.photo.save(f'{data.name}', data, save=False)
                    profile.save(force_update=True)
                else:
                    print("profile does not exist")
                    bio = form.cleaned_data.get('bio')
                    Profile.objects.create(user=request.user, photo=data, bio=bio)
                return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
        if profile:
            context = {'form': form, 'profile': profile}
        else:
            context = {'form': form}
        return render(request, 'edit_profile.html', context)