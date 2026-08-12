#results of the fare prediction and trip summary are displayed after the user clicks Predict
import streamlit as st


class ResultsDisplay:
    def render(self, predicted_fare: float, summary: dict) -> None:
        st.subheader("Fare estimate")

        c1, c2, c3 = st.columns(3)
        c1.metric("Predicted fare", f"${predicted_fare:,.2f}")
        c2.metric("Trip distance", f"{summary['trip_distance_km']:.2f} km")
        c3.metric("Direction", f"{summary['bearing_deg']:.0f}°")


        st.markdown("**Trip information**")
        info_cols = st.columns(4)
        info_cols[0].markdown(f"- **Day:** {summary['day_name']}")
        info_cols[0].markdown(f"- **Hour:** {summary['hour']:02d}:00")
        info_cols[1].markdown(f"- **Month/Year:** {summary['month']}/{summary['year']}")
        info_cols[1].markdown(f"- **Weekend:** {'Yes' if summary['is_weekend'] else 'No'}")
        info_cols[2].markdown(f"- **Rush hour:** {'Yes' if summary['is_rush_hour'] else 'No'}")
        info_cols[2].markdown(f"- **Pickup → center:** {summary['pickup_dist_from_center_km']:.2f} km")
        info_cols[3].markdown(f"- **Drop-off → center:** {summary['dropoff_dist_from_center_km']:.2f} km")
