from django.shortcuts import render
from .simulate import Simulate
from django.urls import reverse
from django.http import HttpResponseRedirect
from celery import task
from celery.result import AsyncResult


# Create your views here.

class App:
    def __init__(self):
        self.sim = None

    def sumilate(self, request):
        if request.method == "POST":
            try:
                comm_size = int(request.POST['commsize'])
                print(comm_size)
                self.sim = Simulate(comm_size)
                self.sim.run_simulation(20)
                return HttpResponseRedirect(reverse('sim:res'))
            except ValueError:
                return render(request, 'simulate/home.html', {
                    'error_title': "Invalid entry",
                    "error_content": "Please enter a numerical number between 1 and 10,000,000. With no punctuation",
                })
        else:
            return render(request, 'simulate/home.html')

    def results(self, request):
        return render(request, 'simulate/results.html', {
            'population': len(self.sim.peeps),
            'outer_cs': len(self.sim.outer_circles)
        })


# this decorator is all that's needed to tell celery this is a worker task
@task
def do_work(self, list_of_work, progress_observer):
    total_work_to_do = len(list_of_work)
    for i, work_item in enumerate(list_of_work):
        do_work_item(work_item)
        # tell the progress observer how many out of the total items we have processed
        progress_observer.set_progress(i, total_work_to_do)
    return 'work is complete'


def my_view(request):
    # the .delay() call here is all that's needed
    # to convert the function to be called asynchronously
    do_work.delay()
    # we can't say 'work done' here anymore because all we did was kick it off
    return HttpResponse('work kicked off!')