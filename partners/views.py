from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from telecompanies.models import Offer
from utils.forms import AddressForm
from .models import PartnerEmployee
from .forms import UserForm, CreatePartnerForm

class PartnersLoginView(LoginView):
    success_url = reverse_lazy('partners:partners_home')
    template_name = 'registration/login.html'
    # TODO check if the user is not activated then give a message that you are not activated
    # def post(self, *args, **kwargs):
    #     username = self.request.POST.get('username', '')
    #     password = self.request.POST.get('password', '')
    #     user = authenticate(username=username, password=password)
    #     import pdb; pdb.set_trace()
    #     if user and not user.is_active:
    #         messages.warning(self.request, _('Sorry! You are not yet activated.'))
    #         return redirect('login')

    #     super(PartnersLoginView, self).get(self.request, *args, **kwargs)
        # login(self.request, kwargs)
            # return HttpResponseRedirect("client/items")

        # employee = PartnerEmployee.objects.filter(user=self.request.user)
        # if not employee: 
        #     messages.warning(self.request, _('Sorry! You are not registered to create offers.'))

    #     if user is not None and user.is_active:
    #         login(self.request, user)
    #         return HttpResponseRedirect("client/items")
    #     else:
    #         return HttpResponse("Invalid login. Please try again.")


class CreateOfferView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Offer
    success_url = reverse_lazy('partners:partners_home')
    fields = [
        'mobile',
        'telecom_company',
        'mobile_name',
        'discount',
        'discount_offered',
        'offer_url',
        'price',
    ]
    template_name = 'partners/create_offer.html'

    def test_func(self):
        """Check if an employee is creating this offer. 
        And the offer being created is for this employees company.
        An employee can create offre only for its own company."""
        employee = PartnerEmployee.objects.filter(user=self.request.user)
        if not employee: 
            messages.warning(self.request, _('Sorry! You are not registered to create offers.'))
            return False
        employee = employee[0]
        # If this is an employee and its 
        # not a post request then load 
        # the form without further checks
        if self.request.method != 'POST': return True
        # Check if the employee is posting 
        # an offer for its own company or not
        elif self.request.POST.get('telecom_company') != str(employee.company.id):
            messages.warning(self.request, _('Sorry! You can create offers only for your company.'))
            return False
        return True


class PartnersCreateView(View):
    """A partner can signup and create account using PartnerCreateView."""
    def get(self, *args, **kwargs):
        context = {
            'user_form': UserForm(),
            'partners_form': CreatePartnerForm(),
            'address_form': AddressForm(),
        }
        return render(self.request, 'registration/signup.html', context)

    def post(self, *args, **kwargs):
        user_form = UserForm(self.request.POST)
        employee_form = CreatePartnerForm(self.request.POST, self.request.FILES)
        address_form = AddressForm(self.request.POST)
        if user_form.is_valid() and employee_form.is_valid() and address_form.is_valid():
            user = user_form.save()
            user.set_password(user_form.cleaned_data['password'])
            user.is_active = False
            user.save()
            address = address_form.save()
            # bday = employee_form.cleaned_data.get("birth_date")
            image = employee_form.cleaned_data.get('image')
            company = employee_form.cleaned_data.get('company')
            employee = PartnerEmployee.objects.create(
               user = user,
            #    birth_date = bday,
               image = image,
               company = company,
               address = address, 
            )
            messages.success(self.request, _('Your account was successfully created!'))
            return redirect('partners:signup_success')
        messages.error(self.request, _('Unable to create account!'))
        context = {
            'user_form':user_form,
            'partners_form':employee_form,
            'address_form':address_form,
        }
        return render(self.request, 'registration/signup.html', context, status=400)


class PartnersHome(LoginRequiredMixin, View):
    """Displays the offers posted by user's company.
    User (partner's employee) is provided with different
    options. e.g. Creating, Deleting offers and profile."""
    def get(self, *args, **kwargs):
        # Get the employee and the related company
        employee = PartnerEmployee.objects.filter(user=self.request.user)
        context = {}
        if employee: 
            employee = employee[0]
            if employee.company:
                context['offers'] = Offer.objects.filter(telecom_company=employee.company)
                context['company'] = employee.company.name
        return render(self.request, 'partners/partners_home.html', context)


class DeleteOfferView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Offer
    success_url = reverse_lazy('partners:partners_home')
    def test_func(self):
        employee = PartnerEmployee.objects.filter(user=self.request.user)
        if not employee: return False
        employee = employee[0]
        pk = self.kwargs['pk']
        offer = Offer.objects.get(id=pk)
        telecom_company = offer.telecom_company
        # Check if the employee is posting 
        # an offer for its own company or not
        if telecom_company.id != employee.company.id:
            messages.warning(self.request, _('Sorry! You can delete offers only for your company.'))
            return False
        return True


class UpdateOfferView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offer
    fields = ['mobile', 'telecom_company', 'mobile_name', 'discount', 'discount_offered', 'offer_url', 'price']
    template_name_suffix = '_update_form'

    def test_func(self):
        employee = PartnerEmployee.objects.filter(user=self.request.user)
        if not employee: return False
        employee = employee[0]
        pk = self.kwargs['pk']
        offer = Offer.objects.get(id=pk)
        telecom_company = offer.telecom_company
        # Check if the employee is posting 
        # an offer for its own company or not
        if telecom_company.id != employee.company.id:
            messages.warning(self.request, _('Sorry! You can only edit offers from your company.'))
            return False
        return True
