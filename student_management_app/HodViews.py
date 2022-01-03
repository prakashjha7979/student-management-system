import datetime
from typing import Reversible

from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.backends import UserModel
from django.core.files.storage import FileSystemStorage
from django.db.models.fields import DateTimeCheckMixin, DateTimeField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from student_management_app.StudentViews import student_document
from student_management_app.forms import AddCourseForm, AddStudentForm,EditStudentForm
from django.views.decorators.csrf import csrf_exempt

from student_management_app.models import Attendance, AttendanceReport, CustomUser, SessionYearModel, Staffs, Courses, StudentDocument, Students, Subjects


def admin_home(request):
    student_count1=Students.objects.all().count()
    staff_count=Staffs.objects.all().count()
    subject_count=Subjects.objects.all().count()
    course_count=Courses.objects.all().count()

    course_all=Courses.objects.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        subjects=Subjects.objects.filter(course=course.id).count()
        students=Students.objects.filter(course=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all=Subjects.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=Courses.objects.get(id=subject.course.id)
        student_count=Students.objects.filter(course=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs=Staffs.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subjects.objects.filter(staff=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        # leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        # attendance_absent_list_staff.append(leaves)
        attendance_present_list_staff.append(attendance)
        staff_name_list.append(staff.admin.username)

    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(absent)
        student_name_list.append(student.admin.username)


    return render(request,"hod_template/home_content.html",{"student_count":student_count1,"staff_count":staff_count,"subject_count":subject_count,"course_count":course_count,"course_name_list":course_name_list,"subject_count_list":subject_count_list,"student_count_list_in_course":student_count_list_in_course,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"staff_name_list":staff_name_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student})

def add_staff(request):
    return render(request,"hod_template/add_staff_template.html")

def add_staff_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
            user.staffs.address=address
            user.save()
            messages.success(request,"Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request,"Failed to Add Staff")
            return HttpResponseRedirect(reverse("add_staff"))

def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return HttpResponseRedirect(reverse("manage_staff"))
    except:
        messages.error(request, "Failed to Delete Staff.")
        return HttpResponseRedirect(reverse("manage_staff"))

def add_course(request):
    course_form=AddCourseForm()
    return render(request,"hod_template/add_course_template.html",{"course_form":course_form})



def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course_form=AddCourseForm(request.POST)

        if course_form.is_valid():
            course_exists=True if (Courses.objects.filter(course_name=course_form.cleaned_data["course_name"]).exists()) else False
            if not course_exists:
                course_name=course_form.cleaned_data["course_name"]
                course_model = Courses(course_name=course_name)
                course_model.save(force_insert=True)
                messages.success(request, "Course Added Successfully!")
                return HttpResponseRedirect(reverse("add_course"))
            else:
                messages.error(request,"Course already exists")
                return HttpResponseRedirect(reverse("add_course"))
        else:
            form=AddCourseForm(request.POST)
            return render(request,"hod_template/add_course_template.html",{"form":form})



        

def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return HttpResponseRedirect(reverse("manage_course"))
    except:
        messages.error(request, "Failed to Delete Course.")
        return HttpResponseRedirect(reverse("manage_course"))

def add_student(request):
    # form=AddStudentForm()
    courses = []
    try:
        list_courses = Courses.objects.all()
        for course in list_courses:
            small_course=(course.id,course.course_name)
            courses.append(small_course)

    except:
        courses = []
    
    sessions = []
    try:
        session_list = SessionYearModel.object.all()

        for ses in session_list:
            small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
            sessions.append(small_ses)
    except:
        sessions=[]

    form=AddStudentForm(courses,sessions)
    return render(request,"hod_template/add_student_template.html",{"form":form})

def add_student_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    
    else:
        # breakpoint()
        form=AddStudentForm(get_course_list,get_session_list,request.POST,request.FILES)
        # form=AddStudentForm(request.POST,request.FILES)

        
        if form.is_valid():
            email_exists=True if (CustomUser.objects.filter(email=form.cleaned_data["email"]).exists()) else False
            username_exists=True if (CustomUser.objects.filter(username=form.cleaned_data["username"]).exists()) else False
            if not email_exists and not username_exists:
                first_name=form.cleaned_data["first_name"]
                last_name=form.cleaned_data["last_name"]
                username=form.cleaned_data["username"]
                email=form.cleaned_data["email"]
                password=form.cleaned_data["password"]
                father_name=form.cleaned_data["father_name"]
                mother_name=form.cleaned_data["mother_name"]
                date_of_birth=form.cleaned_data["date_of_birth"]
                religion=form.cleaned_data["religion"]
                cast=form.cleaned_data["cast"]
                category=form.cleaned_data["category"]
                admission_type=form.cleaned_data["admission_type"]
                admission_status=form.cleaned_data["admission_status"]
                permanent_address=form.cleaned_data["permanent_address"]
                communication_address=form.cleaned_data["communication_address"]
                session_year=form.cleaned_data["session_year"]
                mobile=form.cleaned_data["mobile"]
                qualification=form.cleaned_data["qualification"]
                course=form.cleaned_data["course"]
                gender=form.cleaned_data["gender"]

                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
                # try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.students.permanent_address=permanent_address
                user.students.communication_address=communication_address
                course_obj=Courses.objects.get(id=course)
                user.students.course=course_obj

                session_year_obj=SessionYearModel.object.get(id=session_year)
                user.students.session_year=session_year_obj
                user.students.gender=gender
                user.students.father_name=father_name
                user.students.mother_name=mother_name
                user.students.date_of_birth=date_of_birth
                user.students.religion=religion
                user.students.cast=cast
                user.students.category=category
                user.students.admission_type=admission_type
                user.students.admission_status=admission_status
                user.students.mobile=mobile
                user.students.qualification=qualification
                user.students.profile_pic=profile_pic_url
                user.save()
                messages.success(request,"Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))

            else:
                messages.error(request,"Username or Email already exists")
                return HttpResponseRedirect(reverse("add_student"))
            # except:
            #     messages.error(request,"Failed to Add Student")
            #     return HttpResponseRedirect(reverse("add_student"))
        else:
            # form=AddStudentForm(request=request)
            # form=AddStudentForm(request.POST)
            form=AddStudentForm(get_course_list,get_session_list,request.POST)
            return render(request,"hod_template/add_student_template.html",{"form":form})


def delete_student(request,student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')

def add_subject(request):
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/add_subject_template.html",{"staffs":staffs,"courses":courses})

def add_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        if request.POST.get('subject_name')=="":
            messages.error(request, "Failed to Add Subject!")
            return HttpResponseRedirect("add_subject")
        else:
            subject_name=request.POST.get("subject_name")
            course=request.POST.get("course")
            course=Courses.objects.get(id=course)
            staff=request.POST.get("staff")
            staff=CustomUser.objects.get(id=staff)

        try:
            subject=Subjects(subject_name=subject_name,course=course,staff=staff)
            subject.save()
            messages.success(request,"Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request,"Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))

def manage_staff(request):
    staffs=Staffs.objects.all()
    return render(request,"hod_template/manage_staff_template.html",{"staffs":staffs})

def manage_student(request):
    students=Students.objects.all()
    return render(request,"hod_template/manage_student_template.html",{"students":students})

def manage_course(request):
    courses=Courses.objects.all()
    return render(request,"hod_template/manage_course_template.html",{"courses":courses})

def manage_subject(request):
    subjects=Subjects.objects.all()
    return render(request,"hod_template/manage_subject_template.html",{"subjects":subjects})

def edit_staff(request,staff_id):
    staff=Staffs.objects.get(admin=staff_id)
    return render(request,"hod_template/edit_staff_template.html",{"staff":staff,"id":staff_id})

def edit_staff_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id=request.POST.get("staff_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")

        try:
            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            staff_model=Staffs.objects.get(admin=staff_id)
            staff_model.address=address
            staff_model.save()
            messages.success(request,"Successfully Edited Staff")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))
        except:
            messages.error(request,"Failed to Edit Staff")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))

def edit_student(request,student_id):
    request.session['student_id']=student_id
    student=Students.objects.get(admin=student_id)
    form=EditStudentForm()
    form.fields['email'].initial=student.admin.email
    form.fields['first_name'].initial=student.admin.first_name
    form.fields['last_name'].initial=student.admin.last_name
    form.fields['username'].initial=student.admin.username
    form.fields['profile_pic'].initial=student.profile_pic
    form.fields['course'].initial=student.course.id
    form.fields['gender'].initial=student.gender
    form.fields['father_name'].initial=student.father_name
    form.fields['mother_name'].initial=student.mother_name
    form.fields['date_of_birth'].initial=student.date_of_birth
    form.fields['religion'].initial=student.religion
    form.fields['cast'].initial=student.cast
    form.fields['category'].initial=student.category
    form.fields['admission_type'].initial=student.admission_type
    form.fields['admission_status'].initial=student.admission_type
    form.fields['permanent_address'].initial=student.permanent_address
    form.fields['communication_address'].initial=student.communication_address
    form.fields['session_year'].initial=student.session_year.id
    form.fields['mobile'].initial=student.mobile
    form.fields['qualification'].initial=student.qualification
    return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

def edit_student_save(request):
    if request.method !="POST":
        return HttpResponse("<h2>Method Not allowed</h2>")
    else:
        student_id=request.session.get("student_id")
        if student_id==None:
            return HttpResponseRedirect("manage_student")

        form=EditStudentForm(request.POST,request.FILES)
        
        # student_id=request.POST.get("student_id")
        
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            father_name=form.cleaned_data["father_name"]
            mother_name=form.cleaned_data["mother_name"]
            date_of_birth=form.cleaned_data["date_of_birth"]
            religion=form.cleaned_data["religion"]
            cast=form.cleaned_data["cast"]
            category=form.cleaned_data["category"]
            admission_type=form.cleaned_data["admission_type"]
            admission_status=form.cleaned_data["admission_status"]
            permanent_address=form.cleaned_data["permanent_address"]
            communication_address=form.cleaned_data["communication_address"]
            session_year=form.cleaned_data["session_year"]
            mobile=form.cleaned_data["mobile"] 
            qualification=form.cleaned_data["qualification"]
            course=form.cleaned_data["course"]
            gender=form.cleaned_data["gender"]

            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None

            try:
                user=CustomUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()

                student=Students.objects.get(admin=student_id)
                student.father_name=father_name
                student.mother_name=mother_name
                student.date_of_birth=date_of_birth
                student.religion=religion
                student.cast=cast
                student.category=category
                student.admission_type=admission_type
                student.admission_status=admission_status
                student.permanent_address=permanent_address
                student.communication_address=communication_address
                session_year = SessionYearModel.object.get(id=session_year)
                student.session_year_id = session_year
                student.mobile=mobile
                student.qualification=qualification
                course=Courses.objects.get(id=course)
                student.course_id=course
                student.gender=gender
                if profile_pic_url!=None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,"Successfully Edited Student Record")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
            except:
                messages.error(request,"Failed to Edit Student Record")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
        else:
            form=EditStudentForm(request.POST)
            student=Students.objects.get(admin=student_id)
            return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})


