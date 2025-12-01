"""HubSpot Presence Scanner - Detect HubSpot usage on websites."""

from .detector import HubSpotDetector, DetectionResult
from .scanner import scan_domains, scan_domain
from .email_extractor import (
    extract_emails_from_html,
    crawl_for_emails,
    is_disposable_email,
    load_disposable_domains,
)

# Wappalyzer-style multi-technology detection
from .tech_detector import TechDetector, TechDetectionResult
from .tech_scorer import (
    score_technologies,
    get_highest_value_tech,
    ScoredTechnology,
    TECH_SCORES,
    RECENT_PROJECTS,
)
from .email_generator import (
    generate_outreach_email,
    generate_subject_lines,
    generate_email_body,
    GeneratedEmail,
    CONSULTANT_PROFILE,
)
from .tech_scanner import (
    scan_technologies,
    scan_technologies_batch,
    TechScanResult,
)

__version__ = "1.0.0"
__all__ = [
    # HubSpot-specific detection
    "HubSpotDetector",
    "DetectionResult",
    "scan_domains",
    "scan_domain",
    "extract_emails_from_html",
    "crawl_for_emails",
    "is_disposable_email",
    "load_disposable_domains",
    # Multi-technology detection (Wappalyzer-style)
    "TechDetector",
    "TechDetectionResult",
    "score_technologies",
    "get_highest_value_tech",
    "ScoredTechnology",
    "TECH_SCORES",
    "RECENT_PROJECTS",
    # Email generation
    "generate_outreach_email",
    "generate_subject_lines",
    "generate_email_body",
    "GeneratedEmail",
    "CONSULTANT_PROFILE",
    # Unified scanner
    "scan_technologies",
    "scan_technologies_batch",
    "TechScanResult",
]
