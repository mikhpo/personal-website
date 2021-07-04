from django.contrib import admin
from .models import Script, Run

class RunInline(admin.TabularInline):
    model = Run
    readonly_fields = ("script", "start", "status", "end", "success", "result", "log")
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        '''Объекты запусков нельзя добавлять вручную.'''
        return False

@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели запуска скрипта в панели администрирования Django.
    '''
    model = Run
    
    list_display = ('script', 'start', 'status', 'end', 'success', 'result')
    list_filter = ('status', 'success')

    readonly_fields = ("script", "start", "status", "end", "success", "result", "log")

    fieldsets = (
        ("Метаданные", {'fields': ["script", "start", "status", "end"]}),
        ("Результат", {"fields": ["success", "result", "log"]}),
    )

    def has_add_permission(self, request, obj=None):
        '''Объекты запусков нельзя добавлять вручную.'''
        return False
    

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели скрипта в панели администрирования Django.
    '''
    model = Script
    
    list_display = ('name', 'description', 'schedule', 'active', 'run_script')
    list_filter = ('active', )

    inlines = [
        RunInline,
    ]

