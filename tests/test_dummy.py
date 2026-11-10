from new_project.dummy import answer


def test_answer_returns_placeholder() -> None:
    assert answer() == 42
