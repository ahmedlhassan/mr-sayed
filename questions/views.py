from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import MrQuestion
from django.urls import reverse_lazy
from home.permissions import StudentPermission, AuthenticatedPermission
from django.shortcuts import redirect
import os
import json
import boto3
from datetime import datetime


class QuestionListView (StudentPermission, ListView):
    template_name = "questions/student-questions.html"

    def get_queryset(self):
        return MrQuestion.objects.filter(user=self.request.user)
    def get_context_data(self, **kwargs):
        context = super(QuestionListView, self).get_context_data(**kwargs)
        context["student"] = True
        return context

class SelectedQuestionListView(AuthenticatedPermission, ListView):
    template_name = "questions/student-questions.html"

    def get_queryset(self):
        return MrQuestion.objects.filter(display_to_all=True)

class QuestionDetailView(AuthenticatedPermission, DetailView):
    model = MrQuestion
    template_name = 'questions/question-detail.html'


class QuestionCreateView(StudentPermission, CreateView):
    model = MrQuestion
    template_name = 'questions/question-new.html'
    fields = ('question', 'image_question',)
    success_url = reverse_lazy('student_questions')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def upload_to_s3(request):
    S3_BUCKET = 'mr-sayedabdelhamed2'
    file_name = request.GET.get('file_name')
    file_type = request.GET.get('file_type')
    question = request.GET.get('question')
    if not question:
        question = "سؤال بصورة"
    file_only_name, file_extension = os.path.splitext(file_name)
    if len(file_only_name) > 50:
        file_only_name = file_only_name[:50] + "..."
    now = datetime.now().timestamp()
    # username = request.user.username
    # if len(username) > 50:
    #     username = username[:50] + "..."
    image_name = "images/questions/" + file_only_name + "_" + str(now) + str(file_extension)

    if file_name:
        s3 = boto3.client('s3')
        presigned_post = s3.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key="static/" + image_name,
            Fields={"acl": "public-read", "Content-Type": file_type},
            Conditions=[
                {"acl": "public-read"},
                {"Content-Type": file_type}
            ],
            ExpiresIn=3600
        )
        data = {
            'data': presigned_post,
            'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
        }
        # MrQuestion.objects.create(
        #     question=question, user=request.user, image_question=image_name)
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        MrQuestion.objects.create(
            question=question, user=request.user)
        return redirect('student_questions')

def mr_question_image_success_upload(request):
    image_name = request.GET.get('image_name')[7:]
    question = request.GET.get('question')
    if not question:
        question = "سؤال بصورة"
    MrQuestion.objects.create(
        question=question, user=request.user, image_question=image_name)
    return HttpResponse(status=201)
