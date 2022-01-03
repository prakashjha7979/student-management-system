import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse

from student_management_app.EmailBackEnd import EmailBackEnd
from student_management_app.models import Courses, CustomUser, SessionYearModel



def showDemoPage(request):
    return render(request,"demo.html")

def ShowLoginPage(request):
    return render(request,"login_page.html")

def doLogin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user!=None:
            login(request,user)
            if user.user_type=="1":
                return HttpResponseRedirect('/admin_home')
            elif user.user_type=="2":
                return HttpResponseRedirect(reverse("staff_home"))
            else:
                return HttpResponseRedirect(reverse("student_home"))
        else:
            messages.error(request,"Invalid Login Details")
            return HttpResponseRedirect("/")
            

def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def signup_admin(request):
    return render(request,"signup_admin_page.html")

def do_admin_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=1)
        user.save()
        messages.success(request,"Successfully Created Admin")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Admin")
        return HttpResponseRedirect(reverse("show_login"))


def signup_student(request):
    courses=Courses.objects.all()
    session_years=SessionYearModel.object.all()
    return render(request,"signup_student_page.html",{"courses":courses,"session_years":session_years})

def signup_staff(request):
    return render(request,"signup_staff_page.html")

def do_staff_signup(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    password=request.POST.get("password")
    address=request.POST.get("address")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=2)
        user.staffs.address=address
        user.save()
        messages.success(request,"Successfully Created Staff")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Staff")
        return HttpResponseRedirect(reverse("show_login"))

def do_signup_student(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    father_name = request.POST.get("father_name")
    mother_name = request.POST.get("mother_name")
    date_of_birth = request.POST.get("date_of_birth")
    religion = request.POST.get("religion")
    cast = request.POST.get("cast")
    category = request.POST.get("category")
    admission_type = request.POST.get("admission_type")
    admission_status = request.POST.get("admission_status")
    admission_status = request.POST.get("admission_status")
    mobile = request.POST.get("mobile")
    qualification = request.POST.get("qualification")
    communication_address = request.POST.get("communication_address")
    permanent_address = request.POST.get("permanent_address")
    session_year_id = request.POST.get("session_year")
    course_id = request.POST.get("course")
    gender = request.POST.get("gender")

    profile_pic = request.FILES['profile_pic']
    fs = FileSystemStorage()
    filename = fs.save(profile_pic.name, profile_pic)
    profile_pic_url = fs.url(filename)

    #try:
    user = CustomUser.objects.create_user(username=username, password=password, email=email, last_name=last_name, first_name=first_name, user_type=3)
    user.students.father_name = father_name
    user.students.mother_name = mother_name
    user.students.date_of_birth = date_of_birth
    user.students.religion = religion
    user.students.cast = cast
    user.students.category = category
    user.students.admission_type = admission_type
    user.students.admission_status = admission_status
    user.students.mobile = mobile
    user.students.qualification = qualification
    user.students.permanent_address = permanent_address
    user.students.communication_address = communication_address
    course_obj = Courses.objects.get(id=course_id)
    user.students.course_id = course_obj
    session_year = SessionYearModel.object.get(id=session_year_id)
    user.students.session_year_id = session_year
    user.students.gender = gender
    user.students.profile_pic = profile_pic_url
    user.save()
    messages.success(request, "Successfully Added Student")
    return HttpResponseRedirect(reverse("show_login"))
    #except:
     #   messages.error(request, "Failed to Add Student")
      #  return HttpResponseRedirect(reverse("show_login"

