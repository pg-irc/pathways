from human_services.locations.models import ServiceAtLocation
from human_services.services.tests.helpers import ServiceBuilder
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.locations.tests.helpers import LocationBuilder
from human_services.locations.models import ServiceAtLocation
from search.models import TaskServiceSimilarityScore


class ServiceAtLocationBuilder:
    def create_many(self, count=3):
        organization = OrganizationBuilder().create()
        return ([ServiceAtLocation.objects.create(
                 location=LocationBuilder(organization).create(),
                 service=ServiceBuilder(organization).create())
                 for _ in range(0, count)])

    def create(self):
        organization = OrganizationBuilder().create()
        return (ServiceAtLocation.objects.create(
            location=LocationBuilder(organization).create(),
            service=ServiceBuilder(organization).create()))


def set_service_similarity_score(topic_id, service_id, similarity_score):
    TaskServiceSimilarityScore.objects.create(
        task_id=topic_id,
        service_id=service_id,
        similarity_score=similarity_score
    )


def set_location_for_service(service_id, location_id):
    return ServiceAtLocation.objects.create(service_id=service_id, location_id=location_id)
