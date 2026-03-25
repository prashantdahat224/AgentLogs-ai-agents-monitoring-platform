from pydantic import BaseModel
from typing import Optional, List

# Example: Contact model
class Contact(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

# Example: API Response
class MessageResponse(BaseModel):
    message: str

# Example: User model
class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str