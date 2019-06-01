from human_services.services import models
from human_services.locations.models import ServiceAtLocation
from common.testhelpers.random_test_values import a_string
from newcomers_guide.tests.helpers import create_topics
from search.models import TaskServiceSimilarityScore

def create_related_topic(service_id, similarity_score):
    topic_id = a_string()
    create_topics([topic_id])
    TaskServiceSimilarityScore.objects.create(
        task_id=topic_id,
        service_id=service_id,
        similarity_score=similarity_score
    )
    return topic_id

class ServiceBuilder:
    def __init__(self, organization):
        self.service_id = a_string()
        self.organization = organization
        self.name = a_string()
        self.description = a_string()
        self.taxonomy_terms = []
        self.location_ids = []

    def with_id(self, service_id):
        self.service_id = service_id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_description(self, description):
        self.description = description
        return self

    def with_taxonomy_terms(self, taxonomy_terms):
        self.taxonomy_terms = taxonomy_terms
        return self

    def with_location(self, location):
        self.location_ids.append(location.id)
        return self

    def build(self):
        result = models.Service()
        result.id = self.service_id
        result.name = self.name
        result.organization = self.organization
        result.description = self.description
        for taxonomy_term in self.taxonomy_terms:
            result.taxonomy_terms.add(taxonomy_term)

        return result

    def create(self):
        result = self.build()
        result.save()
        for location_id in self.location_ids:
            ServiceAtLocation.objects.create(service_id=result.id, location_id=location_id)
        return result
