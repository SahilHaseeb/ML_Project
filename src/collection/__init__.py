"""
src/collection
--------------
Modular job data collection pipeline for permitted APIs, feeds, and open datasets.
"""
from src.collection.base import BaseCollector
from src.collection.api_collectors import RemotiveCollector, ArbeitnowCollector
from src.collection.pipeline import CollectionPipeline

__all__ = [
    "BaseCollector",
    "RemotiveCollector",
    "ArbeitnowCollector",
    "CollectionPipeline",
]
