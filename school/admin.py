from django.contrib import admin
from .models import (
    CustomUser, SchoolClass, Subject, Student, Parent,
    Teacher, Exam, Result, Attendance, Department, Notice, ExamTimetable
)

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user__id', 'user__first_name', 'admission_number')

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    
class ResultAdmin(admin.ModelAdmin):
    list_display = ( 'student', 'exam', 'score')    

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SchoolClass)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Parent)
admin.site.register(Teacher)
admin.site.register(Exam)
admin.site.register(Attendance)
admin.site.register(Result, ResultAdmin)
admin.site.register(Department)
admin.site.register(Notice)
admin.site.register(ExamTimetable)
