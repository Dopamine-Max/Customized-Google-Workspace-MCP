"""
Google Contacts MCP Tools

This module provides MCP tools for interacting with the Google Contacts API.
"""

import logging
import asyncio
from typing import Optional, Dict, Any

from auth.service_decorator import require_google_service
from core.utils import handle_http_errors
from core.server import server
from auth.scopes import CONTACTS_READONLY_SCOPE, CONTACTS_SCOPE

# Configure module logger
logger = logging.getLogger(__name__)

# Helper function to format contact details for output
def _format_contact_details(person: Dict[str, Any]) -> str:
    """Formats a person object from the Contacts API into a readable string."""
    details = []
    resource_name = person.get("resourceName", "N/A")
    names = person.get("names", [])
    emails = person.get("emailAddresses", [])
    phone_numbers = person.get("phoneNumbers", [])
    
    display_name = "No Name"
    if names:
        display_name = names[0].get("displayName", "No Name")

    details.append(f"- Name: \"{display_name}\" (Resource Name: {resource_name})")

    if emails:
        email_list = [f"{e.get('value', 'N/A')}" for e in emails]
        details.append(f"  Emails: {', '.join(email_list)}")
    else:
        details.append("  Emails: None")

    if phone_numbers:
        phone_list = [f"{p.get('value', 'N/A')}" for p in phone_numbers]
        details.append(f"  Phone Numbers: {', '.join(phone_list)}")
    else:
        details.append("  Phone Numbers: None")
        
    return "\n".join(details)

@server.tool()
@handle_http_errors("search_contacts", is_read_only=True, service_type="contacts")
@require_google_service("contacts", CONTACTS_READONLY_SCOPE)
async def search_contacts(
    service,
    user_google_email: str,
    query: str,
    page_size: int = 10,
) -> str:
    """
    Searches for contacts by name or email address.

    Args:
        user_google_email (str): The user's Google email address. Required.
        query (str): The name or email to search for.
        page_size (int): The maximum number of contacts to return. Defaults to 10.

    Returns:
        str: A formatted list of found contacts with their names, emails, and resource names.
    """
    logger.info(f"[search_contacts] Invoked. Email: '{user_google_email}', Query: '{query}'")

    # The readMask specifies which fields to return for each person.
    # Add 'phoneNumbers' to the read_mask to retrieve phone numbers.
    read_mask = "names,emailAddresses,phoneNumbers"

    response = await asyncio.to_thread(
        lambda: service.people().searchContacts(
            query=query,
            pageSize=page_size,
            readMask=read_mask
        ).execute()
    )

    results = response.get("results", [])
    if not results:
        return f"No contacts found matching '{query}' for {user_google_email}."

    contact_list = [_format_contact_details(res.get("person", {})) for res in results]
    
    output = (
        f"Found {len(results)} contacts for {user_google_email} matching '{query}':\n"
        + "\n".join(contact_list)
    )
    return output

@server.tool()
@handle_http_errors("create_contact", service_type="contacts")
@require_google_service("contacts", CONTACTS_SCOPE)
async def create_contact(
    service,
    user_google_email: str,
    given_name: str,
    family_name: Optional[str] = None,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
) -> str:
    """
    Creates a new contact with a name and optional email address and phone number.

    Args:
        user_google_email (str): The user's Google email address. Required.
        given_name (str): The contact's first name.
        family_name (Optional[str]): The contact's last name.
        email (Optional[str]): The contact's email address.
        phone_number (Optional[str]): The contact's phone number.

    Returns:
        str: Confirmation message with the new contact's details.
    """
    logger.info(f"[create_contact] Invoked. Email: '{user_google_email}', Name: '{given_name} {family_name}'")

    person_body = {
        "names": [{"givenName": given_name, "familyName": family_name or ""}],
    }

    if email:
        person_body["emailAddresses"] = [{"value": email}]
    
    if phone_number:
        person_body["phoneNumbers"] = [{"value": phone_number}]

    created_person = await asyncio.to_thread(
        lambda: service.people().createContact(body=person_body).execute()
    )

    formatted_details = _format_contact_details(created_person)
    return f"Successfully created contact for {user_google_email}:\n{formatted_details}"

@server.tool()
@handle_http_errors("update_contact_email", service_type="contacts")
@require_google_service("contacts", CONTACTS_SCOPE)
async def update_contact_email(
    service,
    user_google_email: str,
    resource_name: str,
    email: str,
) -> str:
    """
    Updates a contact's email address. Use search_contacts first to get the resourceName.

    Args:
        user_google_email (str): The user's Google email address. Required.
        resource_name (str): The resource name of the contact to update (e.g., 'people/c12345').
        email (str): The new email address to add to the contact.

    Returns:
        str: Confirmation message with the updated contact's details.
    """
    logger.info(f"[update_contact_email] Invoked. Email: '{user_google_email}', Resource: '{resource_name}'")

    # First, get the contact's current state to retrieve the etag
    person_to_update = await asyncio.to_thread(
        lambda: service.people().get(
            resourceName=resource_name,
            personFields="names,emailAddresses"
        ).execute()
    )
    
    etag = person_to_update.get("etag")
    if not etag:
        raise Exception("Could not retrieve etag for contact. Update failed.")

    # Prepare the update body
    person_body = {
        "etag": etag,
        "emailAddresses": person_to_update.get("emailAddresses", []) + [{"value": email}]
    }

    updated_person = await asyncio.to_thread(
        lambda: service.people().updateContact(
            resourceName=resource_name,
            updatePersonFields="emailAddresses",
            body=person_body
        ).execute()
    )

    formatted_details = _format_contact_details(updated_person)
    return f"Successfully updated contact for {user_google_email}:\n{formatted_details}"

