from collections import defaultdict
from char_statistics_analyzer import is_match_extension, count_characters_in_file
import random
import string
import pytest

def generate_random_file(path, size, is_binary=False):
    data_dict = defaultdict(int)
    if is_binary:
        file_data=bytes([random.randint(0,255) for _ in range(size)])
    else:
        file_data = "".join(random.choices(string.printable, k=size))
        for c in file_data:
            data_dict[c] += 1

    with open(path, "wb" if is_binary else "w", encoding="utf-8" if not is_binary else None) as file:
        file.write(file_data)
    return (file_data, data_dict)

def test_is_match_extension():
    assert is_match_extension("./test.pY", ['py'], True) == True
    assert is_match_extension("./test.pY", []) == False
    assert is_match_extension("..", ['.']) == True
    assert is_match_extension("...", ['.']) == True
    assert is_match_extension("...", ['.s']) == False
    assert is_match_extension(".", ['.']) == True
    assert is_match_extension("", ['.']) == False
    assert is_match_extension("something.assf", ['.assf']) == True
    assert is_match_extension("something.assf", ['assf']) == True
    assert is_match_extension("something.assf.asf.asf.as.f.asf.", ['.']) == True
    assert is_match_extension("something.assf.asf.asf.as.f.asf.", ['.asf']) == False

def test_count_characters_in_file(tmp_path):
    file_path = tmp_path / "test_count.txt"
    data = {"s": 2, "a": 3, "f": 2, "l": 1, "\r": 4, "\n": 1}
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("aas\rfas\rfl\r\r\n")
    res = count_characters_in_file(file_path)
    assert data == res

    generate_random_file(file_path, 50, is_binary=True)
    with pytest.raises(SystemExit):
        count_characters_in_file(file_path)
