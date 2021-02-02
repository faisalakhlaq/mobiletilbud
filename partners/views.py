from django.shortcuts import render
from django.views.generic import View

class PartnersLogin(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'partners/login.html', {})
