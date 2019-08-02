import logging
from django.test import TestCase
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from search.save_similarities import (save_topic_similarities,
                                      save_topic_service_similarity_scores,
                                      save_manual_similarities)
from search.remove_similarities_for_topics import remove_similarities_for_topics
from search.remove_similarities_for_services import remove_similarities_for_services
from search.models import Task, TaskSimilarityScore, TaskServiceSimilarityScore
from common.testhelpers.random_test_values import a_string, a_float
from newcomers_guide.tests.helpers import create_topic
import scipy
from search.tests.helpers import create_square_matrix_of_unique_floats


def create_topics(ids):
    for the_id in ids:
        create_topic(the_id)


class TestSavingTaskSimilarities(TestCase):

    def test_deletes_existing_records(self):
        first_topic_id = a_string()
        second_topic_id = a_string()
        create_topics([first_topic_id, second_topic_id])
        record = TaskSimilarityScore(first_task_id=first_topic_id,
                                     second_task_id=second_topic_id,
                                     similarity_score=a_float())
        record.save()

        save_topic_similarities([], [], 0)

        self.assertEqual(TaskSimilarityScore.objects.count(), 0)

    def test_saves_required_number_of_records_for_each_row(self):
        ids = [a_string() for i in range(5)]
        create_topics(ids)
        scores = create_square_matrix_of_unique_floats(5)
        scores_matrix = scipy.sparse.csr_matrix(scores)

        scores_to_save_per_row = 2
        save_topic_similarities(ids, scores_matrix, scores_to_save_per_row)

        scores_saved_in_all = 5 * 2
        self.assertEqual(TaskSimilarityScore.objects.count(), scores_saved_in_all)

    def test_saves_all_off_diagonal_scores_if_number_of_scores_to_save_is_large(self):
        ids = [a_string() for i in range(5)]
        create_topics(ids)
        scores = scipy.sparse.csr_matrix([[a_float() for i in range(5)] for j in range(5)])

        too_many_records_to_save = 2000
        save_topic_similarities(ids, scores, too_many_records_to_save)

        number_of_off_diagonal_elements = 5 * 4
        self.assertEqual(TaskSimilarityScore.objects.count(), number_of_off_diagonal_elements)

    def test_saves_two_non_diagonal_elements_with_the_highest_scores_in_each_row(self):
        ids = [a_string() for i in range(4)]
        create_topics(ids)
        scores = scipy.sparse.csr_matrix([[1, 2, 3, 4],
                                          [5, 6, 7, 8],
                                          [9, 10, 11, 12],
                                          [13, 14, 15, 16]])

        records_to_save_per_row = 2
        save_topic_similarities(ids, scores, records_to_save_per_row)

        records = TaskSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].similarity_score, 3.0)
        self.assertEqual(records[1].similarity_score, 4.0)
        self.assertEqual(records[2].similarity_score, 7.0)
        self.assertEqual(records[3].similarity_score, 8.0)
        self.assertEqual(records[4].similarity_score, 10.0)
        self.assertEqual(records[5].similarity_score, 12.0)
        self.assertEqual(records[6].similarity_score, 14.0)
        self.assertEqual(records[7].similarity_score, 15.0)

    def test_saves_elements_with_first_topic_id(self):
        ids = [a_string() for i in range(4)]
        create_topics(ids)
        scores = scipy.sparse.csr_matrix([[1, 2, 3, 4],
                                          [5, 6, 7, 8],
                                          [9, 10, 11, 12],
                                          [13, 14, 15, 16]])

        records_to_save_per_row = 2
        save_topic_similarities(ids, scores, records_to_save_per_row)

        records = TaskSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].first_task_id, ids[0])
        self.assertEqual(records[1].first_task_id, ids[0])
        self.assertEqual(records[2].first_task_id, ids[1])
        self.assertEqual(records[3].first_task_id, ids[1])
        self.assertEqual(records[4].first_task_id, ids[2])
        self.assertEqual(records[5].first_task_id, ids[2])
        self.assertEqual(records[6].first_task_id, ids[3])
        self.assertEqual(records[7].first_task_id, ids[3])

    def test_saves_elements_with_second_topic_id(self):
        ids = [a_string() for i in range(4)]
        create_topics(ids)
        scores = scipy.sparse.csr_matrix([[1, 2, 3, 4],
                                          [5, 6, 7, 8],
                                          [9, 10, 11, 12],
                                          [13, 14, 15, 16]])

        records_to_save_per_row = 2
        save_topic_similarities(ids, scores, records_to_save_per_row)

        records = TaskSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].second_task_id, ids[2])
        self.assertEqual(records[1].second_task_id, ids[3])
        self.assertEqual(records[2].second_task_id, ids[2])
        self.assertEqual(records[3].second_task_id, ids[3])
        self.assertEqual(records[4].second_task_id, ids[1])
        self.assertEqual(records[5].second_task_id, ids[3])
        self.assertEqual(records[6].second_task_id, ids[1])
        self.assertEqual(records[7].second_task_id, ids[2])


