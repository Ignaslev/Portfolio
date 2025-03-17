from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from django.contrib.auth import logout

from .forms import UserUpdateForm, ProfileUpdateForm, CustomBurgerForm, BurgerReviewForm
from .models import User, MenuItem, Order, OrderItem, CustomBurger, CustomBurgerRecipe, Ingredient, BurgerReview, \
    BlogPost
from .utils import generate_burger_image


def index(request):
    '''
    Renders the homepage with a paginated list of blog posts.
    Retrieves all blog posts ordered by creation date (newest first) and paginates them,
    displaying three posts per page.
    '''

    blog_posts = BlogPost.objects.all().order_by('-created_at')

    paginator = Paginator(blog_posts, 3)
    page_number = request.GET.get('page')
    paged_blog_posts = paginator.get_page(page_number)

    context = {
        'blog_posts': paged_blog_posts
    }
    return render(request, 'burger_shop/index.html', context=context)


def blog_post(request, pk):
    '''
    Renders page for one blog post
    '''
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'burger_shop/blog_post.html', {'post': post})


def custom_logout(request):
    """
    Custom logout view to log out users and show a custom page.
    """
    logout(request)
    return render(request, 'burger_shop/registration/logged_out.html')


def menu(request):
    '''
    Renders the menu page with categorized menu items.
    Filters menu items by category and
    passes them to the 'menu.html' template for display.
    '''
    burgers = MenuItem.objects.filter(category='Burgers').select_related('nutrition')
    sides = MenuItem.objects.filter(category='Sides').select_related('nutrition')
    drinks = MenuItem.objects.filter(category='Drinks').select_related('nutrition')


    context = {
        'burgers': burgers,
        'sides': sides,
        'drinks': drinks,
    }

    return render(request, 'burger_shop/menu.html', context=context)


def all_custom_burgers(request):
    '''
    Renders a paginated list of all custom burgers with optional sorting.
    Retrieves all custom burgers, calculates their average rating, and allows sorting
    by either 'rating' or 'date'.
    '''
    sort_by = request.GET.get('sort', 'date')
    custom_burgers = CustomBurger.objects.annotate(avg_rating=Avg('burgerreview__rating'))

    if sort_by == 'rating':
        custom_burgers = custom_burgers.order_by('-avg_rating', '-created_at')
    elif sort_by == 'date':
        custom_burgers = custom_burgers.order_by('-created_at')

    paginator = Paginator(custom_burgers, 8)
    page_number = request.GET.get('page')
    paged_burgers = paginator.get_page(page_number)

    context = {
        'custom_burgers': paged_burgers,
        'sort_by': sort_by,
    }

    return render(request, 'burger_shop/custom_burgers.html', context=context)


