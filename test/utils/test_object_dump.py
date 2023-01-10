from typing import Optional, List

import pytest

from src.utils.object_dump import get_public_class_members


class TestGetPublicClassMembers:
    class ClassA:

        def __init__(self, arg_x: int = 12) -> None:
            self.member_x: int = arg_x
            self.member_y: Optional[int] = None
            self.member_z: float = 0.0
            self._member_a: bool = True
            self._member_b: bool = True
            self.__member_b: bool = True  # pylint: disable=unused-private-member
            self.member_c: int

        @property
        def a_property(self):
            return self._member_a

        @a_property.setter
        def a_property(self, value: bool) -> None:
            self._member_a = value

        def method(self) -> None:
            pass

        def _method_a(self) -> None:
            pass

        def __method_b(self) -> None:  # pylint: disable=unused-private-member
            pass

        @staticmethod
        def static_method() -> None:
            pass

        @staticmethod
        def _static_method_a() -> None:
            pass

        @staticmethod
        def __static_method_b() -> None:  # pylint: disable=unused-private-member
            pass

    @pytest.mark.parametrize("obj, expected_members", [(ClassA(), ["member_x", "member_y", "member_z", "a_property"])])
    def test_get_public_class_members(self, obj: object, expected_members: List[str]):
        current_members = get_public_class_members(obj)

        assert len(current_members) == len(expected_members)
        for member in current_members:
            assert member in expected_members
