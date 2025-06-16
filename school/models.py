from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# Create your models here.
class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_authorized = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=(
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
        ('Admin', 'Admin'),
        ('Parent', 'Parent')

    ))
    user_photo = models.ImageField(upload_to='users/', default='../static/images/defaultavatar.jpg')

    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name = 'customuser_set',
        blank = True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank = True
    )

    def __str__(self):
        return self.email
    
    
class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=(
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others')
    ))
    title = models.CharField(max_length=10, choices=(
        ('Miss', 'Miss'),
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs')
    ))
    teacher_image = models.ImageField(upload_to='teacher/', blank=True, default='')
    teachers_department = models.ForeignKey('Department', null=True, blank=True, on_delete=models.SET_NULL, related_name='teachers')

    def __str__(self):
        return self.user.username
    
class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    stream = models.CharField(max_length=10, choices=(
        ('Blue', 'Blue'),
        ('Red', 'Red'),
        ('Yellow', 'Yellow'),
        ('Green', 'Green'),

    ))
    class_teacher = models.OneToOneField(Teacher, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'School Classes'

    def __str__(self):
        return f"{self.name} {self.stream}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    class_assigned = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, null=True, on_delete=models.SET_NULL, blank=True, related_name='subjects')
    subjects_department = models.ForeignKey('Department', null=True, blank=True, on_delete=models.SET_NULL, related_name='subjects')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class Exam(models.Model):
    name = models.CharField(max_length=100, choices=(
        ('CAT 1', 'CAT 1'),
        ('CAT 2', 'CAT 2'),
        ('End Term', 'End Term')
    ))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class ExamTimetable(models.Model):
    title = models.CharField(max_length=200)
    class_assigned = models.ManyToManyField(SchoolClass)
    timetable_pdf = models.FileField(upload_to='timetables/')
    is_active = models.BooleanField(default=True)

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others')
    ])
    date_of_birth = models.DateField()
    student_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    religion = models.CharField(max_length=20)
    joining_date = models.DateField()
    admission_number = models.CharField(max_length=15, unique=True)
    student_image = models.ImageField(upload_to='student/', blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.first_name}-{self.user.last_name}-{self.student_id}")
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name}  {self.user.last_name} ({self.admission_number})"
    
class Parent(models.Model):
    name = models.CharField(max_length=100, blank=True)
    relationship_with_student = models.CharField(max_length=20, choices=(
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian'),
    ))
    mobile = models.CharField(max_length=10)
    present_address = models.TextField()
    permanent_address = models.TextField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=((
        'Present', 'Present'),
        ('Absent', 'Absent'), 
        ('Late', 'Late')
    ))

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField()

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    head = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def clean(self):
        if self.head and self.head.teachers_department != self:
            raise ValidationError("The department head must be a member in this department")
    
    def __str__(self):
        return f"{self.name} Department"
    

class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    target_audience = models.CharField(
        max_length=100,
        choices = [
            ('Everyone', 'Everyone'),
            ('Students', 'Students'),
            ('Staff', 'Staff')
        ],
        default='Everyone'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

