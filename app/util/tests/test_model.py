from django.test import TestCase

from app.util.models import Design, Language, Position, Stack


class TestMasterModel(TestCase):
    """포지션, 언어, 스택, 디자인 마스터 모델 테스트"""

    def test_create_position(self):
        # 포지션 생성
        position = Position.objects.create(name="백엔드")
        self.assertEqual(position.name, "백엔드")  # 이름이 올바르게 저장되었는지 확인
        self.assertEqual(str(position), position.name) if hasattr(position, "__str__") else None

    def test_create_language(self):
        # 언어 생성
        language = Language.objects.create(name="Python")
        self.assertEqual(language.name, "Python")  # 이름 확인

    def test_create_stack(self):
        # 스택 생성
        stack = Stack.objects.create(name="Django")
        self.assertEqual(stack.name, "Django")  # 저장된 이름이 기대한 값인지 확인

    def test_create_design(self):
        # 디자인 생성
        design = Design.objects.create(name="Figma")
        self.assertEqual(design.name, "Figma")  # 올바른 이름 저장 여부 확인

    def test_name_max_length(self):
        # 최대 길이를 초과하는 이름으로 저장 시 에러 발생 여부 확인
        long_name = "a" * 101  # 100자를 초과하는 문자열
        with self.assertRaises(Exception):
            Position.objects.create(name=long_name)  # CharField(max_length=100)이므로 예외 발생 기대
