import random
from do_data_utils.preprocessing import clean_citizenid


# ----------------
# Helper functions
# ----------------

def generate_valid_citizen_id():
    id_body = [random.randint(0, 9) for _ in range(12)]
    checksum = sum([(13 - i) * num for i, num in enumerate(id_body)]) % 11
    checksum = (11 - checksum) % 10
    return ''.join(map(str, id_body)) + str(checksum)


def generate_invalid_citizen_id():
    valid_id = generate_valid_citizen_id()
    # Change the checksum to an invalid value
    invalid_checksum = (int(valid_id[-1]) + 1) % 10
    return valid_id[:-1] + str(invalid_checksum)


# ----------------
# Test functions
# ----------------

def test_valid_citizen_id():
    valid_id = generate_valid_citizen_id()
    assert clean_citizenid(valid_id) == valid_id


def test_invalid_citizen_id():
    invalid_id = generate_invalid_citizen_id()
    assert clean_citizenid(invalid_id) is None


def test_valid_citizen_id_format():
    valid_id = generate_valid_citizen_id()
    rand_position = [random.randint(1, 11) for _ in range(4)]
    for r in rand_position:
        valid_id = valid_id[:r] + '-' + valid_id[r:]
    assert clean_citizenid(valid_id) is not None