@csrf_protect
def register_user(request):
    '''
    Handles user registration.
    If form method is 'POST':
    Retrievs all info from form, checks if username and email available and if passwords match.
    Creates user object.
    Signal creates profile.
    Assigns to group 'customer'.
    Assigns phone number to profile.
    '''
    if request.method == 'GET':
        return render(request, 'registration/registration.html')

    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_nr = request.POST.get('phone_nr')

        if password != password2:
            messages.error(request, "Passwords doesn't match")
            return redirect('burger_shop:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'User already exists')
            return redirect('burger_shop:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('burger_shop:register')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )

        customer_group = Group.objects.get(name='Customer')
        user.groups.add(customer_group)

        user.profile.phone = phone_nr
        user.profile.save()

        messages.info(request, f'Registration of {username} successful')
        return redirect('login')


@login_required
def get_user_profile(request):
    '''
    Handles displaying and updating the user's profile.

    If form method is 'POST', retrieves data from the Profile and User update forms.
    Validates and saves forms if valid, displays success message.
    On error, shows an error message.
    For 'GET', displays profile and user data in the forms.
    '''
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            p_form.save()
            u_form.save()
            messages.info(request, 'Profile updated')
        else:
            messages.error(request, 'Error')
        return redirect('burger_shop:user-profile')

    p_form = ProfileUpdateForm(instance=request.user.profile)
    u_form = UserUpdateForm(instance=request.user)

    context = {
        'p_form': p_form,
        'u_form': u_form
    }

    return render(request, 'burger_shop/profile.html', context=context)


@login_required(login_url='burger_shop:pls_login')
def start_order(request):
    '''
    Creates a new draft order for the logged-in user.

    Sets the order status to 'd' (draft).
    Redirects to the order detail page for the created order.
    '''
    order = Order.objects.create(user=request.user, order_status='d')

    return redirect('burger_shop:order_detail', order_id=order.id)


def pls_login(request):
    '''
    Please log in page for 'start_order'.

    As start_order creates draft order immidiatly, we use custom log in page to display if user is not authenticated
    to prevent errors.
    '''
    return render(request, 'burger_shop/pls_login.html')


@login_required
def order_detail(request, order_id):
    '''
    Handles displaying and updating user's order.

    Retrieves the current order by ID and user. Displays menu items and user's custom burgers with pagination.

    POST requests handle:
    - Removing items from the order ('remove_item_id').
    - Adding items to the order. If the item already exists, updates the quantity.

    Calculates the total price of the order, including both menu items and custom burgers.
    Redirects back to the same page after each POST action.
    '''
    order = get_object_or_404(Order, id=order_id, user=request.user)

    burgers = MenuItem.objects.filter(category='Burgers')
    sides = MenuItem.objects.filter(category='Sides')
    drinks = MenuItem.objects.filter(category='Drinks')

    order_items = order.orderitem_set.all()
    all_user_burgers = CustomBurger.objects.filter(user=request.user)

    for item in order_items:
        if item.menu_item:
            item.total_item_price = item.menu_item.price * item.quantity
        elif item.custom_burger:
            item.total_item_price = item.custom_burger.total_price * item.quantity

    total_price = sum(item.total_price for item in order_items)

    paginator = Paginator(all_user_burgers, 4)
    page_number = request.GET.get('page')
    user_burgers_page = paginator.get_page(page_number)

    if request.method == 'POST':

        # IF USER PRESES REMOVE, ITEM ID IS PASSED AND ITEM GETS REMOVED FROM ORDER
        remove_item_id = request.POST.get('remove_item_id')
        if remove_item_id:
            # FIND ITEM ID IN ORDER TO REMOVE
            order_item_to_remove = get_object_or_404(OrderItem, id=remove_item_id, order=order)
            # DELETS ITEM
            order_item_to_remove.delete()
            return redirect('burger_shop:order_detail', order_id=order.id)

        # ADDING ITEM TO ORDER, EXTRACTING ITEM DETAILS
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))

        if item_id and quantity > 0:
            # ADDING ITEMS TO ORDER OF TYPE 'MENU_ITEM'
            if item_type == 'menu_item':
                # GET ITEM ID
                menu_item = get_object_or_404(MenuItem, id=item_id)
                # CHECKS IF ITEM ALREADY IN ORDER, CREATES ITEM IF NOT
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    menu_item=menu_item,
                    defaults={'quantity': quantity}
                )
            # ADDING CUSTOM BURGERS TO MENU
            elif item_type == 'custom_burger':
                # GET ID
                custom_burger = get_object_or_404(CustomBurger, id=item_id)
                # CHECKS IF BURGER ALREADY IN ORDER, CREATES IF NOT
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    custom_burger=custom_burger,
                    defaults={'quantity': quantity}
                )

            # IF ITEM ALREADY IN ORDER, UPDATES QUANTITY IF ADDED AGAIN
            if not created:
                order_item.quantity += quantity
                order_item.save()

        return redirect('burger_shop:order_detail', order_id=order.id)

    context = {
        'order': order,
        'order_items': order_items,
        'burgers': burgers,
        'sides': sides,
        'drinks': drinks,
        'user_burgers': user_burgers_page,
        'total_price': total_price,
        'total_nutrition': order.total_nutrition,
    }
    return render(request, 'burger_shop/order_detail.html', context)


