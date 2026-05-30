from django.urls import path
from .import views

app_name= "polls"
urlpatterns = [
    # ex: /polls/
    path("", views.IndexView.as_view(), name="index"),
    # ex: /polls/5/
    path("<int:pk>/", views.DetailView.as_view() , name="detail"),
    # ex: /polls/5/results/
    path("<int:pk>/results/" , views.ResultsView.as_view() , name="results"),
    # ex /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
    # Url for editing a Question
    path("<int:pk>/update/", views.QuestionUpdateView.as_view(), name= "question_update"),
    # url for deleting a Question
    path("<int:pk>/delete/", views.QuestionDeleteView.as_view(), name="question_delete"),
]
