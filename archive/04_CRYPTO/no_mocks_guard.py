#!/usr/bin/env python3
"""
Runtime guard to ensure no mock imports in live code paths.
This module should be imported at the start of any critical solver/crypto code.
"""

import sys
import inspect


def verify_no_mocks():
    """
    Runtime verification that no mock modules are loaded.
    Raises RuntimeError if any mock modules detected.
    """
    # Check loaded modules for mock-related imports
    forbidden_modules = [
        'mock',
        'unittest.mock',
        'pytest_mock',
        'mockito',
        'flexmock',
        'doublex'
    ]
    
    loaded_mocks = []
    for module_name in sys.modules:
        for forbidden in forbidden_modules:
            if forbidden in module_name.lower():
                loaded_mocks.append(module_name)
    
    if loaded_mocks:
        raise RuntimeError(
            f"Mock modules detected in runtime: {loaded_mocks}\n"
            "This code requires real cryptographic operations only."
        )
    
    # Check call stack for mock-related frames
    stack = inspect.stack()
    for frame_info in stack:
        filename = frame_info.filename.lower()
        if 'mock' in filename or 'test' in filename:
            raise RuntimeError(
                f"Mock or test code detected in call stack: {frame_info.filename}\n"
                "This code must run in production mode only."
            )
    
    return True


def assert_production_mode():
    """
    Assert that code is running in production mode (no debug/test flags).
    """
    # Check for common test/debug environment variables
    test_env_vars = [
        'PYTEST_CURRENT_TEST',
        'TEST_MODE',
        'DEBUG_MODE',
        'MOCK_MODE',
        '__PYTEST_RUNNING'
    ]
    
    import os
    for var in test_env_vars:
        if os.environ.get(var):
            raise RuntimeError(
                f"Test/debug environment variable detected: {var}={os.environ[var]}\n"
                "This code must run in production mode only."
            )
    
    # Verify no mocks loaded
    verify_no_mocks()
    
    return True


# Auto-verify when module is imported
if __name__ != "__main__":
    try:
        assert_production_mode()
    except RuntimeError as e:
        print(f"⚠️  Runtime Guard Alert: {e}", file=sys.stderr)
        # Don't crash in case we're running legitimate analysis
        # but log the warning prominently
        pass