from logic_utils import check_guess, parse_guess, get_range_for_difficulty

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# New tests added while fixing the bugs ---------------------------------------

def test_hints_are_not_backwards():
    # Regression test for the "backwards hints" bug: a guess ABOVE the secret
    # must be "Too High" (not "Too Low"), and below must be "Too Low".
    assert check_guess(80, 50) == "Too High"
    assert check_guess(20, 50) == "Too Low"

def test_parse_guess_handles_bad_input():
    # Empty input and non-numbers should be rejected, not crash.
    ok, value, err = parse_guess("")
    assert ok is False and value is None and err

    ok, value, err = parse_guess("abc")
    assert ok is False and value is None and err

    ok, value, err = parse_guess("42")
    assert ok is True and value == 42 and err is None

def test_range_matches_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)
