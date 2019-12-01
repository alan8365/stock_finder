from django.db import models


# Create your models here.
class StockRecord(models.Model):
    datetime = models.DateTimeField()

    number = models.CharField(
        max_length=20
    )

    name = models.CharField(
        max_length=20
    )

    buy = models.IntegerField()

    sell = models.IntegerField()

    diff = models.IntegerField()

    class Meta:
        unique_together = ('datetime', 'number')
        abstract = True


class Foreign(StockRecord):

    def __str__(self):
        result = '外資'
        if self.diff > 0:
            result += f'買超{self.diff}'
        else:
            result += f'賣超{self.diff}'


class Investment(StockRecord):

    def __str__(self):
        result = '投信'
        if self.diff > 0:
            result += f'買超{self.diff}'
        else:
            result += f'賣超{self.diff}'