class TestSavingTaskServiceSimilarities(TestCase):
    def setUp(self):
        self.organization = OrganizationBuilder().create()
        self.three_topic_ids = [a_string() for i in range(3)]
        create_topics(self.three_topic_ids)

        services = [ServiceBuilder(self.organization).create() for i in range(3)]
        self.three_service_ids = [service.id for service in services]

    def test_deletes_existing_records(self):
        topic_id = a_string()
        Task(id=topic_id, name=a_string(), description=a_string()).save()
        service = ServiceBuilder(self.organization).create()
        record = TaskServiceSimilarityScore(task_id=topic_id,
                                            service=service,
                                            similarity_score=a_float())
        record.save()

        save_topic_service_similarity_scores([], [], [], 0)

        self.assertEqual(TaskServiceSimilarityScore.objects.count(), 0)

    def test_saves_required_number_of_records_for_each_row(self):
        scores = create_square_matrix_of_unique_floats(6)
        scores_matrix = scipy.sparse.csr_matrix([[a_float() for i in range(6)] for j in range(6)])

        scores_to_save_per_row = 2
        save_topic_service_similarity_scores(
            self.three_topic_ids, self.three_service_ids, scores_matrix, scores_to_save_per_row)

        scores_saved_in_all = 3 * 2
        self.assertEqual(TaskServiceSimilarityScore.objects.count(), scores_saved_in_all)

    def test_saves_all_scores_if_number_of_scores_to_save_is_large(self):
        scores = scipy.sparse.csr_matrix([[a_float() for i in range(6)] for j in range(6)])

        too_many_records_to_save = 2000
        save_topic_service_similarity_scores(
            self.three_topic_ids, self.three_service_ids, scores, too_many_records_to_save)

        scores_saved_in_all = 3 * 3
        self.assertEqual(TaskServiceSimilarityScore.objects.count(), scores_saved_in_all)

    def test_saves_elements_with_the_highest_scores_in_each_row(self):
        scores = scipy.sparse.csr_matrix([[0, 0, 0, 1, 2, 3],
                                          [0, 0, 0, 4, 5, 6],
                                          [0, 0, 0, 7, 8, 9],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0]])
        records_to_save_per_row = 2
        save_topic_service_similarity_scores(
            self.three_topic_ids, self.three_service_ids, scores, records_to_save_per_row)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 6)
        self.assertEqual(records[0].similarity_score, 2.0)
        self.assertEqual(records[1].similarity_score, 3.0)
        self.assertEqual(records[2].similarity_score, 5.0)
        self.assertEqual(records[3].similarity_score, 6.0)
        self.assertEqual(records[4].similarity_score, 8.0)
        self.assertEqual(records[5].similarity_score, 9.0)

    def test_saves_elements_with_topic_ids(self):
        scores = scipy.sparse.csr_matrix([[0, 0, 0, 1, 2, 3],
                                          [0, 0, 0, 4, 5, 6],
                                          [0, 0, 0, 7, 8, 9],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0]])
        records_to_save_per_row = 2
        save_topic_service_similarity_scores(
            self.three_topic_ids, self.three_service_ids, scores, records_to_save_per_row)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 6)
        self.assertEqual(records[0].task_id, self.three_topic_ids[0])
        self.assertEqual(records[1].task_id, self.three_topic_ids[0])
        self.assertEqual(records[2].task_id, self.three_topic_ids[1])
        self.assertEqual(records[3].task_id, self.three_topic_ids[1])
        self.assertEqual(records[4].task_id, self.three_topic_ids[2])
        self.assertEqual(records[5].task_id, self.three_topic_ids[2])

    def test_saves_elements_with_service_ids(self):
        scores = scipy.sparse.csr_matrix([[0, 0, 0, 1, 2, 3],
                                          [0, 0, 0, 4, 5, 6],
                                          [0, 0, 0, 7, 8, 9],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0]])
        records_to_save_per_row = 2
        save_topic_service_similarity_scores(
            self.three_topic_ids, self.three_service_ids, scores, records_to_save_per_row)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 6)
        self.assertEqual(records[0].service_id, self.three_service_ids[1])
        self.assertEqual(records[1].service_id, self.three_service_ids[2])
        self.assertEqual(records[2].service_id, self.three_service_ids[1])
        self.assertEqual(records[3].service_id, self.three_service_ids[2])
        self.assertEqual(records[4].service_id, self.three_service_ids[1])
        self.assertEqual(records[5].service_id, self.three_service_ids[2])


