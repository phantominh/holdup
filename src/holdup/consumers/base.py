"""Base classes for consumers."""

from abc import ABC, abstractmethod

from holdup.catalog import CatalogArticle


class BaseConsumer(ABC):
    """Abstract base class for catalog consumers."""

    @abstractmethod
    def consume(self, catalog: dict[str, list[CatalogArticle]], date_str: str) -> None:
        """
        Consume the catalog and produce output.

        Args:
            catalog: Dictionary mapping ticker to list of CatalogArticle objects
            date_str: Date string in ISO format (YYYY-MM-DD)
        """
        pass
