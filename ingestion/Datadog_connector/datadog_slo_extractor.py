"""
datadog_slo_extractor.py
========================

Extracts SLO (Service Level Objective) data from Datadog API.

API Documentation: https://docs.datadoghq.com/api/latest/service-level-objectives/#get-all-slos
"""

import logging
from typing import Dict, List, Any, Optional
from .datadog_client import DatadogAPIClient

logger = logging.getLogger(__name__)


class SLOExtractor:
    """
    Extracts Service Level Objectives (SLOs) and related data from Datadog.
    
    Example:
        extractor = SLOExtractor(client)
        slos = extractor.extract_all_slos(limit=100)
        corrections = extractor.extract_slo_corrections(slo_id="abc123")
    """
    
    API_ENDPOINT_SLOS = "/api/v1/slo"
    API_ENDPOINT_CORRECTIONS = "/api/v1/slo/correction"
    MAX_LIMIT = 1000
    DEFAULT_LIMIT = 100
    
    def __init__(self, client: DatadogAPIClient):
        """
        Initialize the SLO extractor.
        
        Args:
            client: DatadogAPIClient instance with valid credentials
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def extract_all_slos(
        self,
        offset: int = 0,
        limit: int = DEFAULT_LIMIT,
        query: Optional[str] = None,
        tags_query: Optional[str] = None,
        ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract all SLOs with optional filtering.
        
        Args:
            offset: Pagination offset (default: 0)
            limit: Items per page, max 1000 (default: 100)
            query: Filter SLOs by name (e.g., "availability")
            tags_query: Filter by tags (e.g., "env:prod,team:platform")
            ids: Comma-separated SLO IDs to fetch
            
        Returns:
            List of SLO dictionaries with data, metadata, and status
            
        Raises:
            requests.HTTPError: On API errors
            
        Example Response Structure:
            [
              {
                "id": "abc123",
                "name": "API Availability",
                "description": "99.9% uptime for payment API",
                "type": "metric",
                "type_id": 0,
                "tags": ["env:prod", "team:platform"],
                "thresholds": [
                  {"target": 99.9, "target_display": "99.9", "timeframe": "7d"},
                  {"target": 99.95, "target_display": "99.95", "timeframe": "30d"}
                ],
                "monitor_ids": [123456, 789012],
                "monitor_tags": ["monitor:critical"],
                "creator": {...},
                "created_at": 1234567890,
                "modified_at": 1234567891
              }
            ]
        """
        if limit > self.MAX_LIMIT:
            logger.warning(f"Limit {limit} exceeds max {self.MAX_LIMIT}, using {self.MAX_LIMIT}")
            limit = self.MAX_LIMIT
        
        try:
            logger.info(f"📊 Extracting SLOs (offset={offset}, limit={limit})...")
            
            params = {
                "offset": offset,
                "limit": limit,
            }
            
            # Add optional filters
            if query:
                params["query"] = query
                logger.debug(f"  Filter by name: {query}")
            
            if tags_query:
                params["tags_query"] = tags_query
                logger.debug(f"  Filter by tags: {tags_query}")
            
            if ids:
                params["ids"] = ",".join(ids)
                logger.debug(f"  Filter by IDs: {ids}")
            
            response = self.client.get(self.API_ENDPOINT_SLOS, params=params)
            
            slos = response.get("data", [])
            
            logger.info(f"✅ Extracted {len(slos)} SLOs")
            
            return slos
        
        except Exception as e:
            logger.error(f"❌ Error extracting SLOs: {e}", exc_info=True)
            raise
    
    def extract_slo_by_id(self, slo_id: str) -> Dict[str, Any]:
        """
        Extract a single SLO by ID with full details.
        
        Args:
            slo_id: SLO identifier
            
        Returns:
            SLO dictionary with complete details
            
        Raises:
            requests.HTTPError: On API errors (404 if not found)
        """
        try:
            logger.info(f"📊 Extracting SLO: {slo_id}")
            
            endpoint = f"{self.API_ENDPOINT_SLOS}/{slo_id}"
            response = self.client.get(endpoint)
            
            slo = response.get("data", {})
            
            logger.info(f"✅ Extracted SLO: {slo.get('name', slo_id)}")
            
            return slo
        
        except Exception as e:
            logger.error(f"❌ Error extracting SLO {slo_id}: {e}", exc_info=True)
            raise
    
    def extract_slo_corrections(
        self,
        slo_id: Optional[str] = None,
        offset: int = 0,
        limit: int = DEFAULT_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Extract SLO corrections (maintenance windows/scheduled downtime).
        
        SLO corrections are time periods excluded from SLO calculations
        (e.g., planned maintenance, known issues).
        
        Args:
            slo_id: Optional SLO ID to filter corrections
            offset: Pagination offset
            limit: Items per page, max 1000
            
        Returns:
            List of correction dictionaries
            
        Example Response:
            [
              {
                "id": "corr-123",
                "type": "correction",
                "attributes": {
                  "category": "Scheduled Maintenance",
                  "description": "Database migration",
                  "start": 1234567890,
                  "end": 1234571490,
                  "duration": 3600,
                  "slo_id": "abc123",
                  "timezone": "UTC",
                  "rrule": "FREQ=WEEKLY;BYDAY=SU",  # Recurring rules
                  "created_at": 1234567800,
                  "modified_at": 1234567850,
                  "creator": {...},
                  "modifier": {...}
                }
              }
            ]
        """
        if limit > self.MAX_LIMIT:
            logger.warning(f"Limit {limit} exceeds max {self.MAX_LIMIT}, using {self.MAX_LIMIT}")
            limit = self.MAX_LIMIT
        
        try:
            logger.info(f"🛠️  Extracting SLO corrections (slo_id={slo_id or 'all'})...")
            
            params = {
                "offset": offset,
                "limit": limit,
            }
            
            # Filter by SLO ID if provided
            if slo_id:
                # Note: API might use query param or endpoint path
                # Check API docs for exact implementation
                params["filter[slo_id]"] = slo_id
            
            response = self.client.get(self.API_ENDPOINT_CORRECTIONS, params=params)
            
            corrections = response.get("data", [])
            
            logger.info(f"✅ Extracted {len(corrections)} SLO corrections")
            
            return corrections
        
        except Exception as e:
            logger.error(f"❌ Error extracting SLO corrections: {e}", exc_info=True)
            raise
    
    def extract_slo_history(
        self,
        slo_id: str,
        from_ts: int,
        to_ts: int,
        target: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Extract SLO history data for a specific time range.
        
        Args:
            slo_id: SLO identifier
            from_ts: Start timestamp (Unix epoch seconds)
            to_ts: End timestamp (Unix epoch seconds)
            target: Optional target threshold to evaluate against
            
        Returns:
            SLO history with uptime, error budget, and status
            
        Example Response:
            {
              "data": {
                "series": {
                  "res_type": "time_series",
                  "interval": 86400,
                  "times": [1234567890, 1234654290, ...],
                  "values": [99.95, 99.98, 99.92, ...],
                },
                "thresholds": {...},
                "overall": {
                  "sli_value": 99.94,
                  "span_precision": 2,
                  "uptime": 99.94,
                  "history": [[1234567890, 99.95], ...]
                },
                "errors": [...]
              },
              "error": null
            }
        """
        try:
            logger.info(f"📈 Extracting SLO history for {slo_id} ({from_ts} to {to_ts})")
            
            endpoint = f"{self.API_ENDPOINT_SLOS}/{slo_id}/history"
            
            params = {
                "from_ts": from_ts,
                "to_ts": to_ts,
            }
            
            if target is not None:
                params["target"] = target
            
            response = self.client.get(endpoint, params=params)
            
            logger.info(f"✅ Extracted SLO history for {slo_id}")
            
            return response.get("data", {})
        
        except Exception as e:
            logger.error(f"❌ Error extracting SLO history for {slo_id}: {e}", exc_info=True)
            raise
    
    def extract_all_paginated(
        self,
        max_pages: int = 10,
        query: Optional[str] = None,
        tags_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract all SLOs using automatic pagination.
        
        Args:
            max_pages: Maximum number of pages to fetch (safety limit)
            query: Filter by name
            tags_query: Filter by tags
            
        Returns:
            Complete list of all SLOs across all pages
        """
        all_slos = []
        offset = 0
        page = 1
        
        logger.info(f"🔄 Starting paginated SLO extraction (max_pages={max_pages})")
        
        while page <= max_pages:
            try:
                slos = self.extract_all_slos(
                    offset=offset,
                    limit=self.DEFAULT_LIMIT,
                    query=query,
                    tags_query=tags_query,
                )
                
                if not slos:
                    logger.info(f"✅ Pagination complete - no more SLOs (page {page})")
                    break
                
                all_slos.extend(slos)
                logger.info(f"  Page {page}: {len(slos)} SLOs (total: {len(all_slos)})")
                
                # Check if we got less than limit (last page)
                if len(slos) < self.DEFAULT_LIMIT:
                    logger.info(f"✅ Pagination complete - partial page received")
                    break
                
                offset += self.DEFAULT_LIMIT
                page += 1
            
            except Exception as e:
                logger.error(f"❌ Error on page {page}: {e}")
                break
        
        logger.info(f"✅ Extracted total of {len(all_slos)} SLOs across {page} pages")
        
        return all_slos
