from django.core.management.base import BaseCommand
from search.models import Task, TaskServiceSimilarityScore, TaskSimilarityScore


class Command(BaseCommand):
    help = ('Remove all topics, all similarity scores between topics, and all similarity scores between '
            'topics and services')

    def handle(self, *args, **options):

        print('All topic data and topic/service similarity data will be deleted')

        TaskSimilarityScore.objects.all().delete()
        TaskServiceSimilarityScore.objects.all().delete()
        Task.objects.all().delete()
