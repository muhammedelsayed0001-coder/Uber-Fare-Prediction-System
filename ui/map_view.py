#Interactive map components
import folium
from streamlit_folium import st_folium

from config import NYC_CENTER, DEFAULT_ZOOM


class MapSelector:
    def __init__(self, center=NYC_CENTER, zoom=DEFAULT_ZOOM):
        self.center = center
        self.zoom = zoom

    def render(self, pickup=None, dropoff=None, key: str = "trip_map"):
        fmap = folium.Map(location=self.center, zoom_start=self.zoom, tiles="cartodbpositron")

        if pickup:
            folium.Marker(
                location=pickup,
                tooltip="Pickup",
                icon=folium.Icon(color="green", icon="play", prefix="fa"),
            ).add_to(fmap)

        if dropoff:
            folium.Marker(
                location=dropoff,
                tooltip="Drop-off",
                icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
            ).add_to(fmap)

        if pickup and dropoff:
            folium.PolyLine(
                locations=[pickup, dropoff], color="#1E88E5", weight=3, opacity=0.8, dash_array="6"
            ).add_to(fmap)
            fmap.fit_bounds([pickup, dropoff], padding=(40, 40))

        return st_folium(
            fmap,
            height=480,
            use_container_width=True,
            key=key,
            returned_objects=["last_clicked"],
        )
