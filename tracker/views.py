from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import timedelta, datetime
from db_app.models import MOMENT_OF_DAY_CHOICES, MealLog, FavouriteProduct, ShoppingProduct, Product, Recipe, RecipeDetail, DayExtraStat
from .forms import AddMealLogForm, UpdateMealLogForm, AddProductForm, AddShoppingProductForm, UpdateDayExtraStat
from calculators.calories_calculator import calculate_nutritions
from calculators.water_calculator import water_calculate

class Nutritions:
    def __init__(self) -> None:
        self.calories = 0
        self.proteins = 0
        self.fats = 0
        self.carbons = 0

class CalculatedNutritions:
    def __init__(self) -> None:
        self.breakfast = Nutritions()
        self.brunch = Nutritions()
        self.lunch = Nutritions()
        self.snack = Nutritions()
        self.dinner = Nutritions()
        self.all_nutritions = Nutritions()
    
    def round_values(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, Nutritions):
                attr.calories = round(attr.calories, 1)
                attr.proteins = round(attr.proteins, 2)
                attr.fats = round(attr.fats, 2)
                attr.carbons = round(attr.carbons, 2)

@login_required
def calculate_daily_stats(request, burned_calories):
    person = request.user.profile
    person_data = calculate_nutritions(person.weight, person.height, person.age, person.gender, person.activity_level)
    new_person_data = (person_data[0]+burned_calories,) + person_data[1:]
    return new_person_data

def update_nutritions(calculated_nutritions, meal_logs):
    for next in meal_logs:
        product = next.product
        calories = product.calories * ( next.amount / product.portion )
        proteins = product.proteins * ( next.amount / product.portion )
        fats = product.fats * ( next.amount / product.portion )
        carbons = product.carbons * ( next.amount / product.portion )
        match (next.moment_of_day):
            case "BREAKFAST":
                calculated_nutritions.breakfast.calories += calories
                calculated_nutritions.breakfast.proteins += proteins
                calculated_nutritions.breakfast.fats += fats
                calculated_nutritions.breakfast.carbons += carbons
                
            case "BRUNCH":
                calculated_nutritions.brunch.calories += calories
                calculated_nutritions.brunch.proteins += proteins
                calculated_nutritions.brunch.fats += fats
                calculated_nutritions.brunch.carbons += carbons
                
            case "LUNCH":
                calculated_nutritions.lunch.calories += calories
                calculated_nutritions.lunch.proteins += proteins
                calculated_nutritions.lunch.fats += fats
                calculated_nutritions.lunch.carbons += carbons
                
            case "SNACK":
                calculated_nutritions.snack.calories += calories
                calculated_nutritions.snack.proteins += proteins
                calculated_nutritions.snack.fats += fats
                calculated_nutritions.snack.carbons += carbons
                
            case "DINNER":
                calculated_nutritions.dinner.calories += calories
                calculated_nutritions.dinner.proteins += proteins
                calculated_nutritions.dinner.fats += fats
                calculated_nutritions.dinner.carbons += carbons
            case _ :
                raise Exception("error with adding nutritions")

        calculated_nutritions.all_nutritions.calories += calories
        calculated_nutritions.all_nutritions.proteins += proteins
        calculated_nutritions.all_nutritions.fats += fats
        calculated_nutritions.all_nutritions.carbons += carbons

        calculated_nutritions.round_values()

def water_and_training(user, date):
    extra_info = DayExtraStat.objects.filter(user=user, date = date)
    print(extra_info)
    if not extra_info.exists():
        DayExtraStat.objects.create(user=user, date=date)
        return 0, 0
    else:
        extra_info = DayExtraStat.objects.get(user=user, date=date)
        return extra_info.water, extra_info.training

def home(request, date=timezone.now().date()):
    if not request.user.is_authenticated:
        return render(request, 'home.html')
    
    print(type(date))
    user=request.user.profile
    meal_logs = MealLog.objects.filter(user=user, date = date)
    calculated_nutritions = CalculatedNutritions()
    water, burned_calories = water_and_training(user, date)
    daily_needs = calculate_daily_stats(request, burned_calories)
    max_water = water_calculate(user.age, user.gender)
    update_nutritions(calculated_nutritions, meal_logs)

    context = {'moment_of_day_choices': MOMENT_OF_DAY_CHOICES,
                'meal_logs': meal_logs,
                'daily_needs': daily_needs,
                'calculated_nutritions': calculated_nutritions,
                'date': date,
                'previous_date': date-timedelta(days=1),
                'next_date': date+timedelta(days=1),
                'date': date,
                'burned_calories': burned_calories,
                'water': water,
                "max_water": max_water}
    
    return render(request, 'home.html', context)

