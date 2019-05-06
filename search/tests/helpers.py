from common.testhelpers.random_test_values import a_float


def create_scores(test_range):
    scores = [[a_float() for i in range(test_range)] for j in range(test_range)]
    
    if check_if_scores_has_duplicate(scores):
        create_scores(test_range)
    return scores


def check_if_scores_has_duplicate(scores):
    float_dictionary = {}
    has_duplicate = None
    
    for i in scores:
        for j in i:
            if j in float_dictionary:
                has_duplicate = True
                break
            else: 
                float_dictionary[j] = 1
                has_duplicate = False
    return has_duplicate



