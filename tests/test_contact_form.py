from conftest import get_captcha_token, get_csrf_token

VALID_FORM = {
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Hello",
    "emailContent": "This is a test message.",
}


def test_submit_without_csrf_token_is_rejected(client):
    captcha = get_captcha_token(client)
    resp = client.post("/submit_contact", data={**VALID_FORM, "captcha_token": captcha})
    assert resp.status_code == 400


def test_submit_without_captcha_token_is_rejected(client):
    token = get_csrf_token(client)
    resp = client.post("/submit_contact", data={**VALID_FORM, "csrf_token": token})
    assert resp.status_code == 200
    assert b"verify you are human" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_submit_with_invalid_captcha_token_is_rejected(client):
    token = get_csrf_token(client)
    resp = client.post(
        "/submit_contact",
        data={**VALID_FORM, "csrf_token": token, "captcha_token": "fake-invalid-token"},
    )
    assert resp.status_code == 200
    assert b"Captcha verification expired or invalid" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_submit_with_valid_csrf_token_succeeds(client):
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    resp = client.post(
        "/submit_contact",
        data={**VALID_FORM, "csrf_token": token, "captcha_token": captcha},
    )
    assert resp.status_code == 200
    assert b"Message sent successfully" in resp.data

    import main
    main.mail.send.assert_called_once()


def test_oversized_subject_is_rejected_without_sending_mail(client):
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    data = {**VALID_FORM, "csrf_token": token, "captcha_token": captcha, "subject": "x" * 151}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"too long" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_oversized_message_is_rejected_without_sending_mail(client):
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    data = {**VALID_FORM, "csrf_token": token, "captcha_token": captcha, "emailContent": "x" * 5001}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"too long" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_crlf_in_subject_is_rejected_without_sending_mail(client):
    """Guards against SMTP header injection via the subject field."""
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    data = {**VALID_FORM, "csrf_token": token, "captcha_token": captcha, "subject": "Hi\r\nBcc: attacker@evil.com"}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"line breaks" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_newlines_are_allowed_in_the_message_body(client):
    """Only `subject` becomes a raw email header - the message body is
    expected to be multi-line and must not be rejected."""
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    data = {**VALID_FORM, "csrf_token": token, "captcha_token": captcha, "emailContent": "line one\nline two"}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"Message sent successfully" in resp.data


def test_mail_send_failure_shows_generic_error(client):
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    import main
    main.mail.send.side_effect = RuntimeError("SMTP is down")

    resp = client.post("/submit_contact", data={**VALID_FORM, "csrf_token": token, "captcha_token": captcha})
    assert resp.status_code == 200
    assert b"unexpected error" in resp.data


def test_invalid_email_format_is_rejected_without_sending_email(client):
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    import main
    data = {**VALID_FORM, "csrf_token": token, "captcha_token": captcha, "email": "not-an-email"}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"valid email" in resp.data
    main.mail.send.assert_not_called()


def test_excessive_links_in_message_is_rejected_without_sending_email(client):
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    import main
    spam_msg = "Check https://site1.com and https://site2.com and also https://site3.com for deals"
    data = {**VALID_FORM, "csrf_token": token, "captcha_token": captcha, "emailContent": spam_msg}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"too many links" in resp.data
    main.mail.send.assert_not_called()


def test_sub_three_second_timing_is_rejected_without_sending_email(client, app):
    token = get_csrf_token(client)
    captcha = get_captcha_token(client)
    import main
    # Temporarily disable TESTING flag to simulate production timing check
    app.config["TESTING"] = False
    with client.session_transaction() as sess:
        sess["form_loaded_at"] = main.time.time()  # 0 elapsed seconds

    resp = client.post("/submit_contact", data={**VALID_FORM, "csrf_token": token, "captcha_token": captcha})
    assert resp.status_code == 200
    assert b"too quickly" in resp.data
    main.mail.send.assert_not_called()


