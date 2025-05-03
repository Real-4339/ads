import json

from pathlib import Path
from loguru import logger
from pydantic import BaseModel, field_validator, RootModel


class FilterItem(BaseModel):
    """Model for filter data associated with a specific name"""

    property: list[str]


class FilterDict(RootModel):
    """Filter list model"""

    root: dict[str, FilterItem]

    @field_validator("root")
    def validate_unique_names(
        cls, root: dict[str, FilterItem]
    ) -> dict[str, FilterItem]:
        """Check if filter names are unique"""
        if len(root) != len(set(root.keys())):
            logger.error("Filter names are not unique")
            raise ValueError("Filter names are not unique")
        return root


class Config:

    def __init__(self) -> None:
        self.filters = self.read_filters()

    def read_filters(self) -> dict[str, FilterItem]:
        """Read filters from config file"""

        filters_path = Path(__file__).parent
        flist = None

        try:
            with open(filters_path / "filters.json", "r") as f:
                config = json.load(f)

            # Read multiple digits
            flist = FilterDict(**config)

        except Exception as e:
            logger.error(f"Encountered an error: {e}")
            logger.info("Using no filter file.")

            flist = FilterDict(root={})

        return flist.root
