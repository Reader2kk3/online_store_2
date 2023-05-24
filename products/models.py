import uuid

from django.db import models

from users.models import User


class ProductCategory(models.Model):
    name = models.CharField("Название", max_length=128, unique=True)
    discription = models.TextField("Описание", max_length=2500, null=True, blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["-name", ]

    def __str__(self):
        return str(self.name)
        
class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    discription = models.TextField("Описание", max_length=2500, null=True, blank=True)
    price = models.DecimalField("Цена", max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField("Количество", default=0)
    image = models.ImageField("Изображение", upload_to='media/%Y/%m/%d/')
    category = models.ForeignKey(on_delete=models.CASCADE, to=ProductCategory, verbose_name='Категория')
    data = models.DateTimeField("Дата создания", auto_now_add=True)
    up_data = models.DateTimeField("Дата редактирования", auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["-data", "up_data"]

    def __str__(self):
        return f'Продукт: {self.name} | Категория: {self.category}'


class BasketQuerySet(models.QuerySet):

    def  total_sum(self):
        return sum(basket.sum() for basket in self)

    def  total_quantity(self):
        return sum(basket.quantity for basket in self)


class Basket(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Владелец")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveSmallIntegerField("Количество", default=0)
    created_timestamp = models.DateTimeField("Дата создания", auto_now_add=True)

    objects = BasketQuerySet.as_manager()

    def __str__(self):
        return f'Корзина для: {self.user.username} | Продукт: {self.product.name}'

    def sum(self):
        return self.product.price * self.quantity

    def de_json(self):
        basket_item = {
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': float(self.product.price),
            'sum': float(self.sum()),
        }
        return basket_item

    @classmethod
    def create_or_update(cls, product_id, user):
        baskets = Basket.objects.filter(user=user, product_id=product_id)

        if not baskets.exists():
            obj = Basket.objects.create(user=user, product_id=product_id, quantity=1)
            is_created = True
            return obj, is_created
        else:
            basket = baskets.first()
            basket.quantity += 1
            basket.save()
            is_crated = False
            return basket, is_crated
