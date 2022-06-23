from datetime import datetime, timezone

FORECASTS_START_DATETIME = datetime(2022, 1, 1, tzinfo=timezone.utc)

FORECAST_POINT_GEOMETRIES_BY_SITE = {
    "kwando-river-at-kongola": {
        "type": "Point",
        "coordinates": (23.343421, -17.792517),
    },
    "kongola-local": {"type": "Point", "coordinates": (23.343421, -17.792517)},
    "kwando-sub-basin-1": {"type": "Point", "coordinates": (21.04494, -15.13158)},
    "kwando-sub-basin-2": {"type": "Point", "coordinates": (21.80157, -16.01209)},
    "kwando-sub-basin-3": {"type": "Point", "coordinates": (22.91715, -17.38856)},
    "kwando-sub-basin-4": {"type": "Point", "coordinates": (23.006105, -17.347398)},
    "luanginga-at-kalabo": {"type": "Point", "coordinates": (22.669092, -14.971843)},
    "zambezi-at-chavuma": {"type": "Point", "coordinates": (22.675487, -13.08062)},
    # These are deprecated site ids
    # now luanginga-at-kalabo
    "bar-4-zambezi": {
        "type": "Point",
        "coordinates": (22.669092, -14.971843),
    },
    # now zambezi-at-chavuma
    "bar-7-zambezi": {
        "type": "Point",
        "coordinates": (22.675487, -13.08062),
    },
}

FILENAME_PREFIX = "hydroforecast_seasonal_"

COLLECTION_THUMBNAIL_HREF = "https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_thumbnails/kaza-hydroforecast-thumbnail.png"

COLLECTION_EXTRA_FIELDS = {
    "version": "1.0.0",
    "msft:storage_account": "ai4edataeuwest",
    "msft:container": "hydroforecast",
    "msft:short_description": "Seasonal river flow forecasts for the Kwando and "
    "Upper Zambezi rivers in the KAZA region of Africa, "
    "produced by Upstream Tech's HydroForecast model.",
}
