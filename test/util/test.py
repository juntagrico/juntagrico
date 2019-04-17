def test_simple_get(test_case, url):
    test_case.client.force_login(test_case.member.user)
    response = test_case.client.get(url)
    test_case.assertEqual(response.status_code, 200)
