'''
В этом модуле определены настройки отображения моделей 
приложения в административном интерфейсе Django.
'''
from django.contrib import admin
from .models import Job, Execution

class ExecutionInline(admin.TabularInline):
    model = Execution
    readonly_fields = ("job", "start", "status", "end", "success", "result")
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        '''Объекты запусков нельзя добавлять вручную.'''
        return False

@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели запуска скрипта в панели администрирования Django.
    '''
    model = Execution
    
    list_display = ('job', 'start', 'status', 'end', 'success', 'result')
    list_filter = ('status', 'success')

    readonly_fields = ("job", "start", "status", "end", "success", "result")

    fieldsets = (
        ("Метаданные", {'fields': ["job", "start", "status", "end"]}),
        ("Результат", {"fields": ["success", "result"]}),
    )

    def has_add_permission(self, request, obj=None):
        '''Объекты запусков нельзя добавлять вручную.'''
        return False
    

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели скрипта в панели администрирования Django.
    '''
    model = Job
    
    list_display = ('name', 'description', 'schedule', 'last_run', 'active', 'scheduled', 'manual', 'next_run', 'url')
    list_filter = ('active', 'scheduled', 'manual')

    exclude = ('command',)

    inlines = [
        ExecutionInline,
    ]

