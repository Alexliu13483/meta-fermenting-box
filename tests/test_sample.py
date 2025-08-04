"""
示範測試檔案 - 用來驗證 VSCode Testing 面板設定
"""
import pytest


class TestSample:
    """示範測試類別"""
    
    def test_simple_pass(self):
        """簡單的通過測試"""
        assert 1 + 1 == 2
    
    def test_simple_fail(self):
        """簡單的失敗測試 (用來測試錯誤顯示)"""
        # 取消註解下面這行來測試失敗情況
        # assert 1 + 1 == 3
        assert True
    
    @pytest.mark.unit
    def test_with_marker(self):
        """帶有標記的測試"""
        assert "hello".upper() == "HELLO"
    
    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 3),
        (3, 4),
    ])
    def test_parametrized(self, input, expected):
        """參數化測試"""
        assert input + 1 == expected
    
    def test_with_fixture(self, sample_data):
        """使用 fixture 的測試"""
        assert sample_data["name"] == "test"


@pytest.fixture
def sample_data():
    """測試用的 fixture"""
    return {"name": "test", "value": 42}


def test_function_level():
    """函數級別的測試"""
    assert len("hello") == 5


@pytest.mark.slow
def test_slow_operation():
    """標記為慢速的測試"""
    import time
    time.sleep(0.1)  # 模擬慢速操作
    assert True