class TestSavingManualTaskServiceSimilarities(TestCase):
    def setUp(self):
        self.organization = OrganizationBuilder().create()
        self.topic_id = a_string()
        create_topics([self.topic_id])

    def test_creates_topic_service_similarity_record_from_manual_data(self):
        service_id = a_string()
        ServiceBuilder(self.organization).with_id(service_id).create()

        manual_similarity_data = {self.topic_id: [service_id]}
        save_manual_similarities(manual_similarity_data)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].service_id, service_id)
        self.assertEqual(records[0].task_id, self.topic_id)

    def test_sets_similarity_score_to_a_large_value(self):
        service_id = a_string()
        ServiceBuilder(self.organization).with_id(service_id).create()

        manual_similarity_data = {self.topic_id: [service_id]}
        save_manual_similarities(manual_similarity_data)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')

        # NLP computed similarity scores are between 0 and 1, so 1.0 is a "large" value
        self.assertEqual(records[0].similarity_score, 1.0)

    def test_updates_record_if_it_already_exists(self):
        service_id = a_string()
        ServiceBuilder(self.organization).with_id(service_id).create()

        TaskServiceSimilarityScore(task_id=self.topic_id, service_id=service_id, similarity_score=0.2).save()

        manual_similarity_data = {self.topic_id: [service_id]}
        save_manual_similarities(manual_similarity_data)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')

        self.assertEqual(records[0].similarity_score, 1.0)

    def test_can_set_similarity_score_from_one_topic_to_several_services(self):
        services = [ServiceBuilder(self.organization).create() for i in range(3)]
        service_ids = [service.id for service in services]

        manual_similarity_data = {self.topic_id: service_ids}
        save_manual_similarities(manual_similarity_data)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')

        self.assertEqual(len(records), 3)
        self.assertTrue(records[0].service_id in service_ids)
        self.assertTrue(records[1].service_id in service_ids)
        self.assertTrue(records[2].service_id in service_ids)

    def test_can_set_similarity_score_from_several_topics(self):
        topic_ids = [a_string() for i in range(3)]
        create_topics(topic_ids)

        services = [ServiceBuilder(self.organization).create() for i in range(3)]
        service_ids = [service.id for service in services]

        manual_similarity_data = {topic_ids[0]: [service_ids[0]],
                                  topic_ids[1]: [service_ids[1]],
                                  topic_ids[2]: [service_ids[2]]}
        save_manual_similarities(manual_similarity_data)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')

        self.assertEqual(len(records), 3)
        self.assertTrue(records[0].task_id in topic_ids)
        self.assertTrue(records[1].task_id in topic_ids)
        self.assertTrue(records[2].task_id in topic_ids)

    def test_with_non_existent_topic_id_emit_warning_and_do_not_save(self):
        topic_id = a_string()

        service_id = a_string()
        ServiceBuilder(self.organization).with_id(service_id).create()

        manual_similarity_data = {topic_id: [service_id]}
        save_manual_similarities(manual_similarity_data)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')

        self.assertEqual(len(records), 0)

    def test_with_non_existent_service_id_emit_warning_and_do_not_save(self):
        topic_id = a_string()
        create_topic(topic_id)

        service_id = a_string()

        manual_similarity_data = {topic_id: [service_id]}
        save_manual_similarities(manual_similarity_data)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')

        self.assertEqual(len(records), 0)


