from unittest.mock import MagicMock, patch

import pytest

from dream_factory_evals.dream_factory_mcp import (
    BASE_URL,
    HEADERS,
    get_params,
    get_table_records,
    get_table_records_by_ids,
)

# Sample data for hr_employees
HR_EMPLOYEES_SAMPLE = {
    "resource": [
        {
            "employee_id": 1,
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.johnson@example.com",
            "date_joined": "2022-01-15",
            "department_id": 1,
            "role": "Staff",
        },
        {
            "employee_id": 2,
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob.smith@example.com",
            "date_joined": "2022-02-10",
            "department_id": 2,
            "role": "Staff",
        },
        {
            "employee_id": 3,
            "first_name": "Carol",
            "last_name": "Williams",
            "email": "carol.williams@example.com",
            "date_joined": "2022-03-05",
            "department_id": 3,
            "role": "Manager",
        },
        {
            "employee_id": 4,
            "first_name": "David",
            "last_name": "Brown",
            "email": "david.brown@example.com",
            "date_joined": "2022-04-20",
            "department_id": 4,
            "role": "Staff",
        },
        {
            "employee_id": 5,
            "first_name": "Eve",
            "last_name": "Davis",
            "email": "eve.davis@example.com",
            "date_joined": "2022-05-15",
            "department_id": 5,
            "role": "Manager",
        },
    ]
}