def home_history(request, date):
    if date.endswith('favicon.ico'):
        return HttpResponse(status=204)
    if date == 'add_product':
        return add_product(request)
    if date == 'shopping_list':
        return shopping_list(request)
    if date == 'product_list':
        return product_list(request)
    if date == 'recipe_list':
        return recipe_list(request)
    # if date == 'update_extra':
    #     return update_extra(request)
    date_format = "%Y-%m-%d"
    date = datetime.strptime(date.split(' ')[0], date_format).date()
    print(date)
    return home(request, date)


@login_required
def update_meal_log(request, meal_log_id):
    meal_log = MealLog.objects.get(id=meal_log_id)
    if request.method == "POST":
        form = UpdateMealLogForm(request.POST, instance=meal_log)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UpdateMealLogForm(instance=meal_log)
        return render(request, "update_meal_log.html", {"form": form, "meal_log": meal_log})
    
@login_required
def delete_meal_log(request, meal_log_id):
    print(meal_log_id)
    MealLog.objects.filter(id=meal_log_id).delete()
    return redirect('home')

@login_required
def add_favourite_product(request, meal_log_id):
    product = MealLog.objects.get(id=meal_log_id).product
    user = request.user.profile
    if FavouriteProduct.objects.filter(user=user, product=product).exists():
        return redirect('home')
    FavouriteProduct.objects.create(user=user, product=product)
    return redirect('home')

@login_required
def delete_favourite_product(request, product_id):
    product = Product.objects.get(id=product_id)
    favourite_product = FavouriteProduct.objects.get(user=request.user.profile, product=product)
    favourite_product.delete()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            product.save()
            return redirect('add_product')
        return render(request, 'add_product.html', {"form": form})
    else:
        form = AddProductForm()
        return render(request, 'add_product.html', {"form": form})
    
@login_required
def shopping_list(request):
    # Get the current user's shopping products
    shopping_products = ShoppingProduct.objects.filter(user=request.user.profile)

    if request.method == 'POST':
        form = AddShoppingProductForm(request.POST)
        action = request.POST['action']
        if action == 'delete':
            product_ids = request.POST.getlist('product_ids[]')
            ShoppingProduct.objects.filter(id__in=product_ids).delete()
            return redirect('shopping_list')
        if form.is_valid():
            shopping_product = form.save(commit=False)
            shopping_product.user = request.user.profile
            shopping_product.save()
            return redirect('shopping_list')
    else:
        form = AddShoppingProductForm()

    context = {
        'shopping_products': shopping_products,
        'form': form
    }
    return render(request, 'shopping_list.html', context)

