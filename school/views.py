from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower
from django.utils import timezone
from django.db.models import Count, Q
from openpyxl import Workbook # type: ignore


# # npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/output.css --watch                                                                  
from .models import (
    CustomUser, Exam, Result, Student, Parent, SchoolClass, Teacher, 
    Subject, Department, Attendance, Notice
)

# Create your views here.
def index_view(request):
    return render(request, 'school/index.html')

def student_dashboard_view(request):
    return HttpResponse('Student Dashboard')

def parent_dashboard_view(request):
    return HttpResponse('Parent Dashboard')

def sign_up_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        password = request.POST['password']
    
        user = CustomUser.objects.create_user(
            username = username,
            email = email,
            first_name = first_name,
            last_name = last_name,
            role = 'Admin',
            is_admin = True
        )


        user.set_password(password)
        user.save()
        messages.success(request, 'Account created successfully!')
        login(request, user)
        
    return render(request, 'school/signup.html')
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            
            if user.is_student:
                return redirect('student-dashboard')
            elif user.is_teacher:
                return redirect(reverse('teacher-dashboard', args=[user.id]))
            elif user.is_admin:
                return redirect('admin-dashboard')
            elif user.is_parent:
                return redirect('parent-dashboard')
            else:
                messages.error(request, 'Invalid role')
                return redirect('signup')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'school/login.html')
    
            
def logout_view(request):
    logout(request)
    return redirect('login')

def change_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email)
            if user:
                subject = "Password Reset Request"
                
        old_password = request.POST['old-password']
        new_password1 = request.POST['new-password1']
        new_password2 = request.POST['new-password2']
        check_old_password = CustomUser.check_password(old_password)
        if check_old_password and new_password1 == new_password2:
                CustomUser.set_password(new_password2)


    return render(request, 'school/change-password.html')

def student_list_view(request):

    students_classes = SchoolClass.objects.all()
    # searcfilter  students by class
    class_query = request.GET.get('class')
    # search students by first name or lastname
    query = request.GET.get('q')
    if query:
        students = Student.objects.filter(
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
    elif class_query:
        students = Student.objects.filter(student_class_id=class_query)
    else:
        students = Student.objects.filter(user__is_active=True).order_by('user__first_name')

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'school/students.html', {
            'query': query,
            'page_obj': page_obj,
            'students_classes': students_classes,
            'class_query': class_query
        })

   

@login_required
def add_student_view(request):
    if request.user.role != 'Admin':
        return HttpResponseForbidden('You do not have permission')
    if request.method == 'POST':
        # student details
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        gender = request.POST['gender']
        date_of_birth = request.POST['date-of-birth']
        student_classid = request.POST['student-class']
        student_class = SchoolClass.objects.get(id=student_classid)             
        religion = request.POST['religion']
        joining_date = request.POST['joining-date']
        admission_number = request.POST['admission-number']
        student_image = request.FILES.get('student-image')

        # parent details
        mother_name = request.POST['mother-name']
        father_name = request.POST['father-name']
        mother_mobile = request.POST['mother-mobile']
        father_mobile = request.POST['father-mobile']
        present_address = request.POST['present-address']
        permanent_address = request.POST['permanent-address']

        # create student user
        student_user = CustomUser.objects.create_user(
            username = username,
            email = email,
            first_name = first_name,
            last_name = last_name,
            role = 'Student',
            is_student = True
        )
        student_user.set_password(password)
        student_user.save()

        # create student model 
        student = Student.objects.create(
            user = student_user,
            gender = gender,
            date_of_birth = date_of_birth,
            student_class = student_class,
            religion = religion,
            joining_date = joining_date,
            admission_number = admission_number,
            student_image = student_image,
        )
        
         # Create parent model (father details)
        father = Parent.objects.create(
            name = father_name,
            mobile = father_mobile,
            relationship_with_student = 'Father',
            present_address = present_address,
            permanent_address = permanent_address,
            student = student
        ) 

        # Create parent model (mother details)
        mother = Parent.objects.create(
            name = mother_name,
            mobile = mother_mobile,
            relationship_with_student = 'Mother',
            present_address = present_address,
            permanent_address = permanent_address,
            student = student
        )

        messages.success(request, 'Student created successfully!')
        return redirect('student-list')
    return render(request, 'school/student-add.html', {'schoolclasses': SchoolClass.objects.all()})

