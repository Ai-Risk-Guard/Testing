"""
Regression tests for the intentional SQL injection vulnerability.

The vulnerable-baseline test confirms that the lab is exploitable.
After the SQL query is fixed, this test should be updated to expect
the injection attempt to fail.
"""


def test_controlled_sql_injection_bypasses_login(client):
    """
    Baseline demonstration:

    The username field contains SQL syntax that makes the WHERE
    condition true and comments out the password condition.

    The test uses only fictional accounts in an isolated local database.
    """

    response = client.post(
        "/login",
        data={
            "username": "' OR '1'='1' -- ",
            "password": "incorrect-password",
        },
        follow_redirects=True,
    )

    # In the vulnerable baseline, the query accepts the login.
    assert response.status_code == 200

    # The query returns a user and the dashboard is displayed.
    assert b"Available Balance" in response.data


def test_normal_wrong_password_does_not_authenticate(client):
    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "not-the-correct-password",
        },
        follow_redirects=True,
    )

    assert b"Invalid username or password" in response.data
    assert b"Available Balance" not in response.data