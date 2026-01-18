"""Database package for MongoDB Atlas integration."""

from .mongodb import user_manager, UserManager

__all__ = ["user_manager", "UserManager"]

