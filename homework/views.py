from home.permissions import StudentPermission
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import FormView, DeleteView
from .models import (Homework, StudentHomework,
                     StudentHomeworkFile, StudentHomeworkMakeup)
from collections import OrderedDict
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.shortcuts import redirect
from django.utils import timezone
from .forms import StudentHomeworkFileForm, StudentHomeworkMultipleFileForm
from datetime import datetime
from django.shortcuts import redirect
import os
import json
import boto3
import random
import uuid
from django.http import HttpResponse

image_extensions = ('.djvu', '.art', '.cpt', '.tif', '.jpe', '.rgb', '.svgz', '.nef', '.xbm', '.jpeg', '.jpm', '.erf', '.cdt', '.bmp', '.pgm', '.ico', '.xpm', '.jpx', '.pcx', '.ief',
                    '.svg', '.jp2', '.pbm', '.djv', '.cr2', '.png', '.xwd', '.ppm', '.jng', '.jpg2', '.orf', '.cdr', '.gif', '.psd', '.ras', '.pnm', '.crw', '.wbmp', '.pat', '.tiff', '.jpf', '.jpg')


class HomeworkListView(StudentPermission, ListView):
    model = Homework
    template_name = "homework/homework-list.html"
    now = datetime.now()

    def get_queryset(self):
        queryset = Homework.objects.none()

        # Makeup homeworks
        mackup_homeworks = StudentHomeworkMakeup.objects.filter(
            user=self.request.user)
        if mackup_homeworks:
            for makeup_homework in mackup_homeworks:
                queryset |= Homework.objects.filter(id=makeup_homework.homework.id)

        # Week homework
        queryset |= Homework.objects.filter(week__start__lte=self.now.date(), week__end__gte=self.now.date())
        return queryset

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        all_homeworks = []
        homeworks = self.get_queryset()
        for i in homeworks:
            answered = "not answered yet"
            if i.student_homework.filter(user=self.request.user):
                if i.student_homework.filter(user=self.request.user).last().student_homework_file.all():
                    answered = "answered"
            all_homeworks.append({"homework": i,
                                  "answered": answered})
        ctx["homeworks"] = all_homeworks
        if self.request.session.get('homework_is_checked'):
            ctx["homework_is_checked"] = True
            del self.request.session["homework_is_checked"]
        return ctx


class HomeworkMultipleUpdateView(FormView):
    template_name = 'homework/homework.html'
    form_class = StudentHomeworkMultipleFileForm
    success_url = reverse_lazy("homework_list")

    def form_invalid(self, form, error_message):
        ctx = self.get_context_data()
        ctx["error_message"] = error_message
        return self.render_to_response(ctx)

    def dispatch(self, request, *args, **kwargs):
        now = datetime.now()
        if self.request.user.student_is_active is False:
            return redirect('login')
        # Week Homework
        self.homework = Homework.objects.filter(id=self.kwargs.get("homework_pk"),
                                               week__start__lte=now.date(),
                                               week__end__gte=now.date()).last()
        # Makeup Homework
        if not self.homework:
            if self.kwargs.get("homework_pk") in StudentHomeworkMakeup.objects.filter(user=self.request.user).values_list("homework", flat=True):
                self.homework = Homework.objects.get(id=self.kwargs.get("homework_pk"))
             
        if not self.homework:
            return redirect("homework_list")
        self.student_homework, created = StudentHomework.objects.get_or_create(
            homework=self.homework, user=self.request.user)
        if self.student_homework.is_checked is True:
            self.request.session['homework_is_checked'] = True
            return redirect("homework_list")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('student_homework_file')

        if form.is_valid():
            files_length = len(files)
            uploaded_files_length = self.student_homework.student_homework_file.all().count()
            if files_length + uploaded_files_length < 1:
                return self.form_invalid(form, 'عدد الملفات لا يجب أن تقل عن 1')
            elif files_length + uploaded_files_length > 6:
                return self.form_invalid(form, 'عدد الملفات لا يجب أن تزيد عن 6')
            for f in files:
                StudentHomeworkFile.objects.create(
                    student_homework=self.student_homework, student_homework_file=f)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        homework = Homework.objects.get(id=self.kwargs.get("homework_pk"))
        homework_questions = homework.homework_file

        student_homework = StudentHomework.objects.filter(
            homework__id=self.kwargs.get("homework_pk"), user=self.request.user).last()

        ctx["homework_questions"] = homework_questions
        ctx["homework"] = homework
        ctx["image_extensions"] = image_extensions
        if student_homework:
            ctx["uploaded_files"] = student_homework.student_homework_file.all()

        return ctx


class UploadedFileDeleteView(StudentPermission, DeleteView):
    model = StudentHomeworkFile

    def get_object(self):
        return StudentHomeworkFile.objects.get(id=self.kwargs.get("file_pk"))

    def get_success_url(self):
        return reverse_lazy("homework", kwargs={"homework_pk": self.kwargs.get("homework_pk")})


def direct_upload_s3(request):

    lowercase_str = uuid.uuid4().hex
    S3_BUCKET = 'mr-sayedabdelhamed2'
    file_name = request.GET.get('file_name')
    file_type = request.GET.get('file_type')
    homework_id = request.GET.get('homework_id')

    file_only_name, file_extension = os.path.splitext(file_name)
    image_name = "images/homework/" + file_only_name + \
        request.user.username + "-" + lowercase_str[:6] + str(file_extension)

    # if file_name:
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
    return HttpResponse(json.dumps(data), content_type="application/json")


def homework_image_success_upload(request):
    image_name = request.GET.get('image_name')[7:]
    homework_id = request.GET.get('homework_id')

    homework = Homework.objects.get(id=int(homework_id))
    student_homework, created = StudentHomework.objects.get_or_create(
        homework=homework, user=request.user)
    StudentHomeworkFile.objects.create(
        student_homework=student_homework, student_homework_file=image_name)

    return HttpResponse(status=201)