@login_required
def finalize_order(request, order_id):
    '''
    Handles final review and confirmation of draft order.

    GET request:
    - Displays draft order with items and total price.
    - Redirects if order is not in 'draft' status.

    POST request:
    - 'update': Updates item quantities or removes items if quantity is zero.
    - 'remove_<item_id>': Removes item.
    - 'confirm': Changes order status to 'confirmed' if the order has items.
    '''
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.order_status != 'd':
        return redirect('order_detail', order_id=order.id)

    order_items = order.orderitem_set.all()
    total_price = sum(item.total_price for item in order_items)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            for item in order_items:
                quantity = int(request.POST.get(f'quantity_{item.id}', item.quantity))
                if quantity > 0:
                    item.quantity = quantity
                    item.save()
                else:
                    item.delete()

        elif action.startswith('remove_'):
            item_id = int(action.split('_')[1])
            order_item = get_object_or_404(OrderItem, id=item_id, order=order)
            order_item.delete()

        elif action == 'confirm':
            if order_items.exists():
                order.order_status = 'co'
                order.save()
                return redirect('burger_shop:order_success')

        return redirect('burger_shop:finalize_order', order_id=order.id)

    context = {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
    }
    return render(request, 'burger_shop/finalize_order.html', context)


@login_required
def order_success(request):
    '''
    Displays the order success page after an order is confirmed.
    '''
    return render(request, 'burger_shop/order_success.html')


@login_required
def user_orders(request):
    '''
    Displays paginated list of user's orders.

    Orders include related menu items and custom burgers for clearity.
    Sorted by most recent orders first.
    '''
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__menu_item',
                                                                      'orderitem_set__custom_burger').order_by('-time')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    paged_orders = paginator.get_page(page_number)

    return render(request, 'burger_shop/user_orders.html', {'orders': paged_orders})


@login_required
def user_burgers(request):
    '''
    Displays paginated list of user's custom burgers.

    Sorted by most recent burgers first.

    Handles sorting method, can sort by date or rating.
    '''
    sort_by = request.GET.get('sort', 'date')
    burgers = CustomBurger.objects.filter(user=request.user).annotate(avg_rating=Avg('burgerreview__rating'))

    if sort_by == 'rating':
        burgers = burgers.order_by('-avg_rating', '-created_at')
    elif sort_by == 'date':
        burgers = burgers.order_by('-created_at')

    paginator = Paginator(burgers, 8)
    page_number = request.GET.get('page')
    paged_burgers = paginator.get_page(page_number)

    return render(request, 'burger_shop/user_burgers.html', {'burgers': paged_burgers, 'sort_by': sort_by})


def get_user_burger(request, burger_id):
    '''
    Displays a specific custom burger with its recipe and reviews.

    Authenticated users can leave a review if they haven't already.
    Handles burger review form submission and displays all burger reviews.
    '''
    burger = get_object_or_404(CustomBurger, pk=burger_id)
    recipe_items = burger.customburgerrecipe_set.all()

    if request.user.is_authenticated:
        user_review = BurgerReview.objects.filter(user=request.user, burger=burger).first()

    form = None
    if request.user.is_authenticated and not user_review:
        if request.method == 'POST':

            form = BurgerReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.burger = burger
                review.user = request.user
                review.save()
                return redirect('burger_shop:user_burger', burger_id=burger_id)

        else:
            form = BurgerReviewForm(initial={'burger': burger, 'user': request.user})

    reviews = BurgerReview.objects.filter(burger=burger)

    context = {
        'burger': burger,
        'recipe_items': recipe_items,
        'form': form,
        'reviews': reviews

    }
    return render(request, 'burger_shop/custom_burger.html', context)


