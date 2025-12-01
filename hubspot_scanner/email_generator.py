"""
Email generation for technology-based outreach.

Generates personalized cold outreach emails based on detected technologies,
following best practices for consultant-style outreach.
"""

import random
from dataclasses import dataclass
from typing import Any

from .tech_scorer import ScoredTechnology, get_highest_value_tech


# Consultant profile configuration
CONSULTANT_PROFILE = {
    "name": "Chris",
    "location": "Richmond, VA",
    "hourly_rate": "$85/hr",
    "github": "https://github.com/inevitablesale",
    "calendly": "https://calendly.com/inevitable-sale/hubspot-systems-consultation",
    "positioning": "short-term technical consultant",
}


@dataclass
class GeneratedEmail:
    """Generated outreach email with metadata."""

    domain: str
    selected_technology: str
    recent_project: str
    subject_lines: list[str]
    email_body: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "domain": self.domain,
            "selected_technology": self.selected_technology,
            "recent_project": self.recent_project,
            "subject_lines": self.subject_lines,
            "email_body": self.email_body,
        }


def generate_subject_lines(tech_name: str, category: str) -> list[str]:
    """
    Generate 3 subject lines for the outreach email.

    Args:
        tech_name: The selected technology name
        category: The technology category

    Returns:
        List of 3 subject lines
    """
    # Subject line templates by category
    templates = {
        "Ecommerce": [
            f"Quick {tech_name} question",
            f"{tech_name} help from Richmond",
            f"Your {tech_name} setup",
            f"Short-term {tech_name} help?",
            f"Noticed your {tech_name} store",
        ],
        "Payment Processor": [
            f"{tech_name} integration help",
            f"Quick {tech_name} question",
            f"Payment flow thoughts",
            f"Richmond-based {tech_name} help",
        ],
        "Email Marketing": [
            f"{tech_name} automation ideas",
            f"Quick {tech_name} thought",
            f"Email flow improvements",
            f"Noticed your {tech_name} setup",
        ],
        "Marketing Automation": [
            f"{tech_name} workflow ideas",
            f"Quick automation thought",
            f"Noticed your {tech_name} setup",
            f"Short-term {tech_name} help",
        ],
        "CRM": [
            f"{tech_name} workflow question",
            f"Quick CRM thought",
            f"Noticed your {tech_name}",
            f"Richmond {tech_name} consultant",
        ],
        "Live Chat": [
            f"{tech_name} routing idea",
            f"Quick chat flow thought",
            f"Noticed your {tech_name}",
        ],
        "Analytics": [
            f"Tracking question",
            f"{tech_name} setup thoughts",
            f"Analytics improvement idea",
            f"Quick data question",
        ],
        "A/B Testing": [
            f"{tech_name} experiment idea",
            f"Quick testing thought",
            f"Optimization question",
        ],
        "CMS": [
            f"{tech_name} performance idea",
            f"Quick site thought",
            f"Noticed your {tech_name} site",
        ],
        "Infrastructure": [
            f"Quick infrastructure thought",
            f"Performance question",
            f"Technical help available",
        ],
        "Customer Data Platform": [
            f"{tech_name} integration idea",
            f"Data flow question",
            f"CDP optimization thought",
        ],
    }

    # Get templates for this category, or use generic ones
    category_templates = templates.get(
        category,
        [
            f"Quick {tech_name} question",
            f"Short-term help available",
            f"Technical consultant in Richmond",
        ],
    )

    # Select 3 random subject lines
    if len(category_templates) >= 3:
        return random.sample(category_templates, 3)
    else:
        # Pad with generic templates if needed
        generic = [
            f"Quick {tech_name} question",
            f"Short-term technical help",
            f"Richmond-based consultant",
        ]
        combined = category_templates + generic
        return random.sample(combined, min(3, len(combined)))


def generate_email_body(
    domain: str,
    tech: ScoredTechnology,
    profile: dict[str, str] | None = None,
) -> str:
    """
    Generate the email body for outreach.

    Args:
        domain: The target domain
        tech: The selected technology with scoring info
        profile: Optional consultant profile override

    Returns:
        The generated email body (under 180 words)
    """
    p = profile or CONSULTANT_PROFILE

    # Build the email
    email = f"""Hey there,

I was looking at {domain} and noticed you're using {tech.name}. I'm {p['name']}, a {p['positioning']} based in {p['location']}.

I recently {tech.recent_project} It's the kind of short-term work I specialize in—no agency overhead, just direct technical help.

I handle {tech.category.lower()}, automation, CRM, and analytics tasks at {p['hourly_rate']}. Not looking to replace anyone on your team or become a long-term fixture—just available if you ever need a hand with something specific.

If that's useful, happy to chat: {p['calendly']}

You can also see my work here: {p['github']}

Either way, hope things are going well with {tech.name}.

– {p['name']}"""

    return email


def generate_outreach_email(
    domain: str,
    technologies: list[str],
    profile: dict[str, str] | None = None,
) -> GeneratedEmail | None:
    """
    Generate a complete outreach email for a domain.

    Args:
        domain: The target domain
        technologies: List of detected technology names
        profile: Optional consultant profile override

    Returns:
        GeneratedEmail object, or None if no technologies detected
    """
    if not technologies:
        return None

    # Get the highest-value technology
    top_tech = get_highest_value_tech(technologies)
    if not top_tech:
        return None

    # Generate subject lines
    subject_lines = generate_subject_lines(top_tech.name, top_tech.category)

    # Generate email body
    email_body = generate_email_body(domain, top_tech, profile)

    return GeneratedEmail(
        domain=domain,
        selected_technology=top_tech.name,
        recent_project=top_tech.recent_project,
        subject_lines=subject_lines,
        email_body=email_body,
    )
