"""
Basic tests for Seltra AMM development environment
"""

import pytest
import requests


def test_localnet_connection():
    """Test that AlgoKit LocalNet is accessible"""
    try:
        response = requests.get(
            'http://localhost:4001/v2/status',
            headers={'X-Algo-API-Token': 'a'},
            timeout=5
        )
        # We expect a response (even if it's an error about invalid token)
        assert response.status_code in [200, 401]
    except requests.exceptions.RequestException:
        pytest.fail("AlgoKit LocalNet is not accessible")


def test_indexer_connection():
    """Test that Indexer is accessible"""
    try:
        response = requests.get('http://localhost:8980/health', timeout=5)
        assert response.status_code == 200
    except requests.exceptions.RequestException:
        pytest.fail("Indexer is not accessible")


def test_project_structure():
    """Test that essential project files exist"""
    import os
    
    essential_files = [
        'requirements.txt',
        'Makefile',
        'dev.sh',
        'setup.sh',
        'README.md',
        'PRD.md',
        'roadmap.md'
    ]
    
    for file in essential_files:
        assert os.path.exists(file), f"Essential file {file} is missing"
    
    essential_dirs = [
        'contracts',
        'simulation',
        'tests',
        'frontend',
        'scripts'
    ]
    
    for directory in essential_dirs:
        assert os.path.exists(directory), f"Essential directory {directory} is missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