def hod_document(request,student_id):
    # breakpoint()
    request.session['student_id']=student_id
    student=Students.objects.get(admin=student_id)
    std_documents_exists=StudentDocument.objects.filter(student_id=student).exists()
    if std_documents_exists == False:
            std_documents=StudentDocument.objects.create(student_id=student)
    else:
        std_documents=StudentDocument.objects.get(student_id=student)
    
    
    return render(request,"hod_template/hod_document.html",{"std_documents":std_documents,"student":student})


def hod_document_save(request):
    # breakpoint()
    # request.session['student_id']=student_id
    student_id=request.session.get("student_id")
    if student_id==None:
        return HttpResponseRedirect("manage_student")
    
    hsc_marksheet_url= None
    hsc_certificate_url= None
    ssc_marksheet_url= None
    ssc_certificate_url= None
    ug_marksheet_url= None
    ug_certificate_url= None
    pg_marksheet_url= None
    pg_certificate_url= None
    diploma_marksheet_url= None
    diploma_certificate_url= None
    cc_url = None
    caste_url = None
    tc_url = None
    migration_url = None
    gap_url = None
    medical_url = None
    income_url = None
    residence_url = None
    pan_card_url = None
    aadhar_card_url = None
    sk_form_url = None
    affidavit_url = None
    fee_commitment_url = None
    checklist_url = None
    anti_ragging_url = None
    other_url = None
    photo_url = None
    signature_url = None

    if request.method!="POST":
        return HttpResponseRedirect(reverse("hod_document"))
    else:
        hsc_marksheet=request.POST.get("hsc_marksheet")
        hsc_certificate=request.POST.get("hsc_certificate")
        ssc_marksheet=request.POST.get("ssc_marksheet")
        ssc_certificate=request.POST.get("ssc_certificate")
        ug_marksheet=request.POST.get("ug_marksheet")
        ug_certificate=request.POST.get("ug_certificate")
        pg_marksheet=request.POST.get("pg_marksheet")
        pg_certificate=request.POST.get("pg_certificate")
        diploma_marksheet=request.POST.get("diploma_marksheet")
        diploma_certificate=request.POST.get("diploma_certificate")
        cc=request.POST.get("cc")
        caste=request.POST.get("caste")
        tc=request.POST.get("tc")
        migration=request.POST.get("migration")
        gap=request.POST.get("gap")
        medical=request.POST.get("medical")
        income=request.POST.get("income")
        residence=request.POST.get("residence")
        pan_card=request.POST.get("pan_card")
        aadhar_card=request.POST.get("aadhar_card")
        sk_form=request.POST.get("sk_form")
        affidavit=request.POST.get("affidavit")
        fee_commitment=request.POST.get("fee_commitment")
        checklist=request.POST.get("checklist")
        anti_ragging=request.POST.get("anti_ragging")
        other=request.POST.get("other")
        photo=request.POST.get("photo")
        signature=request.POST.get("signature")
        # breakpoint()
        
        try:
            if request.FILES.get('hsc_marksheet',False):
                hsc_marksheet=request.FILES['hsc_marksheet']
                fs=FileSystemStorage()
                filename=fs.save(hsc_marksheet.name,hsc_marksheet)
                hsc_marksheet_url=fs.url(filename)
            
            if request.FILES.get('hsc_certificate',False):
                hsc_certificate=request.FILES['hsc_certificate']
                fs=FileSystemStorage()
                filename=fs.save(hsc_certificate.name,hsc_certificate)
                hsc_certificate_url=fs.url(filename)

            if request.FILES.get('ssc_marksheet',False):
                ssc_marksheet=request.FILES['ssc_marksheet']
                fs=FileSystemStorage()
                filename=fs.save(ssc_marksheet.name,ssc_marksheet)
                ssc_marksheet_url=fs.url(filename)

            if request.FILES.get('ssc_certificate',False):
                ssc_certificate=request.FILES['ssc_certificate']
                fs=FileSystemStorage()
                filename=fs.save(ssc_certificate.name,ssc_certificate)
                ssc_certificate_url=fs.url(filename)
            
            if request.FILES.get('ug_marksheet',False):
                ug_marksheet=request.FILES['ug_marksheet']
                fs=FileSystemStorage()
                filename=fs.save(ug_marksheet.name,ug_marksheet)
                ug_marksheet_url=fs.url(filename)

            if request.FILES.get('ug_certificate',False):
                ug_certificate=request.FILES['ug_certificate']
                fs=FileSystemStorage()
                filename=fs.save(ug_certificate.name,ug_certificate)
                ug_certificate_url=fs.url(filename)

            if request.FILES.get('pg_marksheet',False):
                pg_marksheet=request.FILES['pg_marksheet']
                fs=FileSystemStorage()
                filename=fs.save(pg_marksheet.name,pg_marksheet)
                pg_marksheet_url=fs.url(filename)

            if request.FILES.get('pg_certificate',False):
                pg_certificate=request.FILES['pg_certificate']
                fs=FileSystemStorage()
                filename=fs.save(pg_certificate.name,pg_certificate)
                pg_certificate_url=fs.url(filename)

            if request.FILES.get('diploma_marksheet',False):
                diploma_marksheet=request.FILES['diploma_marksheet']
                fs=FileSystemStorage()
                filename=fs.save(diploma_marksheet.name,diploma_marksheet)
                diploma_marksheet_url=fs.url(filename)

            if request.FILES.get('diploma_certificate',False):
                diploma_certificate=request.FILES['diploma_certificate']
                fs=FileSystemStorage()
                filename=fs.save(diploma_certificate.name,diploma_certificate)
                diploma_certificate_url=fs.url(filename)

            if request.FILES.get('cc',False):
                cc=request.FILES['cc']
                fs=FileSystemStorage()
                filename=fs.save(cc.name,cc)
                cc_url=fs.url(filename)

            if request.FILES.get('caste',False):
                caste=request.FILES['caste']
                fs=FileSystemStorage()
                filename=fs.save(caste.name,caste)
                caste_url=fs.url(filename)

            if request.FILES.get('tc',False):
                tc=request.FILES['tc']
                fs=FileSystemStorage()
                filename=fs.save(tc.name,tc)
                tc_url=fs.url(filename)

            if request.FILES.get('migration',False):
                migration=request.FILES['migration']
                fs=FileSystemStorage()
                filename=fs.save(migration.name,migration)
                migration_url=fs.url(filename)

            if request.FILES.get('gap',False):
                gap=request.FILES['gap']
                fs=FileSystemStorage()
                filename=fs.save(gap.name,gap)
                gap_url=fs.url(filename)

            if request.FILES.get('medical',False):
                medical=request.FILES['medical']
                fs=FileSystemStorage()
                filename=fs.save(medical.name,medical)
                medical_url=fs.url(filename)

            if request.FILES.get('income',False):
                income=request.FILES['income']
                fs=FileSystemStorage()
                filename=fs.save(income.name,income)
                income_url=fs.url(filename)

            if request.FILES.get('residence',False):
                residence=request.FILES['residence']
                fs=FileSystemStorage()
                filename=fs.save(residence.name,residence)
                residence_url=fs.url(filename)

            if request.FILES.get('pan_card',False):
                pan_card=request.FILES['pan_card']
                fs=FileSystemStorage()
                filename=fs.save(pan_card.name,pan_card)
                pan_card_url=fs.url(filename)

            if request.FILES.get('aadhar_card',False):
                aadhar_card=request.FILES['aadhar_card']
                fs=FileSystemStorage()
                filename=fs.save(aadhar_card.name,aadhar_card)
                aadhar_card_url=fs.url(filename)

            if request.FILES.get('sk_form',False):
                sk_form=request.FILES['sk_form']
                fs=FileSystemStorage()
                filename=fs.save(sk_form.name,sk_form)
                sk_form_url=fs.url(filename)

            if request.FILES.get('affidavit',False):
                affidavit=request.FILES['affidavit']
                fs=FileSystemStorage()
                filename=fs.save(affidavit.name,affidavit)
                affidavit_url=fs.url(filename)

            if request.FILES.get('fee_commitment',False):
                fee_commitment=request.FILES['fee_commitment']
                fs=FileSystemStorage()
                filename=fs.save(fee_commitment.name,fee_commitment)
                fee_commitment_url=fs.url(filename)

            if request.FILES.get('checklist',False):
                checklist=request.FILES['checklist']
                fs=FileSystemStorage()
                filename=fs.save(checklist.name,checklist)
                checklist_url=fs.url(filename)

            if request.FILES.get('anti_ragging',False):
                anti_ragging=request.FILES['anti_ragging']
                fs=FileSystemStorage()
                filename=fs.save(anti_ragging.name,anti_ragging)
                anti_ragging_url=fs.url(filename)

            if request.FILES.get('other',False):
                other=request.FILES['other']
                fs=FileSystemStorage()
                filename=fs.save(other.name,other)
                other_url=fs.url(filename)

            if request.FILES.get('photo',False):
                photo=request.FILES['photo']
                fs=FileSystemStorage()
                filename=fs.save(photo.name,photo)
                photo_url=fs.url(filename)

            if request.FILES.get('signature',False):
                signature=request.FILES['signature']
                fs=FileSystemStorage()
                filename=fs.save(signature.name,signature)
                signature_url=fs.url(filename)

            # breakpoint()
            # customuser=CustomUser.objects.get(id=request.user.id)
            student=Students.objects.get(admin=student_id)
            # stud_document=StudentDocument.objects.filter(student_id=student)
            # StudentDocument.objects.create(student_id=student,hsc_marksheet=hsc_marksheet_url)
            if StudentDocument.objects.filter(student_id=student).exists(): 
                stud_document=StudentDocument.objects.get(student_id=student)
                
                if hsc_marksheet_url!=None:
                    stud_document.hsc_marksheet=hsc_marksheet_url
                    stud_document.save()

                if hsc_certificate_url!=None:
                    stud_document.hsc_certificate=hsc_certificate_url
                    stud_document.save()

                if ssc_marksheet_url!=None:
                    stud_document.ssc_marksheet=ssc_marksheet_url
                    stud_document.save()

                if ssc_certificate_url!=None:
                    stud_document.ssc_certificate=ssc_certificate_url
                    stud_document.save()

                if ug_marksheet_url!=None:
                    stud_document.ug_marksheet=ug_marksheet_url
                    stud_document.save()

                if ug_certificate_url!=None:
                    stud_document.ug_certificate=ug_certificate_url
                    stud_document.save()

                if pg_marksheet_url!=None:
                    stud_document.pg_marksheet=pg_marksheet_url
                    stud_document.save()

                if pg_certificate_url!=None:
                    stud_document.pg_certificate=pg_certificate_url
                    stud_document.save()

                if diploma_marksheet_url!=None:
                    stud_document.diploma_marksheet=diploma_marksheet_url
                    stud_document.save()

                if diploma_certificate_url!=None:
                    stud_document.diploma_certificate=diploma_certificate_url
                    stud_document.save()

                if cc_url!=None:
                    stud_document.cc=cc_url
                    stud_document.save()

                if caste_url!=None:
                    stud_document.caste=caste_url
                    stud_document.save()

                if tc_url!=None:
                    stud_document.tc=tc_url
                    stud_document.save()

                if migration_url!=None:
                    stud_document.migration=migration_url
                    stud_document.save()

                if gap_url!=None:
                    stud_document.gap=gap_url
                    stud_document.save()

                if medical_url!=None:
                    stud_document.medical=medical_url
                    stud_document.save()

                if income_url!=None:
                    stud_document.income=income_url
                    stud_document.save()

                if residence_url!=None:
                    stud_document.residence=residence_url
                    stud_document.save()

                if pan_card!=None:
                    stud_document.pan_card=pan_card_url
                    stud_document.save()

                if aadhar_card_url!=None:
                    stud_document.aadhar_card=aadhar_card_url
                    stud_document.save()

                if sk_form!=None:
                    stud_document.sk_form=sk_form_url
                    stud_document.save()

                if affidavit!=None:
                    stud_document.affidavit=affidavit_url
                    stud_document.save()

                if fee_commitment!=None:
                    stud_document.fee_commitment=fee_commitment_url
                    stud_document.save()

                if checklist!=None:
                    stud_document.checklist=checklist_url
                    stud_document.save()

                if anti_ragging!=None:
                    stud_document.anti_ragging=anti_ragging_url
                    stud_document.save()

                if other!=None:
                    stud_document.other=other_url
                    stud_document.save()

                if photo!=None:
                    stud_document.photo=photo_url
                    stud_document.save()

                if signature!=None:
                    stud_document.signature=signature_url
                    stud_document.save()

            else:
                StudentDocument.objects.create(student_id=student,hsc_marksheet=hsc_marksheet_url,hsc_certificate=hsc_certificate_url,ssc_marksheet=ssc_marksheet_url,ssc_certificate=ssc_certificate_url,ug_marksheet=ug_marksheet_url,ug_certificate=ug_certificate_url,pg_marksheet=pg_marksheet_url,pg_certificate=pg_certificate_url,diploma_marksheet=diploma_marksheet_url,diploma_certificate=diploma_certificate_url,cc=cc_url,caste=caste_url,tc=tc_url,migration=migration_url,gap=gap_url,medical=medical_url,income=income_url,residence=residence_url,pan_card=pan_card_url,aadhar_card=aadhar_card_url,sk_form=sk_form_url,affidavit=affidavit_url,fee_commitment=fee_commitment_url,checklist=checklist_url,anti_ragging=anti_ragging_url,other=other_url,photo=photo_url,signature=signature_url)

            messages.success(request, "Successfully Uploaded document")
            return HttpResponseRedirect(reverse("hod_document",kwargs={"student_id":student_id}))            
        except:
            messages.error(request, "Failed to Uploaded document")
            return HttpResponseRedirect(reverse("hod_document",kwargs={"student_id":student_id}))


