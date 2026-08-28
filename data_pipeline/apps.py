"""
App configuration for data_pipeline module.

:Example:

>>> from data_pipeline.apps import DataPipelineConfig
>>> print(DataPipelineConfig.name)
'data_pipeline'
"""

from django.apps import AppConfig


class DataPipelineConfig(AppConfig):
    """
    Django AppConfig for data_pipeline application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_pipeline"
