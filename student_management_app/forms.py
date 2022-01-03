from django import forms
from django.forms import ChoiceField

from student_management_app.models import Courses, SessionYearModel, Subjects, Students


class ChoiceNoValidation(ChoiceField):
    def validate(self, value):
        pass


class DateInput(forms.DateInput):
    input_type = "date"

class NumberInput(forms.NumberInput):
    input_type = "number"

class AddStudentForm(forms.Form):
    def __init__(self,list_courses,session_list,*args,**kwargs):
        super(AddStudentForm,self).__init__(*args,**kwargs)
        self.fields['course'].choices = list_courses
        self.fields['session_year'].choices = session_list
        # self.fields['Course'].widget = forms.Select(attrs={"class":"form-control"})
        # self.list_courses=list_courses

    
    
    

    email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control","autocomplete":"off"}))
    password=forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name=forms.CharField(label="First Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name=forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    username=forms.CharField(label="Username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
    profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}))


    
    # try:
    #     courses = Courses.objects.all().order_by('-course_name')
    #     for course in courses:
    #         small_course=(course.id,course.course_name)
    #         course_list.append(small_course)
    # except:
    #     course_list=[]
    
    # def get(self,request,*args,**kwargs):
    #     try:
    #         courses = Courses.objects.all().order_by('-course_name')
    #         for course in courses:
    #             small_course=(course.id,course.course_name)
    #             self.course_list.append(small_course)

    #     except:
    #         course_list = []
    #     return self.course_list



    
    gender_choice=(
        ("Male","Male"),
        ("Female","Female"),
        ("Other","Other")
    )

    course=forms.ChoiceField(label="Course",widget=forms.Select(attrs={"class":"form-control"}))
    # course = forms.ChoiceField()
    gender=forms.ChoiceField(label="Gender",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    father_name=forms.CharField(label="Father name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    mother_name=forms.CharField(label="Mother name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    date_of_birth=forms.DateField(label="date_of_birth",widget=DateInput(attrs={"class":"form-control"}))
    religion=forms.CharField(label="Religion",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    cast=forms.CharField(label="Cast",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    category=forms.CharField(label="Category",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    admission_type=forms.CharField(label="Admission type",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    admission_status=forms.CharField(label="admission status",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    permanent_address=forms.CharField(label="permanent address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    communication_address=forms.CharField(label="communication address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    session_year=forms.ChoiceField(label="Session Year",widget=forms.Select(attrs={"class":"form-control"}))
    mobile=forms.CharField(label="mobile",max_length=20,widget=forms.NumberInput(attrs={"class":"form-control"}))
    qualification=forms.CharField(label="qualification",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    

class EditStudentForm(forms.Form):
    email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name=forms.CharField(label="First Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name=forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    username=forms.CharField(label="Username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}),required=False)


    course_list=[]
    try:
        courses = Courses.objects.all()
        for course in courses:
            small_course=(course.id,course.course_name)
            course_list.append(small_course)
    except:
        course_list=[]

    session_list = []
    try:
        sessions = SessionYearModel.object.all()

        for ses in sessions:
            small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
            session_list.append(small_ses)
    except:
        session_list = []
    gender_choice=(
        ("Male","Male"),
        ("Female","Female"),
        ("Other","Other")
    )

    course=forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={"class":"form-control"}))
    gender=forms.ChoiceField(label="Sex",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    father_name=forms.CharField(label="Father name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    mother_name=forms.CharField(label="Mother name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    date_of_birth=forms.DateField(label="date_of_birth",widget=DateInput(attrs={"class":"form-control"}))
    religion=forms.CharField(label="Religion",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    cast=forms.CharField(label="Cast",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    category=forms.CharField(label="Category",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    admission_type=forms.CharField(label="Admission type",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    admission_status=forms.CharField(label="admission status",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    permanent_address=forms.CharField(label="permanent address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    communication_address=forms.CharField(label="communication address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    session_year=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    mobile=forms.CharField(label="mobile",max_length=50,widget=forms.NumberInput(attrs={"class":"form-control"}))
    qualification=forms.CharField(label="qualification",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))

class AddCourseForm(forms.Form):
    course_name=forms.CharField(label="Course",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
    
  
