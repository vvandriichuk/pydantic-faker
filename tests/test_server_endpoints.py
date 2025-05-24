import random
from datetime import UTC

import pytest
from fastapi.testclient import TestClient

from pydantic_faker.core import generate_fake_data_for_model, get_faker_instance
from pydantic_faker.server import create_fastapi_app

from .helpers import SimpleTestModel


@pytest.fixture(scope="module")
def simple_user_app_client() -> TestClient:
    """Fixture for creating TestClient for SimpleUser."""
    model_class = SimpleTestModel

    faker_instance = get_faker_instance(locale="en_US", seed=123)
    data_instances = [
        generate_fake_data_for_model(model_class, faker_instance_override=faker_instance) for _ in range(5)
    ]
    app = create_fastapi_app(model_class, data_instances, faker_instance)
    return TestClient(app)


def test_get_all_simple_users(simple_user_app_client: TestClient):
    response = simple_user_app_client.get("/simpletestmodels")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert "name" in data[0]
    assert "email" in data[0]


def test_get_single_simple_user_by_index(simple_user_app_client: TestClient):
    response = simple_user_app_client.get("/simpletestmodels/0")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

    response_not_found = simple_user_app_client.get("/simpletestmodels/99")
    assert response_not_found.status_code == 404


def test_get_single_simple_user_by_id_field(simple_user_app_client: TestClient):
    all_response = simple_user_app_client.get("/simpletestmodels")
    assert all_response.status_code == 200
    all_data = all_response.json()
    if not all_data:
        pytest.skip("No data generated to test get by ID")

    item_to_find = all_data[0]
    item_id_to_find = item_to_find.get("id")

    if item_id_to_find is None:
        pytest.skip("Generated item does not have an 'id' field to test by.")

    response = simple_user_app_client.get(f"/simpletestmodels/{item_id_to_find}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id_to_find

    non_existent_id = 99999
    response_not_found = simple_user_app_client.get(f"/simpletestmodels/{non_existent_id}")
    assert response_not_found.status_code == 404


def test_create_simple_user(simple_user_app_client: TestClient):
    faker_instance = get_faker_instance(locale="en_US", seed=789)
    new_user_payload = {
        "id": faker_instance.pyint(min_value=100, max_value=200),
        "name": faker_instance.name(),
        "email": faker_instance.email(),
        "is_active": faker_instance.boolean(),
        "uuid": faker_instance.uuid4(),
        "created_at": faker_instance.date_time_this_decade(tzinfo=UTC).isoformat(),
        "birth_date": faker_instance.date_of_birth().isoformat(),
        "wakeup_time": faker_instance.time(),
        "description": faker_instance.sentence(nb_words=6),
        "tags": [faker_instance.word() for _ in range(random.randint(1, 3))],
    }

    while len(new_user_payload["name"]) < 5:
        new_user_payload["name"] = faker_instance.name()

    new_user_payload_cleaned = {k: v for k, v in new_user_payload.items() if v is not None}

    response = simple_user_app_client.post("/simpletestmodels", json=new_user_payload_cleaned)
    if response.status_code != 201:
        print("Validation errors:", response.json())
    assert response.status_code == 201  # Created
    created_item = response.json()
    assert created_item["name"] == new_user_payload_cleaned["name"]
    assert "id" in created_item
    if new_user_payload_cleaned.get("id"):
        assert created_item["id"] == new_user_payload_cleaned["id"]
    else:
        assert isinstance(created_item["id"], int)

    get_response = simple_user_app_client.get(f"/simpletestmodels/{created_item['id']}")
    assert get_response.status_code == 200


def test_get_all_simple_users_with_filter(simple_user_app_client: TestClient):
    response_all = simple_user_app_client.get("/simpletestmodels")
    assert response_all.status_code == 200
    all_data = response_all.json()

    if not all_data:
        pytest.skip("No data to test filtering on.")

    target_description = all_data[0].get("description")
    if target_description is not None:
        response_filtered_desc = simple_user_app_client.get(f"/simpletestmodels?description={target_description}")
        assert response_filtered_desc.status_code == 200
        filtered_data_desc = response_filtered_desc.json()
        assert len(filtered_data_desc) > 0
        for item in filtered_data_desc:
            assert item["description"] == target_description
        if len({d["description"] for d in all_data}) > 1:
            assert len(filtered_data_desc) < len(all_data)

    response_filtered_active = simple_user_app_client.get("/simpletestmodels?is_active=true")
    assert response_filtered_active.status_code == 200
    filtered_data_active = response_filtered_active.json()
    if any(item["is_active"] for item in all_data):
        assert len(filtered_data_active) > 0
        for item in filtered_data_active:
            assert item["is_active"] is True
    else:
        assert len(filtered_data_active) == 0

    response_filtered_inactive = simple_user_app_client.get("/simpletestmodels?is_active=false")
    assert response_filtered_inactive.status_code == 200
    filtered_data_inactive = response_filtered_inactive.json()
    if any(not item["is_active"] for item in all_data):
        assert len(filtered_data_inactive) > 0
        for item in filtered_data_inactive:
            assert item["is_active"] is False
    else:
        assert len(filtered_data_inactive) == 0

    target_name_for_combo = all_data[0].get("name")
    target_is_active_for_combo = all_data[0].get("is_active")

    if target_name_for_combo is not None and target_is_active_for_combo is not None:
        response_combo = simple_user_app_client.get(
            f"/simpletestmodels?name={target_name_for_combo}&is_active={str(target_is_active_for_combo).lower()}",
        )
        assert response_combo.status_code == 200
        filtered_combo_data = response_combo.json()
        assert len(filtered_combo_data) > 0
        for item in filtered_combo_data:
            assert item["name"] == target_name_for_combo
            assert item["is_active"] == target_is_active_for_combo

    non_existent_description = "this_description_does_not_exist_12345"
    response_no_match = simple_user_app_client.get(f"/simpletestmodels?description={non_existent_description}")
    assert response_no_match.status_code == 200
    assert response_no_match.json() == []
