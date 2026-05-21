from django.shortcuts import render
from django.http import HttpResponse
from .models import Question

# Create your views here.

def index(request):
    latest_question_list = Question.objects.order_by("pub_date")[:5] 
    output = ", ".join([q.question_text for q in latest_question_list])
    return HttpResponse(output)

def detail(request, question_id):
    return HttpResponse("You are lookin at the question %s."%question_id)

def results(request, question_id):
    response = "You are lookin at the result of the Question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You are voting on the question %s." %question_id)



