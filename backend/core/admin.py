from django.contrib import admin
from .models import Constructor, Driver, Circuit, GrandPrix


@admin.register(Constructor)
class ConstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'nationality', 'ref', 'full_name')
    search_fields = ('name', 'ref')
    list_filter = ('nationality',)
    fields = ('name', 'ref', 'nationality', 'full_name')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'team', 'number',
                    'code', 'nationality', 'ref', 'age', 'birth_date',)
    search_fields = ('first_name', 'last_name', 'team', 'ref')
    list_filter = ('team', 'nationality', 'birth_date',)
    fields = ('first_name', 'last_name', 'team', 'number', 
              'code', 'nationality', 'ref', 'birth_date',)
    list_select_related = ('team',)
    autocomplete_fields = ('team',)

    def age(self, obj):
        """Вычисление возраста"""
        from datetime import date
        if obj.birth_date:
            today = date.today()
            age = today.year - obj.birth_date.year
            if today.month < obj.birth_date.month or \
               (today.month == obj.birth_date.month and today.day < obj.birth_date.day):
                age -= 1
            return f"{age} лет"
        return "—"
    age.short_description = 'Возраст'


@admin.register(Circuit)
class CircuitAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'country', 'full_name', 'ref',)
    search_fields = ('name', 'location', 'country', 'full_name', 'ref')
    list_filter = ('country',)
    fields = ('ref', 'name', 'location', 'country', 'full_name',)


@admin.register(GrandPrix)
class GrandPrixAdmin(admin.ModelAdmin):
    list_display = ('round', 'name', 'circuit', 'date', 'has_sprint',)
    list_display_links = ('name',)
    search_fields = ('name', 'round', 'circuit',)
    list_filter = ('has_sprint', 'date',)
    fields = ('round', 'name', 'circuit', 'date', 'has_sprint',)

admin.site.site_header = "F1 Service Administration"
admin.site.site_title = "Панель администратора"
admin.site.index_title = "F1 service"
