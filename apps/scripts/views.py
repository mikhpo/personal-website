from loguru import logger
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Job, Execution

@logger.catch
@staff_member_required
def command(request, slug):
    '''
    Принимает на вход слаг, соответствующий одной и команд.
    Запускает административную команду, которая соответствует данному слагу.
    Не дожидается окончания выполнения команды.
    '''
    job = Job.objects.get(slug = slug)
    job.run()
    script = job.name
    result = f'Запущено выполнение скрипта "{script}"'
    messages.add_message(request, messages.SUCCESS, result)
    logger.info(result)
    return redirect("scripts:executions")
    
@logger.catch
@staff_member_required
def jobs(request):
    '''Отображает список всех доступных скриптов и их описание.'''
    jobs = Job.objects.filter(active = True).order_by('-last_run')
    return render(
        request,
        'scripts/jobs.html',
        {'jobs': jobs}
    )

@logger.catch
@staff_member_required
def executions(request):
    '''Отображает список всех выполнений всех скриптов.'''
    executions = Execution.objects.all().order_by('-start')
    return render(
        request,
        'scripts/executions.html',
        {'executions': executions}
    )

@logger.catch
@staff_member_required
def job_detail(request, pk):
    '''Отображает детализированный вид скрипта и историю его выполнений.'''
    job = Job.objects.get(pk = pk)
    executions = Execution.objects.filter(job = job.pk)
    return render(
        request,
        'scripts/job_detail.html',
        {
            'job': job,
            'executions': executions
        }
    )
