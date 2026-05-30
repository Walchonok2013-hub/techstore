from django.db import models
#from django.contrib.auth.models import User

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
        Category,
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