@login_required
def edit_student_view(request, id):
    user = get_object_or_404(CustomUser, id=id)
    student_to_edit = get_object_or_404(Student, user=user)
    students_mother = get_object_or_404(Parent, student=student_to_edit, relationship_with_student='Mother')
    students_father = get_object_or_404(Parent, student=student_to_edit, relationship_with_student='Father')
    birthdate_formatted = student_to_edit.date_of_birth.strftime('%Y-%m-%d')
    joiningdate_formatted = student_to_edit.joining_date.strftime('%Y-%m-%d')
    
    if request.user.role != 'Admin':
        return HttpResponseForbidden('You do not have permission')
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        gender = request.POST['gender']
        date_of_birth = request.POST['date-of-birth']
        student_classid = request.POST['student-class']
        student_class = SchoolClass.objects.get(id=student_classid)             
        religion = request.POST['religion']
        joining_date = request.POST['joining-date']
        # admission_number = request.POST['admission-number']
        student_image = request.FILES.get('student-image')

        
        # user.username = username
        user.email = email
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        student_to_edit.gender = gender
        student_to_edit.date_of_birth = date_of_birth
        student_to_edit.student_class = student_class
        student_to_edit.religion = religion
        student_to_edit.joining_date = joining_date
        # student_to_edit.admission_number = admission_number
        student_to_edit.student_image = student_image
        student_to_edit.save()

        students_mother.mother_name = request.POST['mother-name']
        students_father.father_name = request.POST['father-name']
        students_mother.mother_mobile = request.POST['mother-mobile']
        students_father.father_mobile = request.POST['father-mobile']
        students_mother.present_address = request.POST['present-address']
        students_mother.permanent_address = request.POST['permanent-address']
        students_father.present_address = request.POST['present-address']
        students_father.permanent_address = request.POST['permanent-address']
        students_mother.save()
        students_father.save()

        return render(request, 'school/students.html')
    return render(request, 'school/student-edit.html', {
        'user': user,
        'student_to_edit': student_to_edit,
        'students_mother': students_mother,
        'students_father': students_father,
        'birthdate_formatted': birthdate_formatted,
        'joiningdate_formatted': joiningdate_formatted,
        'schoolclasses': SchoolClass.objects.all()
    })

def get_students_details_view(request, id):
    user = get_object_or_404(CustomUser, id=id)
    student = get_object_or_404(Student, user=user)
    latest_announcements = Notice.objects.exclude(target_audience='Staff').order_by('-created_at')[:5]

    students_dad = Parent.objects.get(student=student, relationship_with_student='Father')
    students_mum = Parent.objects.get(student=student, relationship_with_student='Mother')
    students_results = Result.objects.filter(student=student)

    # student exam score
    cat_1 =  Result.objects.filter(student=student, exam__name='CAT 1')
    cat_2 =  Result.objects.filter(Q(student=student) and Q(exam__name='CAT 2'))
    end_term_exam =  Result.objects.filter(Q(student=student) and Q(exam__name='End Term'))

    total_score_cat1 = 0
    total_score_cat2 = 0
    total_score_endterm = 0

    for exam in cat_1:
        total_score_cat1 += exam.score

    for exam in cat_2:
        total_score_cat2 += exam.score

    for exam in end_term_exam:
        total_score_endterm += exam.score


    students_subjects = Subject.objects.filter(class_assigned=student.student_class)

    present_days = Attendance.objects.filter(student=student, status='Present').count()
    absent_days = Attendance.objects.filter(student=student, status='Absent').count()
    late_days = Attendance.objects.filter(student=student, status='Late').count()
   
    return render(request, 'school/student-details.html', context={
            'student': student,
            'students_dad': students_dad,
            'students_mum': students_mum,
            'students_subjects': students_subjects,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'latest_announcements': latest_announcements,
            'students_results': students_results,
            'cat1_results': cat_1,
            'cat2_results': cat_2,
            'endterm_results': end_term_exam,
            'total_score_cat1': total_score_cat1,
            'total_score_cat2': total_score_cat2,
            'total_score_endterm': total_score_endterm
        })

