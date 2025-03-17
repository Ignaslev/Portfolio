from django.contrib import admin
from django import forms
from .models import Profile, Order, MenuItem, OrderItem, CustomBurger, Ingredient, CustomBurgerRecipe, BlogPost, BurgerReview, Nutrition


class CustomBurgerRecipeInline(admin.TabularInline):
    '''
    Allows adding and editing burger ingredients directly in the CustomBurger admin panel.
    '''
    model = CustomBurgerRecipe
    extra = 1

class CustomBurgerAdmin(admin.ModelAdmin):
    '''
    Displays burger name, ID, user, and total price in the list view.
    Allows inline editing of associated CustomBurgerRecipe items.
    '''
    list_display = ('name', 'id', 'user', 'total_price', )
    inlines = [CustomBurgerRecipeInline]


class OrderItemInline(admin.TabularInline):
    '''
    Allows adding and editing order items directly in the Order admin panel.
    '''
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    '''
    Displays order ID, user, total price, order status, and timestamp in the list view.
    Allows inline editing of associated OrderItem entries.
    '''
    list_display = ('id', 'time', 'user', 'total_price', 'order_status')
    list_filter = ('time', 'user')
    list_editable = ('order_status',)
    inlines = [OrderItemInline]

class NutritionInline(admin.TabularInline):
    '''
    Allows adding and editing nutrition for ingredients and menu items in admin panel.
    '''
    model = Nutrition
    can_delete = False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'ingredient':
            # Hide the field if editing a MenuItem
            if 'menuitem' in request.path:
                kwargs['widget'] = forms.HiddenInput()
            # Automatically assign the ingredient id
            if 'ingredient' in request.path:
                kwargs['required'] = False

        if db_field.name == 'menu_item':
            # Hide the field if editing an Ingredient
            if 'ingredient' in request.path:
                kwargs['widget'] = forms.HiddenInput()
            # Automatically assign the menu item id
            if 'menuitem' in request.path:
                kwargs['required'] = False

        return super().formfield_for_foreignkey(db_field, request, **kwargs)



class IngredientAdmin(admin.ModelAdmin):
    '''
    Displays ingredient name, category, and price in the list view.
    Allows price editing and filtering by category.
    '''
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    list_editable = ('price',)
    inlines = [NutritionInline]


class MenuItemAdmin(admin.ModelAdmin):
    '''
    Displays menu item name, category, and price in the list view.
    Allows price editing and filtering by category.
    '''
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    list_editable = ('price',)
    inlines = [NutritionInline]


class BurgerReviewAdmin(admin.ModelAdmin):
    '''
    Displays burger, user, and rating in the list view.
    Allows filtering by user and burger.
    '''
    list_display = ('burger', 'user', 'rating')
    list_filter = ('user', 'burger')

class ProfileAdmin(admin.ModelAdmin):
    '''
    Displays user ID, first name, last name, and user in the list view.
    Custom methods retrieve related user attributes.
    '''
    def user_id(self, profile):
        return profile.user.id

    def user_name(self, profile):
        return profile.user.first_name

    def user_lname(self, profile):
        return profile.user.last_name

    list_display = ('user_id', 'user_name', 'user_lname', 'user')


class BlogPostAdmin(admin.ModelAdmin):
    '''
    Displays blog post title, creation date, and author in the list view.
    '''
    list_display = ('title', 'created_at', 'author')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(CustomBurger,CustomBurgerAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BurgerReview,BurgerReviewAdmin)
