import logging
from search.models import TaskServiceSimilarityScore

LOGGER = logging.getLogger('remove_similarities_for_topics')


def remove_similarities_for_topics(list_of_task_ids):
    for topic_id in list_of_task_ids:
        result = TaskServiceSimilarityScore.objects.filter(task_id=topic_id).delete()
        number_of_records_deleted = result[0]
        if number_of_records_deleted == 0:
            LOGGER.warning('%s: Invalid topic id', topic_id)
