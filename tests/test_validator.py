from server.command.validator import validate_command


def test_valid_commands():
    valid = ["0000", "0001", "0010", "0101", "1011", "1111"]
    for value in valid:
        result = validate_command(value)
        assert result["valid"] is True
        assert result["error"] is None


def test_invalid_commands():
    invalid = ["000", "00000", "1012", "ABCD", "10A1", "1011 ", " 1011"]
    for value in invalid:
        result = validate_command(value)
        assert result["valid"] is False
        assert result["error"] is not None


def test_command_interpretation():
    result = validate_command("1011")
    assert result["valid"] is True
    assert result["bits"] == {"output_1": True, "output_2": False, "output_3": True, "output_4": True}
