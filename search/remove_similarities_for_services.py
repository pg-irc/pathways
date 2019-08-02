import logging
from search.models import TaskServiceSimilarityScore

LOGGER = logging.getLogger('remove_similarities_for_services')


def remove_similarities_for_services(list_of_service_ids):
    for service_id in list_of_service_ids:
        result = TaskServiceSimilarityScore.objects.filter(service_id=service_id).delete()
        number_of_records_deleted = result[0]
        if number_of_records_deleted == 0:
            LOGGER.warning('%s: Invalid service id', service_id)
