from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from tinymce.models import HTMLField


class Profile(models.Model):
    '''
    User's profile model, to be able to add phone number and picture.

    Fields:
    user - One-to-one relationship with Django user
    phone - user phone number
    picture - Image field to add picture to profile, can be left blank and empty
    '''

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField('Phone number', max_length=50)
    picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return f'{self.user} profile'

    @property
    def picture_url(self):
        '''
            Model property picture url.
            Assigns default value /media/default-user.png if no picture is uploaded or 'cleared'
            If picture was uplaoded returns picture url
            '''

        if self.picture:
            return self.picture.url
        return '/media/default-user.png'

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        app_label = 'burger_shop'


class Nutrition(models.Model):
    '''
    Stores nutritional values for ingredients and menu items.

    "ingredient" and "menu_item" creates one to one relationship (one can have only one nutrition entry). Either can be
    empty and "Null' if other is chosen.
    '''
    calories = models.PositiveIntegerField(default=0)
    protein = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    fat = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    carbs = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    ingredient = models.OneToOneField(
        'Ingredient',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='nutrition'
    )

    menu_item = models.OneToOneField(
        'MenuItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='nutrition'
    )

    class Meta:
        app_label = 'burger_shop'


class Order(models.Model):
    '''
    Model Order - where we create main order.

    Fields:
    user - One to many field (One user can have many orders)
    time - automatic field which adds time stamp when order was created
    order_status - status of order. When order is created we assign draft, once its confirmed we change to confirmed.
    '''
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    ORDER_STATUS = (
        ('d', 'Draft'),
        ('co', 'Confirmed'),
        ('f', 'Finished'),
        ('ca', 'Cancelled')
    )

    order_status = models.CharField('Order status',
                                    max_length=2,
                                    choices=ORDER_STATUS,
                                    default='d',
                                    help_text='Status of order')

    @property
    def total_price(self):
        '''
        Calculates final price of whole order.
        This sums up the total_price of all related OrderItems.
        :return: integer
        '''
        return sum(item.total_price for item in self.orderitem_set.all())

    @property
    def total_nutrition(self):
        '''
        Calculates total nutrition for the entire order by summing all order items.
        '''
        nutrition_sum = {}
        for item in self.orderitem_set.all():
            for key, value in item.item_total_nutrition.items():
                nutrition_sum[key] = nutrition_sum.get(key, 0) + value
        return nutrition_sum

    def __str__(self):
        user_info = f'{self.user.id}. {self.user}' if self.user else 'No user'
        return f'{user_info}, {self.time}'

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        app_label = 'burger_shop'


