from django.db import models
from services.utils import SESSION_MAP


class SessionType(models.TextChoices):
    FP1 = 'fp1', 'FP1'
    FP2 = 'fp2', 'FP2'
    FP3 = 'fp3', 'FP3'
    SPRINT_QUALIFYING = 'sprint_qualifying', 'Sprint Qualifying'
    SPRINT = 'sprint', 'Sprint'
    QUALIFYING = 'qualifying', 'Qualifying'
    RACE = 'race', 'Race'


class Constructor(models.Model):
    ref = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Driver(models.Model):
    ref = models.CharField(max_length=50, unique=True)
    number = models.PositiveIntegerField(null=True, blank=True)
    code = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=50)
    flag = models.CharField(max_length=10, default='', blank=True)
    is_primary = models.BooleanField(default=False, db_index=True)
    birth_date = models.DateField(null=True, blank=True)
    team = models.ForeignKey('Constructor', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='drivers')

    def __str__(self):
        team_name = self.team.name if self.team else 'Нет команды'
        return f'{self.first_name} {self.last_name} ({team_name})'


class Circuit(models.Model):
    ref = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.country})"
    

class GrandPrix(models.Model):
    name = models.CharField(max_length=200)
    circuit = models.ForeignKey('Circuit', on_delete=models.CASCADE)
    round = models.IntegerField()
    date = models.DateField()
    year = models.IntegerField()
    has_sprint = models.BooleanField(default=False)

    fp1_datetime = models.DateTimeField(null=True, blank=True)
    fp2_datetime = models.DateTimeField(null=True, blank=True)
    fp3_datetime = models.DateTimeField(null=True, blank=True)
    sprint_qualifying_datetime = models.DateTimeField(null=True, blank=True)
    sprint_datetime = models.DateTimeField(null=True, blank=True)
    qualifying_datetime = models.DateTimeField(null=True, blank=True)
    race_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['year', 'round']
        verbose_name = 'Гран-при'
        verbose_name_plural = 'Гран-при'

        indexes = [
            models.Index(fields=['year', 'round']),
        ]

    def __str__(self):
        if self.has_sprint:
            return f"{self.round}. {self.name} ({self.circuit.name}) - спринт"
        else:
            return f"{self.round}. {self.name} ({self.circuit.name})"
        

class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    notifications_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']


class NotificationLog(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    race = models.ForeignKey('GrandPrix', on_delete=models.CASCADE)
    session_type = models.CharField(max_length=30, choices=SessionType.choices)
    reminder_time = models.PositiveSmallIntegerField(default=60)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'race', 'session_type', 'reminder_time']


class UserSessionSubscription(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='subscriptions')
    session_type = models.CharField(max_length=30, choices=SessionType.choices)
    reminder_time = models.PositiveIntegerField(
        choices=[
            (120, '120 минут'),
            (60, '60 минут'),
            (30, '30 минут'),
            (20, '20 минут'),
            (15, '15 минут'),
            (10, '10 минут'),
        ]
    )

    class Meta:
        unique_together = [('user', 'session_type', 'reminder_time')]
        indexes = [
            models.Index(fields=['session_type']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.session_type} ({self.reminder_time})"