from django.shortcuts import render, HttpResponse

# Create your views here.


def set_sessions(request):
    request.session['name'] = 'gao'
    return HttpResponse('OK')

def get_sessions(request):
    name = request.session.get('name')
    return HttpResponse(name)

