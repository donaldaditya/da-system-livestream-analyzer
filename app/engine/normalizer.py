from app.models.stream import StandardStreamRecord

def normalize(record: StandardStreamRecord) -> StandardStreamRecord:
    record.gmv_total = record.gmv_affiliate or record.gmv_confirmed or 0
    if record.duration_minutes > 0:
        record.gmv_per_hour = record.gmv_total / (record.duration_minutes / 60)
    orders = record.orders_paid or record.orders_confirmed or 0
    views = record.views_total or record.viewers_total or 0
    if views > 0:
        record.conversion_rate = orders / views
    if record.views_total and record.views_total > 0:
        total_eng = (record.comments or 0) + (record.shares or 0) + (record.likes or 0)
        record.engagement_rate = total_eng / record.views_total
    if record.new_followers is not None and record.viewers_peak and record.viewers_peak > 0:
        record.follow_rate = record.new_followers / record.viewers_peak
    if record.add_to_cart is not None and record.viewers_total and record.viewers_total > 0:
        record.atc_rate = record.add_to_cart / record.viewers_total
    return record