def delete_student_view(request, id):
    user = get_object_or_404(CustomUser, id=id)
    if request.user.is_admin:
        user.is_active = False
        user.save()
    
    return redirect('student-list')

def admin_dashboard_view(request):
    students_count =Student.objects.filter(user__is_active=True).count()
    teachers_count = Teacher.objects.filter(user__is_active=True).count()
    subjects_count = Subject.objects.annotate(lower_name = Lower('name')).values_list('lower_name', flat=True).distinct().count()
    active_departments = Department.objects.filter(is_active=True)
    departments_count = active_departments.count()
    school_classes = SchoolClass.objects.all()
    school_classes_count = school_classes.count()
    # total students per class
    all_classes = SchoolClass.objects.annotate(total_students=Count('student'))
    

    recent_students = Student.objects.order_by('-created_at')[:2]
    recent_subjects = Subject.objects.order_by('-created_at')[:2]
    recent_classes = SchoolClass.objects.order_by('-created_at')[:2]
    recent_departments = Department.objects.order_by('-created_at')[:2]
    latest_announcements = Notice.objects.order_by('-created_at')[:5]

    recent_activities = []
    for student in recent_students:
        recent_activities.append({
            'type': 'New Student Registered',
            'name': student.user.first_name,
            'timestamp': student.created_at
        })
        print("Student creation time: ", student.created_at.month)

    for schoolclass in recent_classes:
        recent_activities.append({
            'type': 'New Class added',
            'name': f"{schoolclass.name} {schoolclass.get_stream_display()}",
            'timestamp': schoolclass.created_at
        })

    for subject in recent_subjects:
        recent_activities.append({
            'type': 'New Subject added',
            'name': f"{subject.name} - {subject.class_assigned.name} {subject.class_assigned.get_stream_display()}",
            'timestamp': subject.created_at
        })

    for department in recent_departments:
        recent_activities.append({
            'type': 'New Department created',
            'name': department.name,
            'timestamp': department.created_at
        })

    recent_activities = sorted(recent_activities, key=lambda x : x['timestamp'], reverse=True)

    # charts data
    # Group teachers per department
    teachers_count_per_department  = []
    labels = []
    for dept in active_departments:
        labels.append(dept.code)
        count = Teacher.objects.filter(teachers_department = dept).count()
        teachers_count_per_department.append(count)
    
    # Number of students per class chart
    students_count_per_class = []
    mylabels = []
    for sc in all_classes:
        mylabels.append(f"{sc.name}-{sc.get_stream_display()}")
        print(sc.name, sc.total_students)
        students_count_per_class.append(sc.total_students)

    # Attendance chart per class
    attendance_data_chart = []
    for classroom in school_classes:
        students = Student.objects.filter(student_class=classroom)
        present_days = Attendance.objects.filter(student__in=students, status='Present').count()
        absent_days = Attendance.objects.filter(student__in=students, status='Absent').count()
        late_days = Attendance.objects.filter(student__in=students, status='Late').count()

        attendance_data_chart.append({
            'class': f"{classroom.name} {classroom.get_stream_display()}",
            'present': present_days,
            'absent': absent_days,
            'late': late_days
        })

    # pie chart showing one class attendance at a time
    selected_class_id = request.GET.get('classroom')
    class_selected = False
    attendance_per_classroom = None

    if selected_class_id:
        class_selected = True
        selected_class_name = SchoolClass.objects.get(id=selected_class_id).name
        selected_class_stream = SchoolClass.objects.get(id=selected_class_id).get_stream_display()
        # if selected_class_id:
        classroom_students = Student.objects.filter(student_class_id=selected_class_id)
        present_days_count = Attendance.objects.filter(student__in=classroom_students, status='Present').count()
        absent_days_count = Attendance.objects.filter(student__in=classroom_students, status='Absent').count()
        late_days_count = Attendance.objects.filter(student__in=classroom_students, status='Late').count()

        attendance_per_classroom = {
            'present_count': present_days_count,
            'absent_count': absent_days_count,
            'late_count': late_days_count
        }
    else:
        selected_class_name = None
        selected_class_stream = None
   

    
    return render(request, 'school/admin-dashboard.html', {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'subjects_count': subjects_count,
        'departments_count': departments_count,
        'school_classes_count': school_classes_count,
        'recent_activities': recent_activities,
        'active_departments': active_departments,
        'teachers_count_per_department': teachers_count_per_department,
        'labels': labels,
        'students_count_per_class': students_count_per_class,
        'mylabels': mylabels,
        'students': students,
        'school_classes': school_classes,
        'attendance_data_chart': attendance_data_chart,
        'selected_class_id': selected_class_id,
        'attendance_per_classroom': attendance_per_classroom,
        'selected_class_name': f"{selected_class_name} {selected_class_stream}",
        'class_selected': class_selected,
        'latest_announcements': latest_announcements
    })

