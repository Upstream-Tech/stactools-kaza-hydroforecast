import logging
from pathlib import Path

import pandas as pd
import stac_table
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    Link,
    MediaType,
    Provider,
    ProviderRole,
    SpatialExtent,
    TemporalExtent,
)
from pystac.extensions.item_assets import ItemAssetsExtension

from .constants import (
    COLLECTION_EXTRA_FIELDS,
    COLLECTION_THUMBNAIL_HREF,
    FILENAME_PREFIX,
    FORECAST_POINT_GEOMETRIES_BY_SITE,
    FORECASTS_START_DATETIME,
)

logger = logging.getLogger(__name__)


def create_collection() -> Collection:
    """
    Create a STAC Collection of HydroForecast seasonal river flow forecast data files.

    See `The interactive public dashboard containing this data and further information
         <https://dashboard.hydroforecast.com/public/wwf-kaza>`_.

    Returns:
        Collection: STAC Collection object
    """
    providers = [
        Provider(
            name="Upstream Tech",
            roles=[
                ProviderRole.PRODUCER,
                ProviderRole.PROCESSOR,
                ProviderRole.LICENSOR,
            ],
            url="https://www.upstream.tech",
        ),
        Provider(
            name="Microsoft",
            roles=[ProviderRole.HOST],
            url="https://planetarycomputer.microsoft.com",
        ),
    ]

    # Produce one extent covering all forecast points
    forecast_point_coordinates_x_y = [
        geometry["coordinates"]
        for geometry in FORECAST_POINT_GEOMETRIES_BY_SITE.values()
    ]
    forecast_point_x, forecast_point_y = zip(*forecast_point_coordinates_x_y)
    forecast_point_bounds = [
        min(forecast_point_x),
        min(forecast_point_y),
        max(forecast_point_x),
        max(forecast_point_y),
    ]
    spatial_extents = [forecast_point_bounds]

    # Produce an extent for each forecast point
    forecast_point_coordinates_x_y = [
        geometry["coordinates"]
        for geometry in FORECAST_POINT_GEOMETRIES_BY_SITE.values()
    ]
    spatial_extents = [
        [coord[0], coord[1], coord[0], coord[1]]
        for coord in forecast_point_coordinates_x_y
    ]

    extent = Extent(
        SpatialExtent(spatial_extents),
        TemporalExtent([[FORECASTS_START_DATETIME, None]]),
    )

    collection = Collection(
        id="kaza-hydroforecast",
        title="HydroForecast - Kwando & Upper Zambezi Rivers",
        description=COLLECTION_EXTRA_FIELDS["msft:short_description"],
        license="CDLA-Sharing-1.0",
        providers=providers,
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
        extra_fields=COLLECTION_EXTRA_FIELDS,
    )

    collection.add_asset(
        "thumbnail",
        Asset(
            COLLECTION_THUMBNAIL_HREF,
            title="Thumbnail",
            media_type=MediaType.PNG,
            roles=["thumbnail"],
        ),
    )

    collection.links = [
        Link(
            rel="license",
            target="https://cdla.dev/sharing-1-0/",
            title="Community Data License Agreement – Sharing, Version 1.0",
            media_type="text/html",
        )
    ]

    ItemAssetsExtension.add_to(collection)
    collection.extra_fields["item_assets"] = {
        "data": {
            "type": stac_table.PARQUET_MEDIA_TYPE,
            "title": "River flow forecasts",
            "roles": ["data"],
            "description": "All seasonal river flow forecasts for a specific forecast site, "
            "produced by Upstream Tech's HydroForecast model",
        }
    }

    return collection


def create_item(asset_path, protocol=None, storage_options=None, asset_extra_fields=None) -> Item:
    """
    Create a STAC Item representing a forecast data file for a single site.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item
        protocol (str, optional): The fsspec protocol to use with the asset_pth.
        storage_options (dict, optional): Passed through to pandas.read_parquet
           when reading the asset.
        asset_extra_fields (dict, optional): Extra fields set on the returned
           item's `data` asset.

    Returns:
        Item: STAC Item object
    """
    storage_options = storage_options or {}
    asset_extra_fields = asset_extra_fields or {}
    if protocol:
        asset_href = f"{protocol}://{asset_path}"
    else:
        asset_href = asset_path

    site = Path(asset_path).stem.replace(FILENAME_PREFIX, "").replace("_", "-")
    site_name = site.replace("-", " ").title()

    df = pd.read_parquet(asset_href, storage_options=storage_options)

    table_columns = [
        {
            "name": col,
            "type": _get_column_type_string(col),
            "description": _get_column_description(col),
        }
        for col in df.columns
    ]

    properties = {
        "title": site_name,
        "description": f"Streamflow Forecasts for {site_name}",
        "start_datetime": df["valid_time"].min().isoformat(),
        "end_datetime": df["valid_time"].max().isoformat(),
        "table:columns": table_columns,
        "table:row_count": len(df),
    }

    geometry = FORECAST_POINT_GEOMETRIES_BY_SITE[site]
    x, y = geometry["coordinates"]
    bbox = [x, y, x, y]

    item = Item(
        id=site,
        properties=properties,
        geometry=geometry,
        bbox=bbox,
        datetime=None,  # start|end_datetime are provided in properties
        stac_extensions=[stac_table.SCHEMA_URI],
    )

    item.add_asset(
        "data",
        Asset(
            asset_href,
            title="Forecast Data",
            media_type=stac_table.PARQUET_MEDIA_TYPE,
            roles=["data"],
            extra_fields=asset_extra_fields,
        ),
    )

    return item


def _get_column_type_string(name: str) -> str:
    if name == "lead_time_hours":
        return "int64"
    elif name.endswith("_time"):
        return "timestamp"
    elif name.startswith("discharge"):
        return "double"
    else:
        raise ValueError(f"Data type string not known for column {name}")


def _get_column_description(name: str) -> str:
    if name == "initialization_time":
        return (
            "The initial timestamp in the forecast model which created this forecast step. "
            'All rows with the same initialization time are part of the same "forecast" and '
            "are produced at the same time."
        )
    elif name == "lead_time_hours":
        return "The number of hours ahead of the initialization time this forecast step is predicting."
    elif name == "valid_time":
        return (
            "The point in time this forecast step is predicting. "
            "valid_time = initialization_time + lead_time_hours. "
            "The discharge values in this row are the average rate from this time (inclusive) "
            "until the next valid time (exclusive)."
        )
    elif name.startswith("discharge_q"):
        quantile = float(name.split("_q")[-1])
        return (
            f"The quantile {quantile} of the probabilistic streamflow prediction, as an average "
            "rate across the forecast step in m³/s."
        )
    elif name == "discharge_mean":
        return (
            f"The mean of the probabilistic streamflow prediction, as an average rate across "
            "the forecast step in m³/s."
        )
    elif name == "discharge_median":
        return (
            f"The median of the probabilistic streamflow prediction, as an average rate across "
            "the forecast step in m³/s."
        )
    else:
        raise ValueError(f"Column description not known for column {name}")