def create_burger(request):
    '''
    Handles the creation of a custom burger.

    - Displays available buns and ingredients for selection.
    - Processes the form submission to create a burger with selected ingredients.
    - Validates ingredient selection and handles errors.
    - Tracks ingredient quantities and updates the database.
    - Generates a burger image using the selected ingredients and saves it.
    - Redirects to the burger creation success page upon completion.
    '''
    # PULL OUT BUNS AND INGREDIENTS TO DISPLAY
    buns = Ingredient.objects.filter(category='Bun').all()
    ingredients = Ingredient.objects.exclude(category='Bun')

    categorized_ingredients = {
        'patty': Ingredient.objects.filter(category='Patty'),
        'cheese': Ingredient.objects.filter(category='Cheese'),
        'vegetables': Ingredient.objects.filter(category='Vegetables'),
        'sauce': Ingredient.objects.filter(category='Sauce'),
        'extras': Ingredient.objects.filter(category='Extras'),
    }

    if request.method == 'POST':
        # PULL OUT CREATED BURGER DATA
        burger_name = request.POST.get('name')
        bun_id = request.POST.get('bun_id')
        ingredients_data = request.POST.get('ingredients')

        # IF NO INGREDIENTS REDIRECT BACK WITH ERROR MESSAGE
        if not ingredients_data:
            return render(request, 'burger_shop/create_burger.html',
                          {'form': CustomBurgerForm(), 'error': 'Please select ingredients!'})

        # FROM STRING OF INGREDIENTS IDS MAKING LIST OF NUMBERS
        ingredient_ids = [int(i) for i in ingredients_data.split(',')]
        # GETTING TOP BUN NAME (FOR IMAGE GENERATOR
        top_bun_name = Ingredient.objects.get(id=bun_id).part_image.name

        # CREATE BURGER
        burger = CustomBurger.objects.create(
            user=request.user,
            name=burger_name
        )

        # ADD QUANTITIES OF INGREDIENTS AND ASSIGN INGREDIENT IMAGE PATH FOR IMAGE GENERATOR
        ingredient_quantities = {}
        ingredient_image_paths = []

        # UPDATING INGREDIENT QUANTITIES, IF ADDED FIRST TIME DEFAULT IS ONE, IF ADDED AGAIN ADDS QUANTITY
        for ing_id in ingredient_ids:
            if ing_id in ingredient_quantities:
                ingredient_quantities[ing_id] += 1
            else:
                ingredient_quantities[ing_id] = 1

        # CREATING CUSTOM BURGER RECEPIE (TO MODEL DATABASE)
        for ing_id, quantity in ingredient_quantities.items():
            ingredient = Ingredient.objects.get(id=ing_id)
            CustomBurgerRecipe.objects.create(
                custom_burger=burger,
                ingredient=ingredient,
                quantity=quantity
            )

            # IF INGRIDIENT HAS QAUNTITY MORE THAN ONE WE REPEAT IMAGE PATH AS MANY TIMES AS QUANTITY (FOR IMAGE GENERATOR)
            if ingredient.part_image:
                ingredient_image_paths.extend([ingredient.part_image.name] * quantity)

        # CREATES COMPLETED BURGER IMAGE WITH FUNCTION IN UTILS.PY
        if ingredient_image_paths:
            image_path = generate_burger_image(ingredient_image_paths, burger.id, top_bun_name)
            burger.image.name = image_path
            burger.save()

        return redirect('burger_shop:create_burger_success')

    form = CustomBurgerForm()
    return render(request, 'burger_shop/create_burger.html', {'form': form, 'buns': buns, 'ingredients': ingredients, 'categorized_ingredients': categorized_ingredients})


@login_required
def create_burger_success(request):
    '''
    Renders the burger creation success page.
    '''
    return render(request, 'burger_shop/create_burger_success.html')