class TestRemovingTaskTopicSimilarities(TestCase):
    def setUp(self):
        logging.disable(logging.INFO)
        self.organization = OrganizationBuilder().create()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_can_remove_one_similarity_score_by_topic_id(self):
        service = ServiceBuilder(self.organization).create()
        topic_id = a_string()
        create_topic(topic_id)
        record = TaskServiceSimilarityScore(task_id=topic_id,
                                            service=service,
                                            similarity_score=a_float())
        record.save()

        remove_similarities_for_topics([topic_id])
        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 0)

    def test_can_remove_one_similarity_score_by_service_id(self):
        service_id = a_string()
        service = ServiceBuilder(self.organization).with_id(service_id).create()
        topic_id = a_string()
        create_topic(topic_id)
        record = TaskServiceSimilarityScore(task_id=topic_id,
                                            service=service,
                                            similarity_score=a_float())
        record.save()

        remove_similarities_for_services([service_id])
        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 0)

    def test_can_remove_several_similarity_scores_for_the_same_topic(self):
        services = [ServiceBuilder(self.organization).create() for i in range(4)]
        the_topic_id = a_string()
        create_topics([the_topic_id])
        for service in services:
            TaskServiceSimilarityScore(task_id=the_topic_id,
                                       service=service,
                                       similarity_score=a_float()).save()

        remove_similarities_for_topics([the_topic_id])
        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 0)

    def test_can_remove_similarity_score_for_different_topics(self):
        service = ServiceBuilder(self.organization).create()
        topic_ids = [a_string() for i in range(3)]
        create_topics(topic_ids)
        for topic_id in topic_ids:
            TaskServiceSimilarityScore(task_id=topic_id,
                                       service=service,
                                       similarity_score=a_float()).save()

        remove_similarities_for_topics(topic_ids)
        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 0)

    def test_called_with_invalid_topic_id_does_nothing(self):
        topic_id = a_string()
        create_topic(topic_id)
        service = ServiceBuilder(self.organization).create()
        TaskServiceSimilarityScore(task_id=topic_id,
                                   service=service,
                                   similarity_score=a_float()).save()

        a_different_topic_id = a_string()
        remove_similarities_for_topics([a_different_topic_id])

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 1)

    def test_called_with_invalid_topic_id_logs_warning(self):
        topic_id = a_string()
        create_topic(topic_id)
        service = ServiceBuilder(self.organization).create()
        TaskServiceSimilarityScore(task_id=topic_id,
                                   service=service,
                                   similarity_score=a_float()).save()

        a_different_topic_id = a_string()
        logger_name = 'remove_similarities_for_topics'
        expected_log_output = 'WARNING:{}:{}: Invalid topic id'.format(logger_name, a_different_topic_id)

        with self.assertLogs(logger_name, level='WARN') as context_manager:
            remove_similarities_for_topics([a_different_topic_id])

        self.assertEqual(context_manager.output, [expected_log_output])
