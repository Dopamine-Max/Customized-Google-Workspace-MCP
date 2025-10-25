"""
Google Workspace OAuth Scopes

This module centralizes OAuth scope definitions for Google Workspace integration.
Separated from service_decorator.py to avoid circular imports.
"""
import logging

logger = logging.getLogger(__name__)

# Global variable to store enabled tools (set by main.py)
_ENABLED_TOOLS = None

# Individual OAuth Scope Constants
USERINFO_EMAIL_SCOPE = 'https://www.googleapis.com/auth/userinfo.email'
USERINFO_PROFILE_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'
OPENID_SCOPE = 'openid'

# Google Calendar scopes
CALENDAR_SCOPE = 'https://www.googleapis.com/auth/calendar'
CALENDAR_READONLY_SCOPE = 'https://www.googleapis.com/auth/calendar.readonly'
CALENDAR_EVENTS_SCOPE = 'https://www.googleapis.com/auth/calendar.events'

# Google Drive scopes
DRIVE_SCOPE = 'https://www.googleapis.com/auth/drive'
DRIVE_READONLY_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'
DRIVE_FILE_SCOPE = 'https://www.googleapis.com/auth/drive.file'

# Gmail API scopes
GMAIL_READONLY_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
GMAIL_SEND_SCOPE = 'https://www.googleapis.com/auth/gmail.send'
GMAIL_COMPOSE_SCOPE = 'https://www.googleapis.com/auth/gmail.compose'
GMAIL_MODIFY_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'
GMAIL_LABELS_SCOPE = 'https://www.googleapis.com/auth/gmail.labels'

# Google Tasks API scopes
TASKS_SCOPE = 'https://www.googleapis.com/auth/tasks'
TASKS_READONLY_SCOPE = 'https://www.googleapis.com/auth/tasks.readonly'

# Google Contacts API scopes
CONTACTS_SCOPE = 'https://www.googleapis.com/auth/contacts'
CONTACTS_READONLY_SCOPE = 'https://www.googleapis.com/auth/contacts.readonly'

# Base OAuth scopes required for user identification
BASE_SCOPES = [
    USERINFO_EMAIL_SCOPE,
    USERINFO_PROFILE_SCOPE,
    OPENID_SCOPE
]

CALENDAR_SCOPES = [
    CALENDAR_SCOPE,
    CALENDAR_READONLY_SCOPE,
    CALENDAR_EVENTS_SCOPE
]

DRIVE_SCOPES = [
    DRIVE_SCOPE,
    DRIVE_READONLY_SCOPE,
    DRIVE_FILE_SCOPE
]

GMAIL_SCOPES = [
    GMAIL_READONLY_SCOPE,
    GMAIL_SEND_SCOPE,
    GMAIL_COMPOSE_SCOPE,
    GMAIL_MODIFY_SCOPE,
    GMAIL_LABELS_SCOPE
]

TASKS_SCOPES = [
    TASKS_SCOPE,
    TASKS_READONLY_SCOPE
]

CONTACTS_SCOPES = [
    CONTACTS_SCOPE,
    CONTACTS_READONLY_SCOPE
]

# Tool-to-scopes mapping
TOOL_SCOPES_MAP = {
    'gmail': GMAIL_SCOPES,
    'drive': DRIVE_SCOPES,
    'calendar': CALENDAR_SCOPES,
    'tasks': TASKS_SCOPES,
    'contacts': CONTACTS_SCOPES
}

def set_enabled_tools(enabled_tools):
    """
    Set the globally enabled tools list.
    
    Args:
        enabled_tools: List of enabled tool names.
    """
    global _ENABLED_TOOLS
    _ENABLED_TOOLS = enabled_tools
    logger.info(f"Enabled tools set for scope management: {enabled_tools}")

def get_current_scopes():
    """
    Returns scopes for currently enabled tools.
    Uses globally set enabled tools or all tools if not set.
    
    Returns:
        List of unique scopes for the enabled tools plus base scopes.
    """
    enabled_tools = _ENABLED_TOOLS
    if enabled_tools is None:
        # Default behavior - return all scopes
        enabled_tools = TOOL_SCOPES_MAP.keys()
    
    # Start with base scopes (always required)
    scopes = BASE_SCOPES.copy()
    
    # Add scopes for each enabled tool
    for tool in enabled_tools:
        if tool in TOOL_SCOPES_MAP:
            scopes.extend(TOOL_SCOPES_MAP[tool])
    
    logger.debug(f"Generated scopes for tools {list(enabled_tools)}: {len(set(scopes))} unique scopes")
    # Return unique scopes
    return list(set(scopes))

def get_scopes_for_tools(enabled_tools=None):
    """
    Returns scopes for enabled tools only.
    
    Args:
        enabled_tools: List of enabled tool names. If None, returns all scopes.
    
    Returns:
        List of unique scopes for the enabled tools plus base scopes.
    """
    if enabled_tools is None:
        # Default behavior - return all scopes
        enabled_tools = TOOL_SCOPES_MAP.keys()
    
    # Start with base scopes (always required)
    scopes = BASE_SCOPES.copy()
    
    # Add scopes for each enabled tool
    for tool in enabled_tools:
        if tool in TOOL_SCOPES_MAP:
            scopes.extend(TOOL_SCOPES_MAP[tool])
    
    # Return unique scopes
    return list(set(scopes))

# Combined scopes for all supported Google Workspace operations (backwards compatibility)
SCOPES = get_scopes_for_tools()