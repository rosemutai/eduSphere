from django.urls import path
from django.contrib.auth import views as auth_views
from school import views

urlpatterns = [
    path('index', views.index_view, name='index'),
    path('signup', views.sign_up_view, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('password-change', auth_views.PasswordChangeView.as_view(
        template_name='registration/password-change.html'), name='password-change'),
    path('password-change/done', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password-change-complete.html'), name='password-change-complete'),
    path('password-reset', auth_views.PasswordResetView.as_view(
        template_name='registration/password-reset.html'), name='password-reset'),
    path('password_reset_done', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password-reset-done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password-reset-confirm.html'), name='password-reset-confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password-reset-complete.html'), name='password-reset-complete'),

    path('parent-dashboard', views.parent_dashboard_view, name='parent-dashboard'),
    path('student-dashboard', views.student_dashboard_view, name='student-dashboard'),
    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),
    path('students', views.student_list_view, name='student-list'),
    path('add-student', views.add_student_view, name='add-student'),
    path('edit-student/<int:id>', views.edit_student_view, name='edit-student'),
    path('student-details/<int:id>', views.get_students_details_view, name='student-details'),
    path('delete-student/<int:id>', views.delete_student_view, name='delete-student'),
    path('add-teacher', views.create_teacher_view, name='add-teacher'),
    path('teachers', views.teachers_list_view, name='teachers-list'),
    path('teacher-dashboard/<int:id>', views.teacher_dashboard_view, name='teacher-dashboard'),
    path('edit-teacher/<int:id>', views.edit_teacher_view, name='edit-teacher'),
    path('create-department', views.create_department_view, name='create-department'),
    path('departments', views.departments_list_view, name='departments'),
    path('department-detail/<str:code>', views.department_details_view, name='department-details'),
    path('edit-department/<int:id>', views.edit_department_view, name='edit-department'),
    path('subjects', views.subjects_list_view, name='subjects'),
    path('add-subject', views.create_subject_view, name='add-subject'),
    path('edit-subject/<int:id>', views.edit_subject_view, name='edit-subject'),
    path('delete-subject/<int:id>', views.delete_subject_view, name='delete-subject'),
    path('exams', views.exams_list_view, name='exams'),
    path('add-exam', views.create_exam_view, name='add-exam'),
    path('edit-exam/<int:id>', views.edit_exam_view, name='edit-exam'),
    path('delete-exam/<int:id>', views.delete_exam_view, name='delete-exam'),
    path('attendance-success', views.attendance_success, name='attendance-success'),
    path('mark-attendance', views.mark_attendance_view, name='mark-attendance'),
    path('download', views.download_students_excel_view, name='download'),
    path('create-announcement', views.create_announcemennt_view, name='create-announcement'),
    path('announcements', views.announcements_list_view, name='announcements'),
    path('announcements/<int:id>', views.edit_announcemnt_view, name='edit-announcement'),
    path('delete-announcement/<int:id>', views.delete_announcement_view, name='delete-announcement'),
    path('download-notices', views.download_notices_excel_view, name='download-notices'),
    path('add-results/<int:id>', views.add_students_results_view, name='add-results'),
    path('settings', views.settings_page_view, name='settings'),

]
