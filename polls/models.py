import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib import admin

# Create your models here.
class Question(models.Model):

    author = models.ForeignKey(User, on_delete= models.CASCADE , null= True, blank=True)
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days= 1) <= self.pub_date <= now

    def __str__(self):     # mandatory 
        return self.question_text
    

class Choice (models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField( max_length= 200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
    
# creating a model for the vote this model will make sure that the user can cast only one vote per question
class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name='unique_user_vote_per_question')
        ]

    def __str__(self):
        return f"{self.user.username} voted for {self.choice.choice_text}"