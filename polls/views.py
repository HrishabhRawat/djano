from django.db.models import F
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.http import Http404
from django.urls import reverse
from .models import Choice, Question, Vote
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import QuestionForm , ChoiceFormSet
from django.contrib.auth.decorators import login_required
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
    
    def get_context_data(self, **kwargs):
        # call the super model to get the default context (contains the question object)
        context = super().get_context_data(**kwargs)
        # check if the logged in user has already voted on the question 
        user_has_voted = False
        if self.request.user.is_authenticated:
            user_has_voted = Vote.objects.filter(
                user= self.request.user,
                question = self.object
            ).exists()
        context["user_has_voted"] = user_has_voted
        return context
    

        

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

@login_required
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
        # check if vote record already exists for this user and question
        already_voted = Vote.objects.filter(user = request.user, question = question).exists()
        if already_voted:
            return render(
                request, 
                "polls/detail.html",
                {
                    "question":Question,
                    "error_message":"You already cast your vote for this question"
                }
            )
        
        # save the new vote Transaction
        Vote.objects.create(user = request.user, question= question, choice= selected_choice)

        return HttpResponseRedirect(reverse("polls:results", args= [question_id]))


class QuestionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    fields = ["question_text"]
    success_url = reverse_lazy("polls:index")
    template_name = "polls/question_form.html"

    def test_func(self):
        # this is authorization check
        question = self.get_object()
        return self.request.user == question.author
    
class QuestionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Question
    success_url = reverse_lazy("polls:index")
    template_name = "polls/question_confirm_delete.html"

    def test_func(self):
        # this is authorization check
        question = self.get_object()
        return self.request.user == question.author

# Creating a view 
@login_required
def question_create_view(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        # Ensure both the Question text and all Choices are valid
        if form.is_valid() and formset.is_valid():
            # Save the question but dont commit it to the database yet
            question = form.save(commit=False)
            # Automate the background fields (Author and publication details)
            question.author = request.user
            question.pub_date = timezone.now()
            question.save()   # Save the question to generate the id

            # pass the saved question id into the formset so the choices link to it
            formset.instance = question
            formset.save()
            # question.save()   # save all changes to the data base

            return redirect("polls:index")
    else:
        # if accessing via a get method, display empty forms
        form = QuestionForm()
        formset = ChoiceFormSet()
    return render(
        request,
        "polls/question_create.html",
        {"form":form, "formset":formset}
    )
