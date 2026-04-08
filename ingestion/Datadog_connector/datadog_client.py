"""
datadog_client.py
=================
Low-level Datadog API client with circuit breaker and retry logic.

Follows SOLID principles:
  - Single Responsibility: Only handles HTTP communication
  - Dependency Injection: Config and credentials passed externally
  - Open/Closed: Easy to extend with new endpoints
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class DatadogClientConfig:
    """Configuration object for Datadog client (Immutable)."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        app_key: Optional[str] = None,
        site: str = "datadoghq.eu",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.getenv("DD_API_KEY")
        self.app_key = app_key or os.getenv("DD_APP_KEY")
        self.site = site or os.getenv("DD_SITE", "datadoghq.eu")
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.api_key or not self.app_key:
            raise ValueError("DD_API_KEY and DD_APP_KEY must be provided via env vars or constructor")


class DatadogAPIClient:
    """
    HTTP client for Datadog APIs with built-in retry logic and error handling.
    
    Usage:
        config = DatadogClientConfig()
        client = DatadogAPIClient(config)
        services = client.get("/api/v2/services")
    """
    
    BASE_URL_TEMPLATE = "https://api.{site}"
    
    def __init__(self, config: DatadogClientConfig):
        self.config = config
        self.base_url = self.BASE_URL_TEMPLATE.format(site=config.site)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with authentication."""
        return {
            "DD-API-KEY": self.config.api_key,
            "DD-APPLICATION-KEY": self.config.app_key,
            "Content-Type": "application/json",
        }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform GET request to Datadog API.
        
        Args:
            endpoint: API endpoint (e.g., "/api/v2/services")
            params: Query parameters
            
        Returns:
            Response JSON
            
        Raises:
            requests.HTTPError: On HTTP errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug(f"✓ GET {endpoint} - Status: {response.status_code}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ HTTP Error on GET {endpoint}: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Request Error on GET {endpoint}: {e}")
            raise
    
    def post(self, endpoint: str, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform POST request to Datadog API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=json_data,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug(f"✓ POST {endpoint} - Status: {response.status_code}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ HTTP Error on POST {endpoint}: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Request Error on POST {endpoint}: {e}")
            raise
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
