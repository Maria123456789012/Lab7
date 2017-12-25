from django.shortcuts import render
from django.views.generic.edit import FormView
#from django.contrib.auth.forms import UserCreationForm
# Опять же, спасибо django за готовую форму аутентификации.
#from django.contrib.auth.forms import AuthenticationForm
from dz2.form import UserCreationForm
from dz2.form import AuthenticationForm
# Функция для установки сессионного ключа.
# По нему django будет определять, выполнил ли вход пользователь.
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.contrib.auth import logout
from dz2 import models
from django.contrib.auth.models import User
from dz2 import form
from django.shortcuts import redirect, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)

        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/")

class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "login.html"

    # В случае успеха перенаправим на главную.
    success_url = "/"

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()

        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)

class RegisterFormView(FormView):
    form_class = UserCreationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/login/"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)
# Create your views here.

class flowers_view(ListView):
    model = models.Flowers

    def get(self, request):
        d = self.model.objects.values('id','name','picture')
        paginator = Paginator(d, 6)  # Show 25 contacts per page
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        if(contacts.paginator.num_pages <= 4):
            r = range(1, contacts.paginator.num_pages+1)
        else:
            r = range(contacts.number-1, contacts.number+4)
        return render(request, 'flowers.html', {"contacts": contacts, 'user': request.user, 'range': r})

class flower_view(View):
    model = models.Flowers
    model1 = models.Flower_user
    model2 = User
    def get(self, request,id1):

        b = dict(flower=self.model.objects.filter(id=id1))

        a = dict(users=self.model1.objects.filter(flower_id=id1))

        b.update(a)
        c={'user':request.user}
        b.update(c)
        d={'id':id1}
        b.update(d)
        return render(request, "flower.html", b)

class create_flower(FormView):
    form_class = form.Flower_form
    model = models.Flowers
    template_name = "create_flower.html"
    success_url = "/flowers/"
    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(create_flower, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form1 = form.Flower_form(request.POST)
        if form1.is_valid() and request.FILES.get('picture'):
            obj = models.Flowers()
            obj = form1.save(commit=False)
            obj.picture = request.FILES['picture']
            obj.save()
            b = dict(flower=self.model.objects.filter(name=obj.name))
            return HttpResponseRedirect("/flower/"+str(b['flower'][0].id))
        else:
            form1.add_error('picture', 'Добавьте картинку')
        return render(request, 'create_flower.html', {'form':form1})

class add(View):
    model = models.Flowers
    model1 = models.Flower_user
    model2 = User
    def get(self, request, id2):
        if request.user.is_authenticated:
            u = self.model2.objects.filter(id=request.user.id)
            a = dict(users=self.model1.objects.filter(flower_id=id2))
            b = dict(flower=self.model.objects.filter(id=id2))
            ab = dict(users=self.model1.objects.filter(flower_id=id2))
            b.update(ab)
            er = 0
            for i in a['users']:
                if i.user_id == request.user:
                    er = 1
                    break
            if er == 1:
                ca = {'uze': "Вы уже заказали эти цветы"}
                b.update(ca)
                k = {'message':""}
                ca = {'error':''}
                b.update(k)
                b.update(ca)
                d = {'id': id2}
                b.update(d)
                return render(request, "flower.html", b)
            else:

                a=models.Flower_user()

                a.flower_id=b['flower'][0]
                a.user_id=u[0]
                a.save()

                k = {'message':"Вы успешно заказали цветы"}
                ca = {'error':''}
                b.update(k)
                b.update(ca)
                d = {'id': id2}
                b.update(d)

                return render(request, "flower.html", b)
        else:
            b = dict(flower=self.model.objects.filter(id=id2))
            a = {'error': "Вы не авторизованны. Войдите или зарегистрируйтесь"}
            c = {'message':''}
            b.update(a)
            b.update(c)
            d = {'id': id2}
            b.update(d)
            ab = dict(users=self.model1.objects.filter(flower_id=id2))
            b.update(ab)
            return render(request, "flower.html", b)