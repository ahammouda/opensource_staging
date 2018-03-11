from django.test import TestCase

# Create your tests here.
from django.test import TestCase

class FooTest(TestCase):

    def test_foo(self):
        assert True
        assert 1 == 1


    def test_foo2(self):
        assert 2 == 2
        assert 'x' == 'x'