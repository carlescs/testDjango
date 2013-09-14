from chartit import DataPool, Chart
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils import timezone

from polls.models import Poll, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        """Return the last five published polls."""
        return Poll.objects.annotate(count=Count('choice')).filter(pub_date__lte=timezone.now(), count__gt=1).order_by(
            '-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any polls that aren't published yet.
        """
        return Poll.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        poll_id = context['poll'].pk
        p = get_object_or_404(Poll, pk=poll_id)
        weatherdata = \
            DataPool(
                series=
                [{'options': {
                    'source': p.choice_set},
                  'terms': [
                      'choice_text',
                      'votes']}
                ])
        piechart = Chart(
            datasource=weatherdata,
            series_options=
            [{'options': {
                'type': 'pie'},
              'terms': {
                  'choice_text': [
                      'votes']
              }}],
            chart_options=
            {'title': {
                'text': p.question},
             'xAxis': {
                 'title': {
                     'text': 'Choice'}}})
        context['piechart'] = piechart
        return context


def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))