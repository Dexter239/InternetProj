from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q


def index(request):
    return render(request, "index.html")


def main_view(request):
    if request.user.is_authenticated:
        return render(request, "main.html", context={'user': request.user})
    return HttpResponseRedirect('/login/')


class RegisterFormView(FormView):
    form_class = UserCreationForm
    success_url = "/login/"
    template_name = "register.html"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)


class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = "/main/"

    def form_valid(self, form):
        self.user = form.get_user()
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect("/")


def search_friends(request):
    if request.method == "GET":
        username = request.GET.get('username')
        ans_user = User.objects.filter(Q(username__icontains=username))
        search_user = ''
        for user in ans_user:
            search_user += '<p>'+user.username+'</p>'
        return HttpResponse(search_user)