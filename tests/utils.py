from httpx import Response


def assert_response(
    response: Response,
    expected_code: int,
    expected_data: dict 
):
    assert response.status_code == expected_code, f"{response.status_code} != {expected_code}"
    for k, v in expected_data.items():
        assert response.json().get(k) == v, f"{response.json().get(k)} != {v}"
    