"""
datadog_slo_transformer.py
==========================

Transform Datadog SLO responses to RAG-optimized documents.

This module converts raw SLO JSON from the API into
Markdown-formatted documents optimized for:
  - SentenceTransformer embeddings
  - RAG queries about SLO status, thresholds, and reliability
  - Natural language understanding of service objectives
  - Performance analysis and troubleshooting
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SLOTransformer:
    """
    Transform SLOs and corrections to RAG-optimized markdown documents.
    
    Follows Open/Closed Principle:
      - Closed for modification (stable interface)
      - Open for extension (new transform methods)
    """
    
    def __init__(self):
        pass
    
    def transform_slo(
        self,
        slo: Dict[str, Any],
        include_monitors: bool = True,
        include_thresholds: bool = True,
    ) -> str:
        """
        Transform a single SLO to markdown.
        
        Args:
            slo: SLO dictionary from API
            include_monitors: Whether to include monitor details
            include_thresholds: Whether to include threshold details
            
        Returns:
            Markdown-formatted string optimized for RAG
            
        Example Input:
            {
              "id": "abc123",
              "name": "API Availability",
              "description": "99.9% uptime for payment API",
              "type": "metric",
              "tags": ["env:prod", "team:platform"],
              "thresholds": [
                {"target": 99.9, "timeframe": "7d", "warning": 99.5},
                {"target": 99.95, "timeframe": "30d", "warning": 99.85}
              ],
              "monitor_ids": [123456, 789012],
              "created_at": 1234567890
            }
        
        Example Output:
            # SLO: API Availability
            
            **ID**: abc123
            **Type**: metric
            **Status**: Active
            
            ## Description
            99.9% uptime for payment API
            
            ## Targets & Thresholds
            - **7 days**: 99.9% target (warning at 99.5%)
            - **30 days**: 99.95% target (warning at 99.85%)
            
            ## Configuration
            **Tags**: env:prod, team:platform
            **Monitors**: 2 monitors attached
            **Created**: 2009-02-13 23:31:30 UTC
        """
        try:
            slo_id = slo.get("id", "unknown")
            name = slo.get("name", "Unnamed SLO")
            description = slo.get("description", "")
            slo_type = slo.get("type", "unknown")
            tags = slo.get("tags", [])
            thresholds = slo.get("thresholds", [])
            monitor_ids = slo.get("monitor_ids", [])
            monitor_tags = slo.get("monitor_tags", [])
            created_at = slo.get("created_at")
            modified_at = slo.get("modified_at")
            creator = slo.get("creator", {})
            
            # Build document
            sections = []
            
            # Header
            sections.append(f"# SLO: {name}")
            sections.append("")
            sections.append(f"**ID**: {slo_id}")
            sections.append(f"**Type**: {slo_type}")
            
            # Status (if available)
            if "status" in slo:
                status = slo.get("status", {})
                state = status.get("state", "unknown")
                sections.append(f"**Status**: {state}")
            
            # Description
            if description:
                sections.append("")
                sections.append("## Description")
                sections.append(description)
            
            # Thresholds
            if include_thresholds and thresholds:
                sections.append("")
                sections.append("## Targets & Thresholds")
                sections.extend(self._format_thresholds(thresholds))
            
            # Configuration
            sections.append("")
            sections.append("## Configuration")
            
            if tags:
                sections.append(f"**Tags**: {', '.join(tags)}")
            
            if monitor_ids and include_monitors:
                sections.append(f"**Monitors**: {len(monitor_ids)} monitors attached")
                sections.append(f"  Monitor IDs: {', '.join(map(str, monitor_ids[:5]))}")
                if len(monitor_ids) > 5:
                    sections.append(f"  ... and {len(monitor_ids) - 5} more")
            
            if monitor_tags:
                sections.append(f"**Monitor Tags**: {', '.join(monitor_tags)}")
            
            # Metadata
            if created_at:
                created_date = self._format_timestamp(created_at)
                sections.append(f"**Created**: {created_date}")
            
            if modified_at:
                modified_date = self._format_timestamp(modified_at)
                sections.append(f"**Last Modified**: {modified_date}")
            
            if creator:
                creator_name = creator.get("name", creator.get("email", "Unknown"))
                sections.append(f"**Creator**: {creator_name}")
            
            return "\n".join(sections)
        
        except Exception as e:
            logger.error(f"Error transforming SLO: {e}", exc_info=True)
            return f"# SLO: {slo.get('name', 'Unknown')}\n\n**Error**: Unable to transform SLO data"
    
    def _format_thresholds(self, thresholds: List[Dict[str, Any]]) -> List[str]:
        """
        Format SLO thresholds into readable lines.
        
        Args:
            thresholds: List of threshold dictionaries
            
        Returns:
            List of formatted strings
        """
        lines = []
        
        for threshold in thresholds:
            target = threshold.get("target", 0)
            target_display = threshold.get("target_display", str(target))
            timeframe = threshold.get("timeframe", "unknown")
            warning = threshold.get("warning")
            
            line = f"- **{timeframe}**: {target_display}% target"
            
            if warning is not None:
                line += f" (warning at {warning}%)"
            
            lines.append(line)
        
        return lines
    
    def _format_timestamp(self, timestamp: int) -> str:
        """
        Format Unix timestamp to human-readable string.
        
        Args:
            timestamp: Unix epoch timestamp (seconds)
            
        Returns:
            Formatted date string
        """
        try:
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception:
            return str(timestamp)
    
    def transform_slo_correction(
        self,
        correction: Dict[str, Any],
    ) -> str:
        """
        Transform an SLO correction/maintenance window to markdown.
        
        Args:
            correction: Correction dictionary from API
            
        Returns:
            Markdown-formatted string
            
        Example Input:
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
                "rrule": "FREQ=WEEKLY;BYDAY=SU",
                "created_at": 1234567800,
                "creator": {"name": "John Doe", "email": "john@example.com"}
              }
            }
        
        Example Output:
            # SLO Correction: Scheduled Maintenance
            
            **Correction ID**: corr-123
            **SLO ID**: abc123
            **Category**: Scheduled Maintenance
            
            ## Description
            Database migration
            
            ## Schedule
            **Start**: 2009-02-13 23:31:30 UTC
            **End**: 2009-02-14 00:31:30 UTC
            **Duration**: 1 hour
            **Timezone**: UTC
            **Recurrence**: FREQ=WEEKLY;BYDAY=SU (Every Sunday)
            
            ## Metadata
            **Created**: 2009-02-13 23:30:00 UTC
            **Creator**: John Doe (john@example.com)
        """
        try:
            corr_id = correction.get("id", "unknown")
            corr_type = correction.get("type", "correction")
            attributes = correction.get("attributes", {})
            
            category = attributes.get("category", "Unknown")
            description = attributes.get("description", "")
            start = attributes.get("start")
            end = attributes.get("end")
            duration = attributes.get("duration")
            slo_id = attributes.get("slo_id", "unknown")
            timezone_str = attributes.get("timezone", "UTC")
            rrule = attributes.get("rrule")
            created_at = attributes.get("created_at")
            modified_at = attributes.get("modified_at")
            creator = attributes.get("creator", {})
            modifier = attributes.get("modifier", {})
            
            # Build document
            sections = []
            
            # Header
            sections.append(f"# SLO Correction: {category}")
            sections.append("")
            sections.append(f"**Correction ID**: {corr_id}")
            sections.append(f"**SLO ID**: {slo_id}")
            sections.append(f"**Type**: {corr_type}")
            sections.append(f"_Technical keys: slo_id, correction_id, attributes, category, description_")
            sections.append(f"**Category**: {category}")
            
            # Description
            if description:
                sections.append("")
                sections.append("## Description")
                sections.append(description)
            
            # Schedule
            sections.append("")
            sections.append("## Schedule")
            
            if start:
                sections.append(f"**Start**: {self._format_timestamp(start)}")
            
            if end:
                sections.append(f"**End**: {self._format_timestamp(end)}")
            
            if duration:
                duration_str = self._format_duration(duration)
                sections.append(f"**Duration**: {duration_str}")
            
            sections.append(f"**Timezone**: {timezone_str}")
            
            if rrule:
                readable_rrule = self._format_rrule(rrule)
                sections.append(f"**Recurrence**: {rrule} ({readable_rrule})")
            
            # Metadata
            sections.append("")
            sections.append("## Metadata")
            
            if created_at:
                sections.append(f"**Created**: {self._format_timestamp(created_at)}")
            
            if modified_at:
                sections.append(f"**Last Modified**: {self._format_timestamp(modified_at)}")
            
            if creator:
                creator_name = creator.get("name", "Unknown")
                creator_email = creator.get("email", "")
                creator_str = f"{creator_name}"
                if creator_email:
                    creator_str += f" ({creator_email})"
                sections.append(f"**Creator**: {creator_str}")
            
            if modifier:
                modifier_name = modifier.get("name", "Unknown")
                modifier_email = modifier.get("email", "")
                modifier_str = f"{modifier_name}"
                if modifier_email:
                    modifier_str += f" ({modifier_email})"
                sections.append(f"**Last Modified By**: {modifier_str}")
            
            # Add technical fields section for better RAG retrieval
            sections.append("")
            sections.append("## Technical Fields (Raw JSON Keys)")
            sections.append(f"**slo_id**: {slo_id}")
            sections.append(f"**correction_id**: {corr_id}")
            sections.append(f"**category**: {category}")
            sections.append(f"**type**: {corr_type}")
            if attributes:
                key_attrs = ["duration", "timezone", "rrule", "start", "end"]
                for key in key_attrs:
                    if key in attributes:
                        sections.append(f"**attributes.{key}**: {attributes[key]}")
            
            return "\n".join(sections)
        
        except Exception as e:
            logger.error(f"Error transforming SLO correction: {e}", exc_info=True)
            return f"# SLO Correction\n\n**Error**: Unable to transform correction data"
    
    def _format_duration(self, seconds: int) -> str:
        """
        Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minutes"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hours"
        else:
            days = seconds // 86400
            return f"{days} days"
    
    def _format_rrule(self, rrule: str) -> str:
        """
        Convert RRULE to human-readable format.
        
        Args:
            rrule: RRULE string (RFC 5545 format)
            
        Returns:
            Human-readable recurrence description
        """
        # Simple parsing - can be enhanced with rrule library
        if "FREQ=DAILY" in rrule:
            if "INTERVAL=1" in rrule or "INTERVAL" not in rrule:
                return "Every day"
            else:
                # Extract interval
                import re
                match = re.search(r"INTERVAL=(\d+)", rrule)
                if match:
                    interval = match.group(1)
                    return f"Every {interval} days"
                return "Daily"
        
        elif "FREQ=WEEKLY" in rrule:
            days = ""
            if "BYDAY=" in rrule:
                import re
                match = re.search(r"BYDAY=([A-Z,]+)", rrule)
                if match:
                    days = f" on {match.group(1)}"
            return f"Every week{days}"
        
        elif "FREQ=MONTHLY" in rrule:
            return "Every month"
        
        elif "FREQ=YEARLY" in rrule:
            return "Every year"
        
        else:
            return "Custom schedule"
    
    def transform_slos_batch(
        self,
        slos: List[Dict[str, Any]],
        max_docs: Optional[int] = None,
    ) -> List[str]:
        """
        Transform multiple SLOs to individual documents.
        
        Args:
            slos: List of SLOs from API
            max_docs: Limit number of documents (None = all)
            
        Returns:
            List of markdown documents
        """
        docs = []
        
        for i, slo in enumerate(slos):
            if max_docs and i >= max_docs:
                break
            
            try:
                doc = self.transform_slo(slo)
                if doc:
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Error transforming SLO {i}: {e}")
        
        logger.info(f"Transformed {len(docs)} SLOs to documents")
        return docs
    
    def transform_corrections_batch(
        self,
        corrections: List[Dict[str, Any]],
        max_docs: Optional[int] = None,
    ) -> List[str]:
        """
        Transform multiple corrections to individual documents.
        
        Args:
            corrections: List of corrections from API
            max_docs: Limit number of documents (None = all)
            
        Returns:
            List of markdown documents
        """
        docs = []
        
        for i, correction in enumerate(corrections):
            if max_docs and i >= max_docs:
                break
            
            try:
                doc = self.transform_slo_correction(correction)
                if doc:
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Error transforming correction {i}: {e}")
        
        logger.info(f"Transformed {len(docs)} corrections to documents")
        return docs
    
    def create_consolidated_slo_doc(
        self,
        slo: Dict[str, Any],
        corrections: Optional[List[Dict[str, Any]]] = None,
        history: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a comprehensive SLO profile document.
        
        Combines SLO info, corrections, and history into one RAG document.
        
        Args:
            slo: Main SLO dict
            corrections: Related corrections/maintenance windows
            history: SLO history data
            
        Returns:
            Consolidated markdown document
        """
        sections = []
        
        # Main SLO
        sections.append(self.transform_slo(slo))
        
        # Corrections
        if corrections:
            sections.append("")
            sections.append("---")
            sections.append("")
            sections.append("# Related Maintenance Windows")
            sections.append(f"\nThis SLO has {len(corrections)} scheduled correction(s):\n")
            
            for correction in corrections[:5]:  # Show first 5
                sections.append(self.transform_slo_correction(correction))
                sections.append("")
            
            if len(corrections) > 5:
                sections.append(f"\n... and {len(corrections) - 5} more corrections")
        
        # History summary
        if history:
            sections.append("")
            sections.append("---")
            sections.append("")
            sections.append("# Historical Performance")
            sections.extend(self._format_history_summary(history))
        
        return "\n".join(sections)
    
    def _format_history_summary(self, history: Dict[str, Any]) -> List[str]:
        """
        Format SLO history data into summary.
        
        Args:
            history: History data from API
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        overall = history.get("overall", {})
        sli_value = overall.get("sli_value")
        uptime = overall.get("uptime")
        
        if sli_value is not None:
            lines.append(f"**Current SLI Value**: {sli_value}%")
        
        if uptime is not None:
            lines.append(f"**Overall Uptime**: {uptime}%")
        
        # Add more history details as needed
        series = history.get("series", {})
        if series:
            times = series.get("times", [])
            values = series.get("values", [])
            
            if times and values:
                lines.append(f"\n**Data Points**: {len(times)} measurements")
                
                if values:
                    avg_value = sum(values) / len(values)
                    min_value = min(values)
                    max_value = max(values)
                    
                    lines.append(f"  - Average: {avg_value:.2f}%")
                    lines.append(f"  - Min: {min_value:.2f}%")
                    lines.append(f"  - Max: {max_value:.2f}%")
        
        return lines