def edit_subject(request,subject_id):
    subject=Subjects.objects.get(id=subject_id)
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/edit_subject_template.html",{"subject":subject,"staffs":staffs,"courses":courses,"id":subject_id})

def edit_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get("subject_id")
        subject_name=request.POST.get("subject_name")
        staff_id=request.POST.get("staff")
        course_id=request.POST.get("course")

        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.subject_name=subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id=staff
            course=Courses.objects.get(id=course_id)
            subject.course_id=course
            subject.save()

            messages.success(request,"Successfully Edited Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))
        except:
            messages.error(request,"Failed to Edit Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))


def edit_course(request,course_id):
    course=Courses.objects.get(id=course_id)
    return render(request,"hod_template/edit_course_template.html",{"course":course,"id":course_id})

def edit_course_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id=request.POST.get("course_id")
        course_name=request.POST.get("course")
    try:
        course=Courses.objects.get(id=course_id)
        course.course_name=course_name
        course.save()
        messages.success(request,"Successfully Edited Course")
        return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))
    except:
            messages.error(request,"Failed to Edit Course")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))

def manage_session(request):
    return render(request,"hod_template/manage_session_template.html")

def add_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=SessionYearModel(session_start_year=session_start_year,session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("manage_session"))


def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"hod_template/admin_profile.html",{"user":user})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_course_exist(request):
    course=request.POST.get("course")
    course_obj=Courses.objects.filter(course=course).exists()
    if course_obj:
        return HttpResponse("Course already exists!")
    else:
        return HttpResponse(False)

def get_course_list():
    courses = []
    try:
        list_courses = Courses.objects.all()
        for course in list_courses:
            small_course=(course.id,course.course_name)
            courses.append(small_course)

    except:
        courses = []

    return courses

def get_session_list():
    sessions = []
    try:
        session_list = SessionYearModel.object.all()

        for ses in session_list:
            small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
            sessions.append(small_ses)
    except:
        sessions=[]

    return sessions
