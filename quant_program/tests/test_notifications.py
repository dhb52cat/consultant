# quant_program/tests/test_notifications.py
import pytest
from unittest.mock import MagicMock, patch
from notifications.wxpusher_notifier import WxPusherNotifier
from notifications.wecom_notifier import WeComNotifier

@pytest.fixture
def mock_config(tmp_path):
    config_file = tmp_path / "settings.ini"
    config_file.write_text("""
[NOTIFICATIONS]
WXPUSHER_APP_TOKEN = test_token
WXPUSHER_UIDS = uid1,uid2
WECOM_WEBHOOK_URL = https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ac331fa1-0899-466b-8b1c-f01842e3eaa7
""")
    return str(config_file)

def test_wxpusher_notifier(mock_config):
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {'code': 1000}
        mock_post.return_value.status_code = 200
        
        notifier = WxPusherNotifier(mock_config)
        success = notifier.send_message("Title", "Content")
        
        assert success is True
        mock_post.assert_called_once()

def test_wecom_notifier(mock_config):
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {'errcode': 0}
        mock_post.return_value.status_code = 200
        
        notifier = WeComNotifier(mock_config)
        success = notifier.send_message("Title", "Content")
        
        assert success is True
        mock_post.assert_called_once()
