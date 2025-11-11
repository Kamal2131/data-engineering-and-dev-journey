import json
import re
from collections import OrderedDict
from typing import Dict, List, Generator, Optional, Iterable

DATA_FILE = "Extra_docs/contacts.json"

def normalize_phone(phone: str) -> Optional[str]:
    """Return 10-digit normalized phone (digits only), or None if invalid."""
    if not isinstance(phone, str):
        return None
    digits = re.sub(r"\D", "", phone)
    # accept local 10 digits
    if len(digits) == 10:
        return digits
    # common cases: leading 0 or country code (e.g., 91)
    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]
    if len(digits) >= 12 and digits.endswith(re.sub(r"\D", "", phone)[-10:]):
        # try last 10 if looks like CC + local
        last10 = digits[-10:]
        return last10 if len(last10) == 10 else None
    return None

def normalize_name(name: str) -> Optional[str]:
    if not isinstance(name, str):
        return None
    n = name.strip()
    return n or None

class ContactManager:
    def __init__(self, filename: str = DATA_FILE):
        self.filename = filename
        # key -> contact
        self.contacts: Dict[str, Dict[str, str]] = OrderedDict()
        # explicit ordered list for iteration
        self.contacts_list: List[Dict[str, str]] = []
        self.load()

    # ------------------ persistence ------------------

    def load(self) -> None:
        self.contacts.clear()
        self.contacts_list.clear()
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        except json.JSONDecodeError:
            return

        if not isinstance(data, list):
            return

        for raw in data:
            if not isinstance(raw, dict):
                continue
            name = normalize_name(raw.get("name", ""))
            phone_norm = normalize_phone(raw.get("phone", "")) if raw.get("phone") else None
            if not name and not phone_norm:
                continue
            key = phone_norm if phone_norm else name.lower()
            if key in self.contacts:
                continue
            contact = {"name": name or "", "phone": phone_norm or ""}
            self.contacts[key] = contact
            self.contacts_list.append(contact)

    def save(self) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.contacts_list, f, indent=2, ensure_ascii=False)

    # ------------------ operations ------------------

    def _key_for_contact_fields(self, name: Optional[str], phone: Optional[str]) -> Optional[str]:
        phone_norm = normalize_phone(phone) if phone else None
        if phone_norm:
            return phone_norm
        n = normalize_name(name) if name else None
        return n.lower() if n else None

    def add_contact(self, name: str, phone: str) -> Dict[str, str]:
        name_clean = normalize_name(name)
        if not name_clean:
            raise ValueError("Name is required.")
        phone_norm = normalize_phone(phone)
        if not phone_norm:
            raise ValueError("Phone is invalid. Provide a valid 10-digit number (country code allowed).")

        key = phone_norm
        if key in self.contacts:
            raise ValueError("Phone already exists.")

        contact = {"name": name_clean, "phone": phone_norm}
        self.contacts[key] = contact
        self.contacts_list.append(contact)
        return contact

    def view_contacts(self) -> Iterable[Dict[str, str]]:
        # generator for memory efficiency
        for c in self.contacts_list:
            yield c

    def search(self, query: str) -> Generator[Dict[str, str], None, None]:
        if not isinstance(query, str):
            return
        q = query.strip().lower()
        if not q:
            return
        for c in self.contacts_list:
            name = c.get("name", "")
            phone = c.get("phone", "")
            if (isinstance(name, str) and q in name.lower()) or (isinstance(phone, str) and q in phone):
                yield c

    def delete(self, phone_or_name: str) -> bool:
        if not isinstance(phone_or_name, str) or not phone_or_name.strip():
            return False

        phone_key = normalize_phone(phone_or_name)
        if phone_key and phone_key in self.contacts:
            contact = self.contacts.pop(phone_key)
            self._remove_from_list(contact)
            return True

        # fallback by exact name (case-insensitive)
        target = phone_or_name.strip().lower()
        removed_any = False
        for key, val in list(self.contacts.items()):
            if val.get("name", "").lower() == target:
                contact = self.contacts.pop(key)
                self._remove_from_list(contact)
                removed_any = True
        return removed_any

    def _remove_from_list(self, contact: Dict[str, str]) -> None:
        for i, c in enumerate(self.contacts_list):
            if c.get("name") == contact.get("name") and c.get("phone") == contact.get("phone"):
                del self.contacts_list[i]
                return

if __name__ == "__main__":
    cm = ContactManager()
    try:
        cm.add_contact("kkg1", "98765-43211")
        cm.add_contact("Kamal", "98765-43210")
    except Exception as e:
        print("Add error:", e)

    print("Deleted kkg1:", cm.delete("kkg1"))
    print("Search 'kamal':", list(cm.search("kamal")))
    print("All:", list(cm.view_contacts()))
    cm.save()
