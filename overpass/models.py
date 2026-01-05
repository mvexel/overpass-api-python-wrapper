# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any
    bbox: Optional[list[float]] = None

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.model_dump()


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    id: Optional[Any] = None
    bbox: Optional[list[float]] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    geometry: Optional[GeoJSONGeometry] = None

    def to_geojson(self) -> str:
        return self.model_dump_json()

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.model_dump()


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    bbox: Optional[list[float]] = None
    features: list[GeoJSONFeature] = Field(default_factory=list)

    def to_geojson(self) -> str:
        return self.model_dump_json()

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.model_dump()


class OverpassElement(BaseModel):
    type: str
    id: int
    tags: Optional[dict[str, Any]] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    nodes: Optional[list[int]] = None
    members: Optional[list[dict[str, Any]]] = None


class OverpassResponse(BaseModel):
    elements: list[OverpassElement] = Field(default_factory=list)
    version: Optional[float] = None
    generator: Optional[str] = None
    osm3s: Optional[dict[str, Any]] = None
    remark: Optional[str] = None


class CsvResponse(BaseModel):
    header: list[str]
    rows: list[list[str]]


class XmlResponse(BaseModel):
    text: str
