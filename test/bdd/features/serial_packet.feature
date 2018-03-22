Feature: A packet of scoreboard data

  Scenario: Encode a basketball packet

    Given a game
    And an address map
    When a packet is encoded
    Then a packet of the correct format is returned