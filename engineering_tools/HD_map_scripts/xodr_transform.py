# Copyright 2025 Leidos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script transforms an XODR file by updating the geoReference and rotating the coordinates.
It reads the input XODR file, extracts the original latitude and longitude from the geoReference tag,
applies a transformation to the coordinates, and writes the modified data to a new XODR file.
The script can be run from the command line with the following arguments:
- input_file: The path to the input XODR file.
- output_file: The path to the output XODR file.
Dependency:
- pip install pyproj argparse lxml
Usage:
    python3 xodr_transform.py <input_file> <output_file>
"""

from lxml import etree
from pyproj import CRS, Transformer
import math
import re


def extract_lat_lon_from_georeference(geo_text):
    """Extracts lat_0 and lon_0 from the geoReference WKT string."""
    lat_match = re.search(r"\+lat_0=([-+]?[0-9]*\.?[0-9]+)", geo_text)
    lon_match = re.search(r"\+lon_0=([-+]?[0-9]*\.?[0-9]+)", geo_text)
    if lat_match and lon_match:
        lat = float(lat_match.group(1))
        lon = float(lon_match.group(1))
        return lat, lon
    else:
        raise ValueError("geoReference does not contain +lat_0 and +lon_0")


def update_georeference_text(old_text, new_lat, new_lon):
    """Updates the +lat_0 and +lon_0 values in a proj4 WKT string."""
    new_text = re.sub(r"\+lat_0=([-+]?[0-9]*\.?[0-9]+)", f"+lat_0={new_lat}", old_text)
    new_text = re.sub(r"\+lon_0=([-+]?[0-9]*\.?[0-9]+)", f"+lon_0={new_lon}", new_text)
    return new_text


def rotate(x, y, angle_deg):
    angle_rad = math.radians(angle_deg)
    x_rot = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    y_rot = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return x_rot, y_rot


def transform_latlon(lat, lon, transformer_from_orig_to_utm, transformer_from_utm_to_new, angle_deg):
    x, y = transformer_from_orig_to_utm.transform(lon, lat)
    x_rot, y_rot = rotate(x, y, angle_deg)
    lon_new, lat_new = transformer_from_utm_to_new.transform(x_rot, y_rot, direction='INVERSE')
    return lat_new, lon_new


def transform_hdg(hdg, angle_deg):
    return hdg + math.radians(angle_deg)


def transform_xodr_file(input_path, output_path):
    tree = etree.parse(input_path)
    root = tree.getroot()

    ### INPUT REQUIRED ###
    # Adjust these values as needed
    new_lat = None
    new_lon = None
    angle_deg = 0.0
    ######################

    # Get original lat/lon from geoReference tag
    geo_ref_tag = root.find("header/geoReference")
    if geo_ref_tag is None or not geo_ref_tag.text:
        raise ValueError("No geoReference tag found.")

    orig_lat, orig_lon = extract_lat_lon_from_georeference(geo_ref_tag.text)

    if new_lat is None or new_lon is None:
        new_lat = orig_lat
        new_lon = orig_lon

    # Update geoReference tag for new output
    geo_ref_tag.text = etree.CDATA(update_georeference_text(geo_ref_tag.text, new_lat, new_lon))

    # Define projections
    crs_orig = CRS.from_proj4(f"+proj=tmerc +lat_0={orig_lat} +lon_0={orig_lon} +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    crs_new = CRS.from_proj4(f"+proj=tmerc +lat_0={new_lat} +lon_0={new_lon} +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

    transformer_to_utm = Transformer.from_crs("EPSG:4326", crs_orig, always_xy=True)
    transformer_from_utm = Transformer.from_crs("EPSG:4326", crs_new, always_xy=True)

    for elem in root.iter():
        lat = elem.attrib.get("lat")
        lon = elem.attrib.get("lon")
        x = elem.attrib.get("x")
        y = elem.attrib.get("y")
        hdg = elem.attrib.get("hdg")

        # Transform GPS-based coordinates
        if lat and lon:
            lat_f = float(lat)
            lon_f = float(lon)
            lat_new_val, lon_new_val = transform_latlon(lat_f, lon_f, transformer_to_utm, transformer_from_utm, angle_deg)
            elem.set("lat", f"{lat_new_val:.8f}")
            elem.set("lon", f"{lon_new_val:.8f}")

        # Transform local x, y coordinates
        if x and y:
            x_f = float(x)
            y_f = float(y)
            x_rot, y_rot = rotate(x_f, y_f, angle_deg)
            elem.set("x", f"{x_rot:.8f}")
            elem.set("y", f"{y_rot:.8f}")

        # Adjust heading
        if hdg:
            hdg_f = float(hdg)
            hdg_new = transform_hdg(hdg_f, angle_deg)
            elem.set("hdg", f"{hdg_new:.8f}")

    # Write modified XML
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transform XODR GPS-coordinates with a new geoReference and rotation.")
    parser.add_argument("input_file", help="Path to input .xodr file")
    parser.add_argument("output_file", help="Path to output .xodr file")

    args = parser.parse_args()

    transform_xodr_file(args.input_file, args.output_file)
