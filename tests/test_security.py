from auth.security import check_password, hash_password


def test_password_hash_roundtrip():
    password = "super-secret-password"
    hashed = hash_password(password)
    assert hashed != password
    assert check_password(password, hashed)
    assert not check_password("wrong-password", hashed)