def create_teacher_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        gender = request.POST['gender']
        title = request.POST['usertitle']
        teacher_image = request.FILES.get('teacher-image')
        subject_ids = request.POST.getlist('subjects')


        user = CustomUser.objects.create_user(
            username = username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password,
            role = 'Teacher',
            is_teacher = True
        )

        teacher = Teacher.objects.create(
            user = user,
            gender = gender,
            title = title,
            teacher_image = teacher_image
        )

        Subject.objects.filter(id__in=subject_ids, teacher__isnull=True).update(teacher=teacher)
        return redirect('teacher-dashboard')
    else:
        available_subjects = Subject.objects.filter(teacher__isnull=True)
        print("Available subjects: ", available_subjects)
    return render(request, 'school/teacher-add.html', context={'available_subjects': available_subjects})

def teachers_list_view(request):
    teachers = Teacher.objects.all()
    paginator = Paginator(teachers, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'school/teachers-list.html', {'page_obj': page_obj})

def teacher_dashboard_view(request, id):
    user = get_object_or_404(CustomUser, id=id)
    teacher = get_object_or_404(Teacher, user=user)
    latest_announcements = Notice.objects.exclude(target_audience='Students').order_by('-created_at')[:5]

    # this teachers classes
    teachers_classes = Subject.objects.filter(teacher=teacher)
    classes_count = teachers_classes.count()
    return render(request, 'school/teacher-dashboard.html', 
                {
                    'teacher': teacher, 
                    'teachers_classes': teachers_classes,
                    'classes_count': classes_count,
                    'classes_count': classes_count,
                    'latest_announcements': latest_announcements 
                    # 'is_class_teacher_of': is_class_teacher_of
                })

def edit_teacher_view(request, id):

    user = get_object_or_404(CustomUser, id=id)
    teacher = get_object_or_404(Teacher, user=user)
    all_subjects = Subject.objects.all()

    if request.method == 'POST' and request.user == user:
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        gender = request.POST['gender']
        title = request.POST['usertitle']
        teacher_image = request.FILES.get('teacher-image')

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role = 'Teacher'
        user.is_teacher = True
        if password:
            user.set_password(password)
        user.save()
        

        # teacher.user = user
        teacher.gender = gender
        teacher.title = title
        teacher.teacher_image = teacher_image
        teacher.save()  
        
        subject_ids = request.POST.getlist('subjects')
        Subject.objects.filter(teacher=teacher).exclude(id__in=subject_ids).update(teacher=None)
        Subject.objects.filter(id__in=subject_ids).update(teacher=teacher)

        return redirect(reverse('teacher-dashboard', args=[id]))
    assigned_ids = teacher.subjects.values_list('id', flat=True)
    
    return render(request, 'school/teacher-edit.html', 
                {
                    'teacher': teacher,
                    'all_subjects': all_subjects,
                    'assigned_ids': assigned_ids
                })

def delete_teacher_view(request, id):
    user = get_object_or_404(CustomUser, id=id)
    if request.user.is_admin:
        user.is_active == False
        user.save()

