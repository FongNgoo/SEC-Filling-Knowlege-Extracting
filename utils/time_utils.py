import pytz
import datetime
import logging

logger = logging.getLogger(__name__)
# Convert UTC to EST
def convert_utc_to_est(utc_dt_str):
    try:
        utc_dt = datetime.strptime(utc_dt_str, '%Y-%m-%d')
        utc = pytz.UTC
        utc_dt = utc.localize(utc_dt)
        est = pytz.timezone("US/Eastern")
        est_dt = utc_dt.astimezone(est).replace(tzinfo=None)
        return est_dt.strftime('%Y-%m-%d')
    except Exception as e:
        logger.error(f"Error converting UTC to EST for {utc_dt_str}: {e}")
        return utc_dt_str