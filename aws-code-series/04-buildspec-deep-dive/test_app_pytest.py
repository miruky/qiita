import pytest
from app import hello, add

class TestApp:
    def test_hello(self):
        assert hello() == "Hello, AWS CodeBuild!"

    def test_add_positive(self):
        assert add(1, 2) == 3

    def test_add_negative(self):
        assert add(-1, 1) == 0

    def test_add_zero(self):
        assert add(0, 0) == 0
