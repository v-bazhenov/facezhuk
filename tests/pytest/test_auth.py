import pytest

from tests.pytest.utils import do_login, register_random_user, register_user, activate_user, generate_token, \
    change_password, change_profile_data, get_random_username_and_email


@pytest.mark.asyncio
async def test_register():
    username, email = get_random_username_and_email()
    password, first_name, last_name, phone = "test_password", "test_first", "test_last", "+380989009900"
    register_response = await register_user(username, email, password, first_name, last_name, phone)
    assert register_response.status_code == 201
    user = register_response.json()
    assert (user["username"], user["email"]) == (username, email)


@pytest.mark.asyncio
async def test_register_conflicts():
    user, password, email, first_name, last_name = await register_random_user()
    assert (await register_user("different_username", user["email"], password,
                                'test', 'test', '380989009900')).status_code == 409
    assert (await register_user(user["username"], "different@email.com", password,
                                'test', 'test', '380989009900')).status_code == 409


@pytest.mark.asyncio
async def test_login_user_not_active():
    user, password, email, first_name, last_name = await register_random_user()
    login_response = await do_login(user["email"], password)
    assert login_response.status_code == 400
    assert login_response.json()['detail'] == 'User is not active'


@pytest.mark.asyncio
async def test_login_user_active():
    user, password, email, first_name, last_name = await register_random_user()
    token = await generate_token(email)
    await activate_user(token)
    login_response = await do_login(user["email"], password)
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_login_wrong_credentials():
    user, password, email, first_name, last_name = await register_random_user()
    res = await do_login("wrong@email.com", password)
    assert res.status_code == 400
    assert res.json()['detail'] == 'Wrong email or password'


@pytest.mark.asyncio
async def test_change_password():
    user, password, email, first_name, last_name = await register_random_user()
    token = await generate_token(email)
    await activate_user(token)
    new_password = 'new_password'
    logged_in_user = await do_login(email, password)
    access_token = logged_in_user.json()['accessToken']
    login_response = await change_password(password, new_password, access_token)
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_change_profile_data():
    user, password, email, first_name, last_name = await register_random_user()
    token = await generate_token(email)
    await activate_user(token)
    logged_in_user = await do_login(email, password)
    access_token = logged_in_user.json()['accessToken']
    login_response = await change_profile_data('new_first_name', 'new_last_name', access_token)
    assert login_response.status_code == 200
    assert login_response.json()['firstName'] == 'new_first_name'
    assert login_response.json()['lastName'] == 'new_last_name'
