from django.shortcuts import render
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = 'login.html'


class IndexView(TemplateView):
    template_name = 'index.html'


class StudentDashboardView(TemplateView):
    template_name = 'student_dashboard.html'


class ExamView(TemplateView):
    template_name = 'exam.html'


class ResultsView(TemplateView):
    template_name = 'results.html'


class AdminDashboardView(TemplateView):
    template_name = 'admin_dashboard.html'


class UserManagementView(TemplateView):
    template_name = 'user_management.html'


class QuestionBankView(TemplateView):
    template_name = 'question_bank.html'


class CreateQuizView(TemplateView):
    template_name = 'create_quiz.html'


class ImportExcelView(TemplateView):
    template_name = 'import_excel.html'
