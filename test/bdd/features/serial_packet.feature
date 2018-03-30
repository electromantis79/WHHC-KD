Feature: A packet of scoreboard data

  Scenario: Encode a basketball packet

    Given a basketball game
    And a basketball packet
    When a basketball packet is encoded
    Then a basketball packet of the correct format is returned

  Scenario: Encode a football packet

    Given a football game
    And a football packet
    When a football packet is encoded
    Then a football packet of the correct format is returned