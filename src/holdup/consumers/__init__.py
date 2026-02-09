"""Consumers module - reads catalog and produces outputs."""

from holdup.consumers.base import BaseConsumer
from holdup.consumers.summary import SummaryConsumer

__all__ = ["BaseConsumer", "SummaryConsumer"]