@login_required
def create_department_view(request):
    teachers = Teacher.objects.all()

    if request.user.role != 'Admin':
        return HttpResponseForbidden('You do not have permission')
    if request.method == 'POST':
        name = request.POST['name']
        code = request.POST['code']
        description = request.POST['description']
        head_id = request.POST['dept-head']

        # department = Department( name=name, code=code, description=description)
       
        head = Teacher.objects.get(id=head_id)
        # department.head = head
        department = Department.objects.create( 
            name = name, 
            code = code, 
            description = description,
            head = head
        )
       
    return render(request, 'school/create-department.html', { 'teachers': teachers })

def departments_list_view(request):
    departments = Department.objects.all()
    paginator = Paginator(departments, 6)
    page_number  = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)
    return render(request, 'school/departments.html', {'page_obj': page_obj})

def department_details_view(request, code):
    department = get_object_or_404(Department, code=code)
    department_teachers = Teacher.objects.filter(teachers_department=department)
    teachers_count = department_teachers.count()
    return render(request, 'school/department-details.html', {
            'department': department,
            'department_teachers': department_teachers,
            'teachers_count': teachers_count
        })

@login_required
def delete_department_view(request, code):
    department = get_object_or_404(Department, code=code)
    if request.user.role != 'Admin':
        return HttpResponseForbidden("You dont have permission")
    department.is_active = False
    department.save()

@login_required
def edit_department_view(request, id):
    department = get_object_or_404(Department, id=id)
    teachers = Teacher.objects.filter(teachers_department = department)
    if request.user.role != 'Admin':
        return HttpResponseForbidden('You do not have permissions')
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')
        head_id = request.POST['dept-head']

        head = Teacher.objects.get(id=head_id)

        department.name = name
        department.code = code
        department.description = description
        department.head = head

        department.save()
    return render(request, 'school/department-edit.html', {
            'department': department,
            'teachers': teachers
        })

def subjects_list_view(request):
    subjects = Subject.objects.filter(is_active=True).order_by('id')
    paginator = Paginator(subjects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'school/subjects.html', {'page_obj': page_obj})

@login_required
def create_subject_view(request):
    teachers = Teacher.objects.all()
    schoolclasses = SchoolClass.objects.all()
    departments = Department.objects.all()

    if request.user.role != 'Admin':
        return HttpResponseForbidden('You do not have permissions')
    if request.method == 'POST':
        name = request.POST['name']
        classassigned_id = request.POST['classassigned']
        classassigned = SchoolClass.objects.get(id=classassigned_id)
        teacher_id = request.POST['teacher']
        teacher = Teacher.objects.get(id=teacher_id)
        subjects_department_id = request.POST['department']
        subjects_department = Department.objects.get(id=subjects_department_id)

        Subject.objects.create(
            name = name,
            class_assigned = classassigned,
            teacher = teacher,
            subjects_department = subjects_department
        )
        return redirect('subjects')
    return render(request, 'school/subject-create.html', {
        'teachers': teachers,
        'schoolclasses': schoolclasses,
        'departments': departments
    })

def edit_subject_view(request, id):
    subject = get_object_or_404(Subject, id=id)
    teachers = Teacher.objects.all()
    departments = Department.objects.all()
    schoolclasses = SchoolClass.objects.all()

    if request.user.role != 'Admin':
        return HttpResponseForbidden('You do not have permissions')
    if request.method == 'POST':
        name = request.POST.get('name')
        classassigned_id = request.POST.get('classassigned')
        classassigned = SchoolClass.objects.get(id=classassigned_id)
        teacher_id = request.POST.get('teacher')
        teacher = Teacher.objects.get(id=teacher_id)
        subjects_department_id = request.POST.get('department')
        subjects_department = Department.objects.get(id=subjects_department_id)

        subject.name = name
        subject.class_assigned = classassigned
        subject.teacher = teacher
        subject.subjects_department = subjects_department
        subject.save()

        return redirect('subjects')
    return render(request, 'school/subject-edit.html', { 
            'subject': subject,
            'teachers': teachers,
            'departments': departments,
            'schoolclasses': schoolclasses
        })

