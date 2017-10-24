Feature: Management of question entities

    Scenario: Retrieve an entity
        Given a question with text "foo"
        Then I can get the question with text "foo"

    Scenario: Create an entity

        When I create a question with text "bar"
        Then I can get the question with text "bar"

    Scenario: Update an entity

        Given a question with text "foo"
        When I update the question with text "baz"
        Then I can get the question with text "baz"

    Scenario: Delete an entity

        Given a question
        When I delete the question
        Then I fail to get the question
