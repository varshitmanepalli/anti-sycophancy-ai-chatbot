"""Pydantic schemas — API request/response DTOs.

Data transfer objects for the HTTP layer. Separate from domain entities
and SQLAlchemy ORM models to avoid leaking persistence details to clients.
"""