def delete_subject_view(request, id):
    subject = get_object_or_404(Subject, id=id)

    if request.user.role != 'Admin':
        return HttpResponseForbidden("You do not have permissions")
    subject.is_active = False
    subject.save()

    print("Deleted")

def exams_list_view(request):
    exams = Exam.objects.filter(is_active=True)
    paginator = Paginator(exams, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'school/exams.html', {'page_obj': page_obj})


def create_exam_view(request):
    school_classes = SchoolClass.objects.all()
    current_class = request.GET.get('class')
    subjects = None
    # subjects = Subject.objects.filter(class_assigned__name = current_class)
    # subjects = Subject.objects.annotate(lower_name = Lower('name')).distinct().filter(class_assigned__name = current_class)
    if current_class:
        selected_class_name, stream = current_class.split('|')
        subjects = Subject.objects.annotate(
            lower_name = Lower('name')).values_list('id', 'lower_name').filter(
            Q(class_assigned__name = selected_class_name) and Q(class_assigned__stream=stream)).distinct()
    

    if request.user.role != 'Admin':
        return HttpResponseForbidden("You do not have permissions")
    
    if request.method == 'POST':
        name = request.POST['name']
        subject_id = request.POST['subject']
        subject = Subject.objects.get(id=subject_id)

        print("current subject id", subject)
        exam_date = request.POST['exam-date']

        Exam.objects.create(
            name = name,
            subject = subject,
            exam_date = exam_date
        )

        return redirect('exams')
    return render(request, 'school/exam-create.html', {
            'subjects': subjects,
            'school_classes': school_classes
        })

def edit_exam_view(request, id):
    exam = get_object_or_404(Exam, id=id)
    subjects = Subject.objects.all()

    if request.user.role != 'Admin':
        return HttpResponseForbidden("You do not have permissions")
    if request.method == 'POST':
        name = request.POST.get('name')
        subject_id = request.POST.get('subject')
        subject = Subject.objects.get(id=subject_id)
        exam_date = request.POST.get('exam-date')

        
        exam.name = name,
        exam.subject = subject,
        exam.exam_date = exam_date
        exam.save()

        return redirect('exams')
    return render(request, 'school/exam-create.html', {'exam': exam, 'subjects': subjects })

def delete_exam_view(request, id):
    exam = get_object_or_404(Exam, id=id)

    if request.user.role != 'Admin':
        return HttpResponseForbidden("You do not have permissions")
    
    exam.is_active = False
    exam.save()
    return redirect('exams')

def attendance_success(request):
    return render(request, 'school/attendance-success.html')

def mark_attendance_view(request):
    if request.user.role != 'Teacher':
        return HttpResponseForbidden('You do not have permissions')
    
    teacher = Teacher.objects.get(user=request.user)
    try:
        classroom = SchoolClass.objects.get(class_teacher=teacher)
    except SchoolClass.DoesNotExist:
        classroom = None
    if not classroom:
        return render(request, 'school/error.html', {
            'message': 'You are not assigned as a class teacher yet'
        })
    
    students = Student.objects.filter(student_class=classroom)
    paginator = Paginator(students, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f"status_{student.user.id}")
            if status:
                Attendance.objects.update_or_create(
                    student = student,
                    date = timezone.now().date(),
                    defaults = {'status': status}
                )
        return redirect('attendance-success')
    return render(request, 'school/mark-attendance.html', {
            'page_obj': page_obj,
            'classroom': classroom
        })

def download_students_excel_view(request):
    # pip install openpyxl
    students = Student.objects.filter(user__is_active=True).order_by('user__first_name')

    class_query = request.GET.get('class')
    # search students by first name or lastname
    query = request.GET.get('q')
    filename_parts = ["students"]
    if query:
        students = Student.objects.filter(
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        )
        filename_parts.append(query)


    elif class_query:
        students = Student.objects.filter(student_class_id=class_query)
        selected_class = SchoolClass.objects.get(id=class_query)

        filename_parts.append(f"{selected_class.name}_{selected_class.get_stream_display()}")
    
    workbook = Workbook()
    sheet = workbook.active

    sheet.title= 'students'
                
    sheet.append(['NAME', 'ADM NO.', 'CLASS', 'STREAM', 'GENDER'])

    for student in students:
        name = f"{student.user.first_name} {student.user.last_name}"
        sheet.append([name, student.admission_number, student.student_class.name, student.student_class.get_stream_display(), student.get_gender_display()])

    filename = "_".join(filename_parts) + ".xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response

