#user can select passenger count, date/time, click mode, and reset the inputs
from dataclasses import dataclass
from datetime import date, time

import streamlit as st


@dataclass
class SidebarInputs:
    click_mode: str          # choose Pickup or Drop-off
    passenger_count: int
    trip_date: date
    trip_time: time
    reset_clicked: bool


class Sidebar:
    def render(self) -> SidebarInputs:
        st.sidebar.header("Trip details")

        click_mode = st.sidebar.radio(
            "Clicking the map sets:",
            options=["Pickup", "Drop-off"],
            help="Choose what a map click sets, then click the map.",
        )

        passenger_count = st.sidebar.slider("Passengers", min_value=1, max_value=6, value=1)

        st.sidebar.markdown("**Pickup date & time**")
        trip_date = st.sidebar.date_input("Date", value=date.today())
        trip_time = st.sidebar.time_input("Time", value=time(hour=12, minute=0))

        reset_clicked = st.sidebar.button("Clear pickup / drop-off", use_container_width=True)

        st.sidebar.divider()

        return SidebarInputs(
            click_mode=click_mode,
            passenger_count=passenger_count,
            trip_date=trip_date,
            trip_time=trip_time,
            reset_clicked=reset_clicked,
        )
