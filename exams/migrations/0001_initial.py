# Generated by Django 2.2.15 on 2020-10-04 03:28

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChoiceQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=300, null=True)),
                ('image_question', models.ImageField(blank=True, null=True, upload_to='')),
                ('option1', models.CharField(max_length=300)),
                ('option2', models.CharField(max_length=300)),
                ('option3', models.CharField(max_length=300)),
                ('option4', models.CharField(max_length=300)),
                ('right_answer_choice', models.IntegerField(choices=[(1, 'الاختيار الاول'), (2, 'الاختيار الثاني'), (3, 'الاختيار الثالث'), (4, 'الاختيار الرابع')])),
                ('grade', models.FloatField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EssayQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=300, null=True)),
                ('image_question', models.ImageField(blank=True, null=True, upload_to='')),
                ('grade', models.FloatField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('total_question', models.IntegerField(default=0)),
                ('grade', models.DecimalField(decimal_places=1, default=0, max_digits=10, verbose_name='الدرجة')),
                ('time', models.IntegerField(default=0, verbose_name='الوقت بالدقايق')),
                ('exam_type', models.IntegerField(choices=[(0, 'امتحان اختياري'), (1, 'امتحان اختياري و مقالي')], default=0)),
                ('answer', models.FileField(blank=True, null=True, upload_to='')),
                ('show_answer', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('been_a_week', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('week', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='classes.Week', verbose_name='الأسبوع')),
            ],
        ),
        migrations.CreateModel(
            name='StudentExam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('answered_questions', models.IntegerField(blank=True, default=0, null=True)),
                ('is_graded', models.BooleanField(default=False)),
                ('expiry_time', models.DateTimeField(blank=True, null=True)),
                ('questions', models.TextField(blank=True, null=True)),
                ('questions_json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_exam', to='exams.Exam')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrueFalseQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=300, null=True)),
                ('image_question', models.ImageField(blank=True, null=True, upload_to='')),
                ('grade', models.FloatField(max_length=100)),
                ('right_answer', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='true_false_question', to='exams.Exam')),
            ],
        ),
        migrations.CreateModel(
            name='StudentTrueFalseAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.BooleanField()),
                ('grade', models.FloatField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.EssayQuestion')),
                ('student_exam', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='exams.StudentExam')),
            ],
        ),
        migrations.CreateModel(
            name='StudentEssayAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(blank=True, max_length=100, null=True)),
                ('image_answer', models.ImageField(blank=True, null=True, upload_to='')),
                ('grade', models.FloatField(blank=True, max_length=100, null=True)),
                ('is_graded', models.BooleanField(default=False)),
                ('is_answered', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_essay_answer', to='exams.EssayQuestion')),
                ('student_exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_essay_answer', to='exams.StudentExam')),
            ],
        ),
        migrations.CreateModel(
            name='StudentChoiceAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(blank=True, max_length=100, null=True)),
                ('grade', models.FloatField(blank=True, default=0, max_length=100, null=True)),
                ('is_answered', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_choice_answer', to='exams.ChoiceQuestion')),
                ('student_exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_choice_answer', to='exams.StudentExam')),
            ],
        ),
        migrations.AddField(
            model_name='essayquestion',
            name='exam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='essay_question', to='exams.Exam'),
        ),
        migrations.AddField(
            model_name='choicequestion',
            name='exam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice_question', to='exams.Exam'),
        ),
    ]