def create_announcemennt_view(request):
    if request.user.role != 'Admin':
        return HttpResponseForbidden('You do not have permissions to perform this action')
    if request.method == 'POST':
        title = request.POST['title']
        message = request.POST['message']
        posted_by = request.user
        target_audience = request.POST['target-audience']

        Notice.objects.create(
            title = title,
            message = message,
            posted_by = posted_by,
            target_audience = target_audience
        )
        return redirect('admin-dashboard')
    return render(request, 'school/announcement-create.html')

def announcements_list_view(request):
    announcements = Notice.objects.filter(is_active=True).order_by('-created_at')
    admin_users = CustomUser.objects.filter(role='Admin')

    creator_query = request.GET.get('creator')
    title_query = request.GET.get('title')

    if title_query:
        announcements = Notice.objects.filter(Q(title__icontains=title_query))
    
    if creator_query:
        announcements = Notice.objects.filter(posted_by__username=creator_query)

    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'school/announcements.html',
        {
            'page_obj': page_obj,
            'admin_users': admin_users
        })

def edit_announcemnt_view(request, id):
    if request.user.role != 'Admin':
        return HttpResponseForbidden("You do not have permissions to perform this action")
    announcement = get_object_or_404(Notice, id=id)
    if request.user == announcement.posted_by:
        if request.method == 'POST':
            title = request.POST.get('title')
            message = request.POST.get('message')
            target_audience = request.POST.get('target-audience')

            announcement.title = title
            announcement.message = message
            announcement.target_audience = target_audience
            announcement.updated_at = timezone.now()

            announcement.save()
            return redirect('announcements')
    return render(request, 'school/announcement-edit.html', {
       'announcement': announcement
    })


def delete_announcement_view(request, id):
    if request.user.role != 'Admin':
        return HttpResponseForbidden("You do not have permissions to perform this action")
    announcement = get_object_or_404(Notice, id=id)
    if request.user == announcement.posted_by:
        announcement.is_active = False
        announcement.save()
        return redirect('announcements')
    return


def download_notices_excel_view(request):
    # pip install openpyxl
    announcements = Notice.objects.filter(is_active=True).order_by('-created_at')

    title_query = request.GET.get('title')
    # search students by first name or lastname
    creator_query = request.GET.get('creator')

    filename_parts = ["Announcements"]

    if title_query:
        announcements = Notice.objects.filter(Q(title__icontains=title_query))
        filename_parts.append(title_query)

    
    if creator_query:
        announcements = Notice.objects.filter(posted_by__username=creator_query)
        filename_parts.append(creator_query)

    
    workbook = Workbook()
    sheet = workbook.active

    sheet.title= 'Announcements'
                
    sheet.append(['Title', 'Message'])

    for notice in announcements:
        sheet.append([notice.title, notice.message])

    filename = "_".join(filename_parts) + ".xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response


def add_students_results_view(request, id):
    student = get_object_or_404(Student, user_id=id)
    exams = Exam.objects.filter(subject__class_assigned = student.student_class, result__score__isnull=True)

    if request.user.role != 'Admin':
        return HttpResponseForbidden("You do not have permissisons")
    if request.method == 'POST':
        exam_id = request.POST['exam']
        exam = Exam.objects.get(id=exam_id)
        score = request.POST['score']

        Result.objects.create(
            student = student,
            exam = exam,
            score = score
        )
        return redirect('student-details', student.user.id)
    return render(request, 'school/add-results.html', { 
        'student': student,
        'exams': exams,
    })

def settings_page_view(request):
    return render(request, 'school/settings.html')