@login_required
def add_meal_log(request, moment_of_day):
    query = request.GET.get('search')
    min_calories = request.GET.get('min_calories')
    max_calories = request.GET.get('max_calories')
    min_proteins = request.GET.get('min_proteins')
    max_proteins = request.GET.get('max_proteins')
    min_fats = request.GET.get('min_fats')
    max_fats = request.GET.get('max_fats')
    min_carbons = request.GET.get('min_carbons')
    max_carbons = request.GET.get('max_carbons')

    user = request.user.profile
    favourite_products = Product.objects.filter(favouriteproduct__user = user)
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)
        favourite_products = favourite_products.filter(name__icontains=query)

    if min_calories:
        products = products.filter(calories__gte=min_calories)
        favourite_products = favourite_products.filter(calories__gte=min_calories)
    if max_calories:
        products = products.filter(calories__lte=max_calories)
        favourite_products = favourite_products.filter(calories__lte=max_calories)

    if min_proteins:
        products = products.filter(proteins__gte=min_proteins)
        favourite_products = favourite_products.filter(proteins__gte=min_proteins)
    if max_proteins:
        products = products.filter(proteins__lte=max_proteins)
        favourite_products = favourite_products.filter(proteins__lte=max_proteins)

    if min_fats:
        products = products.filter(fats__gte=min_fats)
        favourite_products = favourite_products.filter(fats__gte=min_fats)
    if max_fats:
        products = products.filter(fats__lte=max_fats)
        favourite_products = favourite_products.filter(fats__lte=max_fats)

    if min_carbons:
        products = products.filter(carbons__gte=min_carbons)
        favourite_products = favourite_products.filter(carbons__gte=min_carbons)
    if max_carbons:
        products = products.filter(carbons__lte=max_carbons)
        favourite_products = favourite_products.filter(carbons__lte=max_carbons)


    if request.method == "POST":
        form = AddMealLogForm(request.POST)
        print(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user.profile
            meal.save()
            return redirect('home')
        else:
            return render(request, 'add_meal_log.html', {"form": form, "moment_of_day": moment_of_day, "products": products, 'favourite_products': favourite_products})
    else:
        form = AddMealLogForm()
        form.fields['moment_of_day'].initial = moment_of_day
        form.fields['date'].initial = timezone.now().date()
        return render(request, 'add_meal_log.html', {"form": form, "moment_of_day": moment_of_day, "products": products, 'favourite_products': favourite_products})


@login_required
def product_list(request):
    query = request.GET.get('search')
    min_calories = request.GET.get('min_calories')
    max_calories = request.GET.get('max_calories')
    min_proteins = request.GET.get('min_proteins')
    max_proteins = request.GET.get('max_proteins')
    min_fats = request.GET.get('min_fats')
    max_fats = request.GET.get('max_fats')
    min_carbons = request.GET.get('min_carbons')
    max_carbons = request.GET.get('max_carbons')

    user = request.user.profile
    favourite_products = Product.objects.filter(favouriteproduct__user = user)

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)
        favourite_products = favourite_products.filter(name__icontains=query)

    if min_calories:
        products = products.filter(calories__gte=min_calories)
        favourite_products = favourite_products.filter(calories__gte=min_calories)
    if max_calories:
        products = products.filter(calories__lte=max_calories)
        favourite_products = favourite_products.filter(calories__lte=max_calories)

    if min_proteins:
        products = products.filter(proteins__gte=min_proteins)
        favourite_products = favourite_products.filter(proteins__gte=min_proteins)
    if max_proteins:
        products = products.filter(proteins__lte=max_proteins)
        favourite_products = favourite_products.filter(proteins__lte=max_proteins)

    if min_fats:
        products = products.filter(fats__gte=min_fats)
        favourite_products = favourite_products.filter(fats__gte=min_fats)
    if max_fats:
        products = products.filter(fats__lte=max_fats)
        favourite_products = favourite_products.filter(fats__lte=max_fats)

    if min_carbons:
        products = products.filter(carbons__gte=min_carbons)
        favourite_products = favourite_products.filter(carbons__gte=min_carbons)
    if max_carbons:
        products = products.filter(carbons__lte=max_carbons)
        favourite_products = favourite_products.filter(carbons__lte=max_carbons)

    return render(request, 'product_list.html', {'products': products,
                                                 'favourite_products': favourite_products})

@login_required
def recipe_list(request):
    recipes = Recipe.objects.all()
    products = Product.objects.all()
    if request.method == "POST":
        recipe_name = request.POST.get('recipe_name')
        recipe_description = request.POST.get('recipe_description')
        recipe = Recipe.objects.create(name=recipe_name, description=recipe_description)

        product_ids = request.POST.getlist('product_ids[]')
        amounts = request.POST.getlist('amounts[]')
        for product_id, amount in zip(product_ids, amounts):
            product = Product.objects.get(pk=product_id)
            if not amount:
                amount = -1
            RecipeDetail.objects.create(recipe=recipe, product=product, amount=amount)
        
        return redirect('recipe_list')

    return render(request, 'recipe_list.html', {'recipes': recipes, 'products': products})

@login_required
def update_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    products = Product.objects.all()
    recipe_details = RecipeDetail.objects.filter(recipe = recipe)
    if request.method == "POST":
        recipe.name = request.POST.get('recipe_name')
        recipe.description = request.POST.get('recipe_description')
        recipe.save()
        recipe_details.delete()

        product_ids = request.POST.getlist('product_ids[]')
        amounts = request.POST.getlist('amounts[]')
        for product_id, amount in zip(product_ids, amounts):
            product = Product.objects.get(pk=product_id)
            if not amount:
                amount = -1
            RecipeDetail.objects.create(recipe=recipe, product=product, amount=amount)
        return redirect('recipe_list')
    else:
        return render(request, "update_recipe.html", {"products": products, "recipe": recipe, "recipe_details": recipe_details})


@login_required
def recipe_details(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_details = RecipeDetail.objects.filter(recipe = recipe)
    return render(request, 'recipe_details.html', {'recipe': recipe,
        'recipe_details': recipe_details})

@login_required
def delete_recipe(request, recipe_id):
    print("gowno")
    Recipe.objects.filter(id=recipe_id).delete()
    return redirect('recipe_list')

@login_required
def update_extra(request, date):
    stat = DayExtraStat.objects.get(user=request.user.profile, date=date)
    if request.method == "POST":
        form = UpdateDayExtraStat(request.POST, instance=stat)
        if form.is_valid():
            form.save()
            return redirect("/" + date)
    else:
        form = UpdateDayExtraStat(instance=stat)
        return render(request, 'update_dayextrastat.html', {"form": form, "stat": stat, "date": date})