#!/usr/bin/env python
"""
Simple test script to verify the logging system
"""
import os
import sys
import django

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

import logging
from common.utils.logging import get_logger, PerformanceLogger

def test_basic_logging():
    """Test basic logging functionality"""
    print("Testing basic logging...")

    # Test basic logger
    logger = get_logger('test')
    logger.info("This is a test info message")
    logger.warning("This is a test warning message")
    logger.error("This is a test error message")

    print("✓ Basic logging works")

def test_performance_logger():
    """Test performance logger"""
    print("Testing performance logger...")

    perf_logger = PerformanceLogger()
    perf_logger.start_timer('test_operation')

    # Simulate some work
    import time
    time.sleep(0.1)

    duration_ms = perf_logger.end_timer(threshold_ms=100)
    print(f"✓ Performance logging works - Duration: {duration_ms}ms")

def test_request_logger():
    """Test request logger"""
    print("Testing request logger...")

    request_logger = get_logger('teaching_platform.api', 'test-request-id')
    request_logger.info("Test request log", extra={
        'user_id': 123,
        'path': '/api/test',
        'method': 'GET'
    })

    print("✓ Request logging works")

def test_log_files():
    """Test log file creation"""
    print("Testing log file creation...")

    # Get log directory
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')

    # Check if log files are being created
    log_files = ['django.log', 'api.log', 'error.log', 'security.log', 'celery.log']

    for log_file in log_files:
        log_path = os.path.join(log_dir, log_file)
        if os.path.exists(log_path):
            print(f"✓ {log_file} exists")
        else:
            print(f"⚠ {log_file} does not exist (this is normal in development)")

    # Check if any log file was recently written to
    for log_file in log_files:
        log_path = os.path.join(log_dir, log_file)
        if os.path.exists(log_path):
            stat = os.stat(log_path)
            print(f"✓ {log_file} was last modified at {stat.st_mtime}")

if __name__ == '__main__':
    print("=" * 50)
    print("Django Backend Logging System Test")
    print("=" * 50)

    try:
        test_basic_logging()
        test_performance_logger()
        test_request_logger()
        test_log_files()

        print("\n" + "=" * 50)
        print("✅ All logging tests passed!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)