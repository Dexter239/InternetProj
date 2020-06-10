from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from filesender.models import Notifications
from django.db.models import Q
import transliterate
import random
import string

responses = {}

def index(request):
    return render(request, "index.html")


def main_view(request):
    if request.user.is_authenticated:
        if Notifications.objects.filter(user=request.user.profile).count():
            notify = Notifications.objects.filter(user=request.user.profile)
        else:
            Notifications.objects.create(user=request.user.profile, notify="<p>Уведомлений нет</p>")
            notify = Notifications.objects.filter(user=request.user.profile)
        return render(request, "main.html", context={'user': request.user, 'notify': notify})
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
            search_user += '<li class="nav-item"><a class="nav-link" href="/user/'+str(user.id)+'">'+user.username+'</a></li>'
        return HttpResponse(search_user)


def user_page(request, user_id):
    if request.user.is_authenticated:
        user = User.objects.get(id=user_id)
        if Notifications.objects.filter(user=request.user.profile).count():
            notify = Notifications.objects.filter(user=request.user.profile)
        else:
            Notifications.objects.create(user=request.user.profile, notify="<p>Уведомлений нет</p>")
            notify = Notifications.objects.filter(user=request.user.profile)
        return render(request, "user.html", context={'user': user, 'myself': request.user, 'notify': notify})
    return HttpResponseRedirect('/login/')


def change_rights(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            user_id = request.POST.get('userID')
            right = request.POST.get('rights')
            myself = request.user
            if right == "allow":
                user = User.objects.get(id=user_id)
                delete_empty = Notifications.objects.filter(user=user.profile, notify="<p>Уведомлений нет</p>")
                delete_empty.delete()
                Notifications.objects.create(user=user.profile, notify="<p><span>Запрос на заявку в друзья от <b>"+request.user.username+"</b></span> <button onclick=\"location.href = '/add_to_friend/"+str(request.user.id)+"/'\" class=\"btn btn-success\"><i class=\"fa fa-check-square\"></i></button></p>")
                return render(request, "user.html", context={'user': user, 'myself':  myself})
            elif right == "decline":
                user = User.objects.get(id=user_id)
                if (user.profile in  myself.profile.friends.all()):
                    myself.profile.friends.remove(user.profile)
                    delete_empty = Notifications.objects.filter(user=user.profile, notify="<p>Уведомлений нет</p>")
                    delete_empty.delete()
                    Notifications.objects.create(user=user.profile, notify="<p>Пользователь <b>" + myself.username + "</b> удалил Вас из друзей.</p>")
                return render(request, "user.html", context={'user': user, 'myself':  myself})
    return HttpResponseRedirect('/login/')


def notification_center(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            action = request.POST.get('action')
            user_id = request.POST.get('userID')
            if action == "remove":
                user = User.objects.get(id=user_id)
                delete_empty = Notifications.objects.filter(user=user.profile)
                delete_empty.delete()
                Notifications.objects.create(user=request.user.profile, notify="<p>Уведомлений нет</p>")
                notify = Notifications.objects.filter(user=user.profile)
                notifyHTML = ""
                for note in notify:
                    notifyHTML += note.notify
                return HttpResponse(notifyHTML)
            elif action == "update":
                user = User.objects.get(id=user_id)
                notify = Notifications.objects.filter(user=user.profile)
                notifyHTML = ""
                for note in notify:
                    notifyHTML += note.notify
                return HttpResponse(notifyHTML)
    return HttpResponseRedirect('/login/')


def add_to_friend(request, user_id):
    if request.user.is_authenticated:
        user = User.objects.get(id=user_id)
        myself = request.user
        notifications = Notifications.objects.filter(user=myself.profile, notify="<p><span>Запрос на заявку в друзья от <b>"+user.username+"</b></span> <button onclick=\"location.href = '/add_to_friend/"+str(user.id)+"/'\" class=\"btn btn-success\"><i class=\"fa fa-check-square\"></i></button></p>")
        if notifications.count():
            if (user.profile not in myself.profile.friends.all()):
                myself.profile.friends.add(user.profile)
                delete_empty = Notifications.objects.filter(user=user.profile, notify="<p>Уведомлений нет</p>")
                delete_empty.delete()
                Notifications.objects.create(user=user.profile, notify="<p>Пользователь <b>"+myself.username+"</b> добавил Вас в друзья.</p>")
                notifications.delete()
            return HttpResponseRedirect('/main/')
        else:
            delete_empty = Notifications.objects.filter(user=myself.profile, notify="<p>Уведомлений нет</p>")
            delete_empty.delete()
            Notifications.objects.create(user=myself.profile,
                                         notify="<p>Вы играете с огнем!</p>")
            return HttpResponseRedirect('/main/')
    return HttpResponseRedirect('/login/')


def download(request, user_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            file = request.FILES.get('file')
            filename = file.name
            lang = transliterate.detect_language(filename)
            if lang == 'ru':
                filename = transliterate.translit(filename, reversed=True)
            user = User.objects.get(id=user_id)
            delete_empty = Notifications.objects.filter(user=user.profile, notify="<p>Уведомлений нет</p>")
            delete_empty.delete()
            response = HttpResponse(file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=' + filename
            token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
            responses[token] = response
            Notifications.objects.create(user=user.profile,
                                         notify="<p><span>Пользователь <b>" + request.user.username + "</b> хочет отправить вам файл <b>" + filename + "</b></span> <button onclick=\"location.href = '/file/" + str(
                                             token) + "/accept/'\" class=\"btn btn-success\"><i class=\"fa fa-check-square\"></i></button> <button onclick=\"location.href = '/file/" + str(
                                             token) + "/decline/'\" class=\"btn btn-danger\"><i class=\"fa fa-ban\"></i></button></p>")
            return HttpResponseRedirect('/main/')
    return HttpResponseRedirect('/login/')


def download_file(request, file_id, action):
    if request.user.is_authenticated:
        delete_empty = Notifications.objects.filter(user=request.user.profile)
        delete_empty.delete()
        Notifications.objects.create(user=request.user.profile, notify="<p>Уведомлений нет</p>")
        if action == "accept":
            return responses.pop(file_id)
        elif action == "decline":
            responses.pop(file_id)
            return HttpResponseRedirect('/main/')
    return HttpResponseRedirect('/login/')