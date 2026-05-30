from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.http import Http404
from django.urls import reverse
from .models import Choice, Question
from django.utils import timezone
# Create your views here.

# def index(request):
#     latest_question_list = Question.objects.order_by("pub_date")[:5]     # orm
#     # template = loader.get_template("polls/index.html")
#     # context = {"latest_question_list":latest_question_list}
#     # return HttpResponse(template.render(context, request))
#     context = {"latest_question_list":latest_question_list}
#     return render(request, "polls/index.html" ,context)

# def detail(request, question_id):
#     # return HttpResponse("You are lookin at the question %s."%question_id)

    
#     # try:
#     #     question = Question.objects.get(pk=question_id)
#     # except Question.DoesNotExist:
#     #     raise Http404("Question does not Exist")
#     # return render(request, "polls/detail.html",{"question": question})

#     question = get_object_or_404(Question, pk= question_id)
#     return render(request, 'polls/detail.html', {"question": question})


# def results(request, question_id):
#     question = get_object_or_404(Question, pk = question_id)
#     return render(request, "polls/result.html", {"question":question} )


# Using class Based views
# index view class
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """ Return the last five published question (not including those set to be published in future)"""
        return Question.objects.filter(pub_date__lte = timezone.now()).order_by("-pub_date")[:5]
    

# Detail view
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """ Excludes any questions that aren't published yet """
        return Question.objects.filter(pub_date__lte = timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request, 
            "polls/detail.html",
            {
                "question":question,
                "error_message":"You didn't select a choice",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question_id,)))



