import datetime
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls.base import reverse
import student_management_app

from student_management_app.models import Attendance, AttendanceReport, Courses, CustomUser, FeedBackStudent, LeaveReportStudent, SessionYearModel, StudentDocument, Students, Subjects


def student_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=student_obj.course.id)
    subjects=Subjects.objects.filter(course_id=course).count()
    subjects_data=Subjects.objects.filter(course_id=course)
    session_obj=SessionYearModel.object.get(id=student_obj.session_year.id)
    

    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True,student_id=student_obj.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False,student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    return render(request,"student_template/student_home_template.html",{"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent})

def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=student.course_id
    subjects=Subjects.objects.filter(course_id=course)
    return render(request,"student_template/student_view_attendance.html",{"subjects":subjects})

def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")

    start_data_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_data_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subjects.objects.get(id=subject_id)
    user_object=CustomUser.objects.get(id=request.user.id)
    stud_obj=Students.objects.get(admin=user_object)

    attendance=Attendance.objects.filter(attendance_date__range=(start_data_parse,end_data_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
    return render(request,"student_template/student_attendance_data.html",{"attendance_reports":attendance_reports})


def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    return render(request,"student_template/student_profile.html",{"user":user,"student":student})

def student_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        permanent_address=request.POST.get("permanent_address")
        communication_address=request.POST.get("communication_address")
        profile_pic=request.POST.get("profile_pic")
        if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            student=Students.objects.get(admin=customuser)
            student.permanent_address=permanent_address 
            student.communication_address=communication_address
            if profile_pic_url!=None:
                    student.profile_pic=profile_pic_url
            student.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("student_profile"))

def student_apply_leave(request):
    staff_obj = Students.objects.get(admin=request.user.id)
    leave_data=LeaveReportStudent.objects.filter(student_id=staff_obj)
    return render(request,"student_template/student_apply_leave.html",{"leave_data":leave_data})

def student_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStudent(student_id=student_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))
        except:
            messages.error(request, "Failed To Apply for Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))


def student_feedback(request):
    staff_id=Students.objects.get(admin=request.user.id)
    feedback_data=FeedBackStudent.objects.filter(student_id=staff_id)
    return render(request,"student_template/student_feedback.html",{"feedback_data":feedback_data})

def student_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStudent(student_id=student_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("student_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("student_feedback"))


def student_dashboard(request):
    user=CustomUser.objects.get(id=request.user.id)
    # student_objct=Students.objects.get(admin=user)
    students=Students.objects.filter(admin=user)
    # students=user.object.get(admin=Students)
    return render(request,"student_template/student_dashboard.html",{"user":user,"students":students})

def student_document(request):
    std_documents = None
    # request.session['student_id']=student_id
    user=CustomUser.objects.get(id=request.user.id)
    students=Students.objects.filter(admin=user).get()
    if students != None:
        std_documents_exists=StudentDocument.objects.filter(student_id=students).exists()
        if std_documents_exists == False:
            std_documents=StudentDocument.objects.create(student_id=students)
        else:
            std_documents=StudentDocument.objects.get(student_id=students)

    return render(request,"student_template/student_document.html",{"user":user,"students":students,"std_documents":std_documents})

def student_document_save(request):
    # student_id=request.session.get("student_id")
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
        return HttpResponseRedirect(reverse("student_document"))
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


            customuser=CustomUser.objects.get(id=request.user.id)
            student=Students.objects.get(admin=customuser)
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
                StudentDocument.objects.create(student_id_id=student,hsc_marksheet=hsc_marksheet_url,hsc_certificate=hsc_certificate_url,ssc_marksheet=ssc_marksheet_url,ssc_certificate=ssc_certificate_url,ug_marksheet=ug_marksheet_url,ug_certificate=ug_certificate_url,pg_marksheet=pg_marksheet_url,pg_certificate=pg_certificate_url,diploma_marksheet=diploma_marksheet_url,diploma_certificate=diploma_certificate_url,cc=cc_url,caste=caste_url,tc=tc_url,migration=migration_url,gap=gap_url,medical=medical_url,income=income_url,residence=residence_url,pan_card=pan_card_url,aadhar_card=aadhar_card_url,sk_form=sk_form_url,affidavit=affidavit_url,fee_commitment=fee_commitment_url,checklist=checklist_url,anti_ragging=anti_ragging_url,other=other_url,photo=photo_url,signature=signature_url)

            messages.success(request, "Successfully Uploaded document")
            return HttpResponseRedirect(reverse("student_document"))            
        except:
            messages.error(request, "Failed to Uploaded document")
            return HttpResponseRedirect(reverse("student_document"))
