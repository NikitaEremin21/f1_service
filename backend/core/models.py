from django.db import models


class Constructor(models.Model):
    ref = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Driver(models.Model):
    ref = models.CharField(max_length=50, unique=True)
    number = models.PositiveIntegerField()
    code = models.CharField(max_length=3)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    team = models.ForeignKey('Constructor', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='drivers')

    def __str__(self):
        team_name = self.team.name if self.team else 'Нет команды'
        return f'{self.first_name} {self.last_name} ({team_name})'