# Mock httpx.get for the tests
@pytest.fixture
def mock_httpx_get():
    with patch("httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response
        yield mock_get


# Specific mock for hr_employees table
@pytest.fixture
def mock_hr_employees_get():
    with patch("httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = HR_EMPLOYEES_SAMPLE
        mock_get.return_value = mock_response
        yield mock_get


# Test get_table_records with hr_employees
def test_get_hr_employees(mock_hr_employees_get):
    result = get_table_records(table_name="hr_employees")

    mock_hr_employees_get.assert_called_once_with(
        url=f"{BASE_URL}/_table/hr_employees",
        headers=HEADERS,
        params=get_params(),
    )

    assert result == HR_EMPLOYEES_SAMPLE
    assert len(result["resource"]) == 5
    assert result["resource"][0]["first_name"] == "Alice"
    assert result["resource"][2]["first_name"] == "Carol"
    assert result["resource"][4]["first_name"] == "Eve"


# Test filtering hr_employees with more combinations
@pytest.mark.parametrize(
    "filter_str,expected_employee_ids",
    [
        ("first_name='Alice'", [1]),
        ("department_id=2", [2]),
        ("role='Staff'", [1, 2, 4]),
        ("role='Manager'", [3, 5]),
        ("department_id>3", [4, 5]),
        ("date_joined>='2022-03-01'", [3, 4, 5]),
        ("(role='Manager') AND (department_id>3)", [5]),
        ("first_name like 'A%'", [1]),
        ("email like '%@example.com'", [1, 2, 3, 4, 5]),
    ],
)
def test_filter_hr_employees(filter_str, expected_employee_ids):
    with patch("httpx.get") as mock_get:
        # Create filtered response based on the filter
        filtered_employees = [
            emp for emp in HR_EMPLOYEES_SAMPLE["resource"] if emp["employee_id"] in expected_employee_ids
        ]
        filtered_response = {"resource": filtered_employees}

        mock_response = MagicMock()
        mock_response.json.return_value = filtered_response
        mock_get.return_value = mock_response

        result = get_table_records(table_name="hr_employees", filter=filter_str)

        mock_get.assert_called_once_with(
            url=f"{BASE_URL}/_table/hr_employees",
            headers=HEADERS,
            params=get_params(filter=filter_str),
        )

        assert len(result["resource"]) == len(expected_employee_ids)
        for emp in result["resource"]:
            assert emp["employee_id"] in expected_employee_ids


# Test getting specific fields
def test_get_hr_employees_specific_fields():
    with patch("httpx.get") as mock_get:
        fields = ["first_name", "last_name", "role"]
        field_response = {
            "resource": [
                {"first_name": "Alice", "last_name": "Johnson", "role": "Staff"},
                {"first_name": "Bob", "last_name": "Smith", "role": "Staff"},
                {"first_name": "Carol", "last_name": "Williams", "role": "Manager"},
                {"first_name": "David", "last_name": "Brown", "role": "Staff"},
                {"first_name": "Eve", "last_name": "Davis", "role": "Manager"},
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = field_response
        mock_get.return_value = mock_response

        result = get_table_records(table_name="hr_employees", fields=fields)

        mock_get.assert_called_once_with(
            url=f"{BASE_URL}/_table/hr_employees",
            headers=HEADERS,
            params=get_params(fields=fields),
        )

        assert result == field_response
        for emp in result["resource"]:
            assert "email" not in emp
            assert "first_name" in emp
            assert "role" in emp


# Test getting records by IDs
def test_get_hr_employees_by_ids():
    with patch("httpx.get") as mock_get:
        ids = ["1", "3", "5"]
        expected_employees = [emp for emp in HR_EMPLOYEES_SAMPLE["resource"] if str(emp["employee_id"]) in ids]

        mock_response = MagicMock()
        mock_response.json.return_value = {"resource": expected_employees}
        mock_get.return_value = mock_response

        result = get_table_records_by_ids(table_name="hr_employees", ids=ids)

        params = {"ids": ",".join(ids)}
        params.update(get_params())

        mock_get.assert_called_once_with(
            url=f"{BASE_URL}/_table/hr_employees",
            headers=HEADERS,
            params=params,
        )

        assert len(result["resource"]) == 3
        emp_ids = [emp["employee_id"] for emp in result["resource"]]
        assert set(emp_ids) == {1, 3, 5}
        assert result["resource"][0]["first_name"] == "Alice"
        assert result["resource"][1]["first_name"] == "Carol"
        assert result["resource"][2]["first_name"] == "Eve"


# Test limit and offset with hr_employees
@pytest.mark.parametrize(
    "limit,offset,expected_ids",
    [
        (2, 0, [1, 2]),
        (2, 2, [3, 4]),
        (1, 4, [5]),
        (3, 1, [2, 3, 4]),
    ],
)
def test_hr_employees_limit_offset(limit, offset, expected_ids):
    with patch("httpx.get") as mock_get:
        expected_employees = [emp for emp in HR_EMPLOYEES_SAMPLE["resource"] if emp["employee_id"] in expected_ids]

        mock_response = MagicMock()
        mock_response.json.return_value = {"resource": expected_employees}
        mock_get.return_value = mock_response

        result = get_table_records(table_name="hr_employees", limit=limit, offset=offset)

        mock_get.assert_called_once_with(
            url=f"{BASE_URL}/_table/hr_employees",
            headers=HEADERS,
            params=get_params(limit=limit, offset=offset),
        )

        assert len(result["resource"]) == len(expected_ids)
        result_ids = [emp["employee_id"] for emp in result["resource"]]
        assert result_ids == expected_ids


# Test ordering
@pytest.mark.parametrize(
    "order_field,expected_ids",
    [
        ("first_name ASC", [1, 2, 3, 4, 5]),
        ("first_name DESC", [5, 4, 3, 2, 1]),
        ("department_id ASC", [1, 2, 3, 4, 5]),
        ("date_joined DESC", [5, 4, 3, 2, 1]),
    ],
)
def test_hr_employees_ordering(order_field, expected_ids):
    with patch("httpx.get") as mock_get:
        ordered_employees = [
            emp
            for emp_id in expected_ids
            for emp in HR_EMPLOYEES_SAMPLE["resource"]
            if emp["employee_id"] == emp_id
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {"resource": ordered_employees}
        mock_get.return_value = mock_response

        result = get_table_records(table_name="hr_employees", order_field=order_field)

        mock_get.assert_called_once_with(
            url=f"{BASE_URL}/_table/hr_employees",
            headers=HEADERS,
            params=get_params(order_field=order_field),
        )

        assert len(result["resource"]) == 5
        result_ids = [emp["employee_id"] for emp in result["resource"]]
        assert result_ids == expected_ids
