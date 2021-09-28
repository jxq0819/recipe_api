from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandsTest(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for database when database is available"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as mock_getitem:
            mock_getitem.return_value = True
            call_command('wait_for_db')
            self.assertEqual(mock_getitem.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, time_sleep):
        """Test waiting for database"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as mock_getitem:
            mock_getitem.side_effect = [OperationalError, OperationalError, OperationalError, OperationalError,
                                        OperationalError, True]
            call_command('wait_for_db')
            self.assertEqual(mock_getitem.call_count, 6)
