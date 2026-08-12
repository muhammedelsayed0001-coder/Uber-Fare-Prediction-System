#main app
import streamlit as st
 
from datetime import datetime
 
from config import DB_PATH, LAT_BOUNDS, LON_BOUNDS, NYC_CENTER
from core.feature_engineering import FeatureEngineer, TripRequest
from core.predictor import UberFarePredictor
from database import PredictionRecord, PredictionRepository
from ui.map_view import MapSelector
from ui.results import ResultsDisplay
from ui.sidebar import Sidebar, SidebarInputs
 
st.set_page_config(page_title="Uber Fare Estimator", layout="wide")
 
 
@st.cache_resource #helps avoid reloading the model every time the user clicks Predict
def get_predictor() -> UberFarePredictor:
    return UberFarePredictor()
 
 
@st.cache_resource #one connection lifecycle for the app, same pattern as get_predictor
def get_repository() -> PredictionRepository:
    return PredictionRepository(DB_PATH)
 
 
def _init_session_state() -> None:
    st.session_state.setdefault("pickup", None)
    st.session_state.setdefault("dropoff", None)
 
 
def _handle_map_click(map_result: dict, inputs: SidebarInputs) -> None:
    clicked = map_result.get("last_clicked") if map_result else None
    if not clicked:
        return
    point = (clicked["lat"], clicked["lng"])
    if inputs.click_mode == "Pickup":
        st.session_state["pickup"] = point
    else:
        st.session_state["dropoff"] = point
 
 
def _in_nyc_bounds(lat: float, lon: float) -> bool:
    return LAT_BOUNDS[0] <= lat <= LAT_BOUNDS[1] and LON_BOUNDS[0] <= lon <= LON_BOUNDS[1]
 
 
def main() -> None:
    _init_session_state()
 
    st.title("Uber Fare Estimator")
    st.caption(
        "Click the map to set pickup and drop-off points, then predict the fare. "
    )
 
    sidebar = Sidebar()
    inputs = sidebar.render()
 
    if inputs.reset_clicked:
        st.session_state["pickup"] = None
        st.session_state["dropoff"] = None
        st.rerun()
 
    left, right = st.columns([3, 2])
 
    with left:
        st.markdown(f"**Click mode:** setting **{inputs.click_mode}** on next click")
        map_selector = MapSelector(center=NYC_CENTER)
        map_result = map_selector.render(
            pickup=st.session_state["pickup"],
            dropoff=st.session_state["dropoff"],
        )
        _handle_map_click(map_result, inputs)
 
        pickup = st.session_state["pickup"]
        dropoff = st.session_state["dropoff"]
 
        status_cols = st.columns(2)
        status_cols[0].info(f"Pickup: {pickup}" if pickup else "Pickup: not set")
        status_cols[1].info(f"Drop-off: {dropoff}" if dropoff else "Drop-off: not set")
 
    with right:
        st.markdown("### Predict")
 
        ready = pickup is not None and dropoff is not None
        if not ready:
            st.warning("Select both a pickup and a drop-off point on the map to continue.")
        else:
            out_of_bounds = not (_in_nyc_bounds(*pickup) and _in_nyc_bounds(*dropoff))
            if out_of_bounds:
                st.warning(
                    "One of your points is outside the NYC area the model was "
                    "trained on — the estimate may be unreliable."
                )
 
            
            if st.button("Predict fare", type="primary", use_container_width=True, disabled=not ready):
                pickup_datetime = datetime.combine(inputs.trip_date, inputs.trip_time)
                #after the user clicks Predict this object is created
                trip = TripRequest(
                    pickup_lat=pickup[0],
                    pickup_lon=pickup[1],
                    dropoff_lat=dropoff[0],
                    dropoff_lon=dropoff[1],
                    passenger_count=inputs.passenger_count,
                    pickup_datetime=pickup_datetime,
                )
 
                engineer = FeatureEngineer()
                features = engineer.transform(trip)
                summary = engineer.trip_summary(trip)
 
                predictor = get_predictor()
                predicted_fare = predictor.predict(features)
 
                st.session_state["last_prediction"] = (predicted_fare, summary)
 
                #persist this request so every prediction is auditable/reviewable later
                repository = get_repository()
                record = PredictionRecord(
                    pickup_lat=trip.pickup_lat,
                    pickup_lon=trip.pickup_lon,
                    dropoff_lat=trip.dropoff_lat,
                    dropoff_lon=trip.dropoff_lon,
                    pickup_datetime=pickup_datetime,
                    passenger_count=trip.passenger_count,
                    predicted_fare=predicted_fare,
                    engineered_features=features.iloc[0].to_dict(),
                )
                repository.save(record)
 
        if "last_prediction" in st.session_state:
            predicted_fare, summary = st.session_state["last_prediction"]
            results = ResultsDisplay()
            results.render(predicted_fare, summary)
 
    st.divider()
    with st.expander("Recent predictions (from database)"):
        repository = get_repository()
        records = repository.get_all(limit=10)
        if not records:
            st.caption("No predictions saved yet.")
        else:
            st.dataframe(
                [
                    {
                        "id": r.id,
                        "pickup": f"{r.pickup_lat:.4f}, {r.pickup_lon:.4f}",
                        "dropoff": f"{r.dropoff_lat:.4f}, {r.dropoff_lon:.4f}",
                        "pickup_datetime": r.pickup_datetime,
                        "passengers": r.passenger_count,
                        "predicted_fare": round(r.predicted_fare, 2),
                        "saved_at": r.created_at,
                    }
                    for r in records
                ],
                use_container_width=True,
                hide_index=True,
            )
 
 
if __name__ == "__main__":
    main()
 