class MenuItem(models.Model):
    '''
    Model for restaurant's default menu items.

    Fields:
    category - Category of item
    name - Name of item
    description - Description of item
    price - Float number of fixed item price
    image- Image for menu item
    '''
    category = models.CharField('Category', max_length=50)
    name = models.CharField('Name', max_length=50)
    description = models.TextField('Description', max_length=150)
    price = models.DecimalField('Price', max_digits=30, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

    def __str__(self):
        return f'{self.name}, {self.price}eur'

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        app_label = 'burger_shop'


class OrderItem(models.Model):
    '''
    Intermediate model to connect order items with order and set quantity.

    Fields:
    order - Many to one realtionship with order (one order can have many order items)
    menu_item - Realtionship to menu item, can be empty if custom_burger is present
    custom_burger - Realtionship to custom burger, can be empty if menu_item is present
    quantity - Integer field to set amount of menu_item or custom_burger
    '''
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, blank=True, null=True)
    custom_burger = models.ForeignKey('CustomBurger', on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField('Quantity')

    @property
    def total_price(self):
        '''
        Property to calculate total price of item. Item can either menu_item or custom_burger, so we use if to determine
        which one we calculating
        :return: Float of total price
        '''
        if self.menu_item:
            return self.menu_item.price * self.quantity
        elif self.custom_burger:
            return self.custom_burger.total_price * self.quantity
        return 0

    @property
    def item_total_nutrition(self):
        '''
        Calculates total nutrition for this item (handles custom burgers and menu items).
        '''
        if self.custom_burger and self.custom_burger.total_nutrition:
            nutrition = self.custom_burger.total_nutrition
            return {
                'calories': nutrition['calories'] * self.quantity,
                'protein': nutrition['protein'] * self.quantity,
                'fat': nutrition['fat'] * self.quantity,
                'carbs': nutrition['carbs'] * self.quantity,
            }
        elif self.menu_item and self.menu_item.nutrition:
            nutrition = self.menu_item.nutrition
            return {
                'calories': nutrition.calories * self.quantity,
                'protein': nutrition.protein * self.quantity,
                'fat': nutrition.fat * self.quantity,
                'carbs': nutrition.carbs * self.quantity,
            }
        return {}


    def __str__(self):
        if self.menu_item:
            return f'{self.menu_item.name} x {self.quantity}'
        elif self.custom_burger:
            return f'{self.custom_burger.name} x {self.quantity}'

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        app_label = 'burger_shop'


class CustomBurger(models.Model):
    '''
    Model of users created custom burgers.

    Fields:
    user - Many to one relationship to user (one user can have many custom burgers)
    name - name of burger
    image - generated image of whole burger( from seperate ingredients images)
    created_at - automatic date field when burger was created ( for sorting purposes )
    '''
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField('Name', max_length=50)
    image = models.ImageField(upload_to='users_burgers', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        '''
        Pulls out ingredients of the burger from the CustomBurgerRecipe relationship.
        :return: Float, sum of all ingredient prices.
        '''
        recipe_items = self.customburgerrecipe_set.all()
        return sum(item.price for item in recipe_items)

    @property
    def average_rating(self):
        '''
        Calculates the average rating of the burger. Pulls ratings from the BurgerReview relationship.
        :return: Range of the rounded average rating. Rounded for the 'stars' system (only full stars).
                 Returns a range to display the correct number of stars.
        '''
        avg_rating = self.burgerreview_set.aggregate(Avg('rating'))['rating__avg']
        return range(round(avg_rating)) if avg_rating else 0

    @property
    def total_nutrition(self):
        '''
        Sums up total nutrition from all ingredients in this custom burger.
        '''
        total = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

        for recipe_item in self.customburgerrecipe_set.all():
            ingredient_nutrition = recipe_item.total_nutrition
            total['calories'] += ingredient_nutrition['calories']
            total['protein'] += ingredient_nutrition['protein']
            total['fat'] += ingredient_nutrition['fat']
            total['carbs'] += ingredient_nutrition['carbs']

        return total


    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Custom Burger'
        verbose_name_plural = 'Custom Burgers'
        app_label = 'burger_shop'


class Ingredient(models.Model):
    """
    Custom burger ingredients model.

    Fields:
    category - category of ingridient
    name - name of ingredient
    description - description of ingredient
    price - fixed price of ingredient
    part_image - ingredient png image used to generate full custom burger image
    """
    category = models.CharField('Category', max_length=50)
    name = models.CharField('Name', max_length=50)
    description = models.CharField('Description', max_length=150)
    price = models.DecimalField('Price', max_digits=30, decimal_places=2)
    part_image = models.ImageField(upload_to='burger_components/', blank=True)

    def __str__(self):
        return f'{self.name}, {self.price}eur'

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        app_label = 'burger_shop'


class CustomBurgerRecipe(models.Model):
    '''
    Intermediate model between CustomBurger and Ingredient, used to determine the amount of each ingredient used.

    Fields:
    custom_burger - ForeignKey: Many-to-One (Each ingredient is linked to a single custom burger, but a burger can have many ingredients).
    ingredient - ForeignKey: Many-to-One (Each ingredient entry is linked to a single ingredient, but one ingredient can appear in many custom burgers).
    quantity - Integer field representing the amount of the ingredient used.
    '''
    custom_burger = models.ForeignKey(CustomBurger, on_delete=models.CASCADE, null=True, blank=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField('Quantity')

    def __str__(self):
        return f'{self.ingredient.name} x {self.quantity}'

    @property
    def price(self):
        '''
        Calculates total price of ingredient
        :return: Float ingredient price times how many used
        '''
        if self.ingredient and self.quantity:
            return self.ingredient.price * self.quantity
        return 0

    @property
    def total_nutrition(self):
        '''
        Calculates total nutrition for this ingredient in the burger (nutrition * quantity).
        '''
        if self.ingredient and self.ingredient.nutrition:
            return {
                'calories': self.ingredient.nutrition.calories * self.quantity,
                'protein': self.ingredient.nutrition.protein * self.quantity,
                'fat': self.ingredient.nutrition.fat * self.quantity,
                'carbs': self.ingredient.nutrition.carbs * self.quantity,
            }
        return {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

    class Meta:
        app_label = 'burger_shop'

class BlogPost(models.Model):
    '''
    Model for writing blog posts

    Fields:
    title - title of post
    content - html field to be able to format and upload youtube videos in blog content
    image - image field used in thumbnail of post
    author - author of post, Many to one relationship(One author can have many posts)
    created_at - automatic date field when post was written
    content_image - image field used to display image under content

    '''
    title = models.CharField(max_length=200)
    content = HTMLField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    class Meta:
        app_label = 'burger_shop'


class BurgerReview(models.Model):
    '''
    Model for leaving review and rating under custom users burgers

    Fields:
    date - automatic date field when review was left
    content - Text field for leaving comments
    burger - Many to one relationship (one burger can have many reviews)
    rating - rating of burger (range from 1 to 5)
    user - One to many relationship (one user can leave many reviews(one per burger))
    '''
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField('Content', max_length=2000)
    burger = models.ForeignKey(CustomBurger, on_delete=models.CASCADE, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.date}, {self.user}, {self.burger}, {self.rating}/5, {self.content}'

    class Meta:
        app_label = 'burger_shop'
