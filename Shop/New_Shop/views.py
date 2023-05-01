from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from New_Shop.forms import *
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import user_passes_test
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import SubscribedUser, Product


def home_page(request):
    category_list = Category.objects.all()
    context = {
        'title': 'Shop',
        'categories': category_list
    }
    return render(request, 'home page.html', context)


def product(request, category_slug=None):
    query = request.GET.get('q')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        queryset = Product.objects.filter(category=category)
    else:
        if query:
            queryset = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        else:
            queryset = Product.objects.all()
    category_list = Category.objects.all()
    paginator = Paginator(queryset, 2)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    context = {
        'title': 'Product',
        'objects_list': queryset,
        'categories': category_list,
        'search_query': query,
        'page_request_var': page_request_var
    }
    return render(request, 'product.html', context)


def detail(request, id_product, product_slug):
    instance = get_object_or_404(Product, id=id_product,
                                 slug=product_slug,
                                 available=True)
    category_list = Category.objects.all()
    context = {
        'title': 'Detail',
        'object': instance,
        'categories': category_list,
    }
    return render(request, 'detail.html', context)


def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_staff_or_superuser)
def create(request):
    form = ProductForm(request.POST or None,
                       request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, 'Продукт збережено!')
        messages.info(
            request, '<a href="/create">Створити</a> ще 1 продукт?',
            extra_tags='html_safe'
        )
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        'title': 'Create',
        'form': form
    }
    return render(request, 'create.html', context)


@user_passes_test(is_staff_or_superuser)
def update(request, id_product=None):
    instance = get_object_or_404(Product, id=id_product)
    form = ProductForm(request.POST or None,
                       request.FILES or None,
                       instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.info(
            request, '<a href="/create">Створити</a> новий продукт?',
            extra_tags='html_safe'
        )
        messages.info(
            request, '<a href="/">Вернутись на домашню сторінку?</a>',
            extra_tags='html_safe'
        )
        messages.success(
            request, f'<a href="/detail/{id}">Продукт</a> збережено!',
            extra_tags='html_safe'
        )
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        'title': 'Update',
        'form': form
    }
    return render(request, 'create.html', context)


@user_passes_test(is_staff_or_superuser)
def delete(request, id_product=None):
    instance = get_object_or_404(Product, id=id_product)
    instance.delete()
    messages.success(request, 'Продукт видалено!')
    return redirect('New_Shop:home_page')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Customer.objects.create(user=user)
            messages.success(request, "Registration successful.")
            return redirect(request.session.get('previous_url', 'New_Shop:home_page'))
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    context = {
        'title': 'register',
        'register_form': form
    }
    request.session['previous_url'] = request.META.get('HTTP_REFERER', 'New_Shop:home_page')
    return render(request, 'registration/register.html', context)


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect(request.session.get('previous_url', 'New_Shop:home_page'))
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    context = {
        'title': 'register',
        'login_form': form
    }
    request.session['previous_url'] = request.META.get('HTTP_REFERER', 'New_Shop:home_page')
    return render(request, 'registration/login.html', context)


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect(request.META.get("HTTP_REFERER", 'New_Shop:home_page'))


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return redirect('New_Shop:home_page')
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    context = {
        'password_reset_form': password_reset_form
    }
    return render(request, 'registration/password_reset.html', context)


def subscribe(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)

        if not name or not email:
            messages.error(request, "You must type legit name and email to subscribe to a Newsletter")
            return redirect('New_Shop:home_page')

        if get_user_model().objects.filter(email=email).first():
            messages.error(request,
                           f"Found registered user with associated {email}"
                           f" email. You must login to subscribe or unsubscribe.")
            return redirect(request.META.get("HTTP_REFERER", 'New_Shop:home_page'))

        subscribe_user = SubscribedUser.objects.filter(email=email).first()
        if subscribe_user:
            messages.error(request, f"{email} email address is already subscriber.")
            return redirect(request.META.get("HTTP_REFERER", 'New_Shop:home_page'))

        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect('New_Shop:home_page')

        subscribe_model_instance = SubscribedUser()
        subscribe_model_instance.name = name
        subscribe_model_instance.email = email
        subscribe_model_instance.save()
        messages.success(request, f'{email} email was successfully subscribed to our newsletter!')
        return redirect(request.META.get("HTTP_REFERER", 'New_Shop:home_page'))


def cart(request):
    products, total, discount = [], 0, 0

    if 'cart' in request.session:
        products, total = get_products_and_total(request)

    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
    else:
        guest_user, created = User.objects.get_or_create(username='guest')
        customer, created = Customer.objects.get_or_create(user=guest_user)

    address_form = AddressForm()

    if request.method == 'POST':
        address_form = AddressForm(request.POST)

        if address_form.is_valid():
            quantity = request.COOKIES.get('product_count_in_cart', 0)

            instance = address_form.save(commit=False)
            instance.customer = customer
            instance.quantity = quantity
            instance.total_price = total
            instance.status = 'Pending'
            instance.save()

            for p in products:
                instance.product.add(p)

            return redirect('New_Shop:payment')
    context = {'products': products, 'total': total, 'address_form': address_form}
    return render(request, 'cart/cart.html', context)


def get_products_and_total(request):
    products_in_cart = request.session['cart']
    product_ids = list(products_in_cart.keys())
    products = Product.objects.filter(id__in=product_ids)
    total = 0

    for p in products:
        p.quantity = products_in_cart[str(p.id)]['quantity']
        total += p.price * p.quantity

    return products, total


def add_to_cart(request, pk):
    instance = get_object_or_404(Product, id=pk, available=True)
    if 'cart' not in request.session:
        request.session['cart'] = {}
    products_in_cart = request.session['cart']
    quantity = int(request.POST.get('quantity', 1))
    if str(pk) in products_in_cart:
        products_in_cart[str(pk)]['quantity'] += quantity
    else:
        products_in_cart[str(pk)] = {'quantity': quantity}
    request.session.modified = True
    messages.info(request, f"{quantity} {instance.name} added to cart successfully!")
    return redirect(request.META.get("HTTP_REFERER", 'New_Shop:home_page'))


def remove_from_cart(request, pk):
    if 'cart' in request.session:
        products_in_cart = request.session['cart']
        if str(pk) in products_in_cart:
            remove_quantity = int(request.POST.get('remove_quantity', 1))
            if products_in_cart[str(pk)]['quantity'] <= remove_quantity:
                del products_in_cart[str(pk)]
            else:
                products_in_cart[str(pk)]['quantity'] -= remove_quantity
            request.session.modified = True
    return redirect('New_Shop:cart')


def payment(request):
    return render(request, 'cart/payment.html')
