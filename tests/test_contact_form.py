from conftest import get_csrf_token

VALID_FORM = {
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Hello",
    "emailContent": "This is a test message.",
}


def test_submit_without_csrf_token_is_rejected(client):
    resp = client.post("/submit_contact", data=VALID_FORM)
    assert resp.status_code == 400


def test_submit_with_valid_csrf_token_succeeds(client):
    token = get_csrf_token(client)
    resp = client.post("/submit_contact", data={**VALID_FORM, "csrf_token": token})
    assert resp.status_code == 200
    assert b"Message sent successfully" in resp.data

    import main
    main.mail.send.assert_called_once()


def test_oversized_subject_is_rejected_without_sending_mail(client):
    token = get_csrf_token(client)
    data = {**VALID_FORM, "csrf_token": token, "subject": "x" * 151}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"too long" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_oversized_message_is_rejected_without_sending_mail(client):
    token = get_csrf_token(client)
    data = {**VALID_FORM, "csrf_token": token, "emailContent": "x" * 5001}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"too long" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_crlf_in_subject_is_rejected_without_sending_mail(client):
    """Guards against SMTP header injection via the subject field - the
    underlying email library already blocks this at send time, but the
    explicit check gives a real error message instead of a generic one,
    and this test would catch it if that check were ever removed."""
    token = get_csrf_token(client)
    data = {**VALID_FORM, "csrf_token": token, "subject": "Hi\r\nBcc: attacker@evil.com"}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"line breaks" in resp.data

    import main
    main.mail.send.assert_not_called()


def test_newlines_are_allowed_in_the_message_body(client):
    """Only `subject` becomes a raw email header - the message body is
    expected to be multi-line and must not be rejected."""
    token = get_csrf_token(client)
    data = {**VALID_FORM, "csrf_token": token, "emailContent": "line one\nline two"}
    resp = client.post("/submit_contact", data=data)
    assert resp.status_code == 200
    assert b"Message sent successfully" in resp.data


def test_mail_send_failure_shows_generic_error(client):
    token = get_csrf_token(client)
    import main
    main.mail.send.side_effect = RuntimeError("SMTP is down")

    resp = client.post("/submit_contact", data={**VALID_FORM, "csrf_token": token})
    assert resp.status_code == 200
    assert b"unexpected error" in resp.data
