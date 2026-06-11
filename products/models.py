

# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)

#     def __str__(self):
#         return self.name

# # class Product(models.Model):
# #     name = models.CharField(max_length=200)
# #     price = models.DecimalField(max_digits=10, decimal_places=2)
# #     category = models.ForeignKey(Category, on_delete=models.CASCADE)
# #     is_active = models.BooleanField(default=True)
# #     available = models.BooleanField(default=True)

# #     def __str__(self):
# #         return self.name

# class Favorite(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # используем AUTH_USER_MODEL
#         on_delete=models.CASCADE
#     )
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'product')

#     def __str__(self):
#         return f'{self.user.username} - {self.product.name}'

# class Cart(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # используем AUTH_USER_MODEL
#         on_delete=models.CASCADE
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Корзина пользователя {self.user.username}"


from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=200)
    #slug = models.SlugField(unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True) 
    description = models.TextField(blank=True, null=True)
    specifications = models.TextField(
    verbose_name="Характеристики продукта",
    blank=True,
    help_text="Укажите характеристики в формате 'Параметр: значение' через новую строку"
    )
    image = models.ImageField(
    upload_to='products/',
    blank=True,   # форма Django может оставить поле пустым
    null=True    # в базе данных поле может быть NULL
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='products'
    )
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # ... другие поля ...
    available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    def get_specifications_dict(self):
        """
        Парсит поле specifications и возвращает словарь.
        Пример: "Вес: 2 кг\nЦвет: Чёрный" → {'Вес': '2 кг', 'Цвет': 'Чёрный'}
        """
        if not self.specifications:
            return {}

        specs = {}
        lines = self.specifications.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)  # Разделяем только по первому двоеточию
                specs[key.strip()] = value.strip()
        return specs



class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products_carts'  # уникальное имя
    )

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

# class Favorite(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='favorites'
#     )
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'product')

#     def __str__(self):
#         return f"{self.user.username} - {self.product.name}"



