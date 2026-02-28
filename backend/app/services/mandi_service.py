from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.mandi import MandiPrice
from app.schemas.mandi import MandiPriceResponse, MandiPriceTrend, SellRecommendation


def get_today_prices(
    db: Session,
    crop_name: str,
    state: Optional[str] = None,
    district: Optional[str] = None,
) -> List[MandiPriceResponse]:
    query = db.query(MandiPrice).filter(MandiPrice.crop_name == crop_name)
    if state:
        query = query.filter(MandiPrice.state == state)
    if district:
        query = query.filter(MandiPrice.district == district)
    query = query.order_by(desc(MandiPrice.price_date)).limit(50)
    results = query.all()
    return [MandiPriceResponse.model_validate(r) for r in results]


def get_price_trend(
    db: Session, crop_name: str, mandi_name: str, days: int = 30
) -> MandiPriceTrend:
    since = date.today() - timedelta(days=days)
    results = (
        db.query(MandiPrice)
        .filter(
            MandiPrice.crop_name == crop_name,
            MandiPrice.mandi_name == mandi_name,
            MandiPrice.price_date >= since,
        )
        .order_by(MandiPrice.price_date)
        .all()
    )
    prices = [MandiPriceResponse.model_validate(r) for r in results]

    if len(prices) >= 2:
        first_half = prices[: len(prices) // 2]
        second_half = prices[len(prices) // 2 :]
        avg_first = sum(p.modal_price for p in first_half) / len(first_half)
        avg_second = sum(p.modal_price for p in second_half) / len(second_half)
        change_pct = ((avg_second - avg_first) / avg_first) * 100 if avg_first else 0
        if change_pct > 5:
            trend = "rising"
        elif change_pct < -5:
            trend = "falling"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    recommendations = {
        "rising": ("Prices are rising. Consider waiting for better rates.", "दाम बढ़ रहे हैं। बेहतर भाव के लिए इंतजार करें।"),
        "falling": ("Prices are falling. Consider selling soon.", "दाम गिर रहे हैं। जल्द बेचने पर विचार करें।"),
        "stable": ("Prices are stable. Sell based on your storage capacity.", "दाम स्थिर हैं। अपनी भंडारण क्षमता के अनुसार बेचें।"),
        "insufficient_data": ("Not enough data for trend analysis.", "रुझान विश्लेषण के लिए पर्याप्त डेटा नहीं है।"),
    }
    rec, rec_hi = recommendations[trend]

    return MandiPriceTrend(
        crop_name=crop_name,
        mandi_name=mandi_name,
        prices=prices,
        trend=trend,
        recommendation=rec,
        recommendation_hi=rec_hi,
    )


def get_sell_recommendation(
    db: Session, crop_name: str, mandi_name: str, msp_price: Optional[float] = None
) -> SellRecommendation:
    last_30 = date.today() - timedelta(days=30)
    results = (
        db.query(MandiPrice)
        .filter(
            MandiPrice.crop_name == crop_name,
            MandiPrice.mandi_name == mandi_name,
            MandiPrice.price_date >= last_30,
        )
        .order_by(desc(MandiPrice.price_date))
        .all()
    )

    if not results:
        return SellRecommendation(
            crop_name=crop_name,
            current_price=0,
            avg_price_30d=0,
            msp_price=msp_price,
            recommendation="hold",
            reasoning="No recent price data available. Hold and check again.",
            reasoning_hi="हाल की कीमत का डेटा नहीं है। रुकें और दोबारा जांचें।",
        )

    current = results[0].modal_price
    avg_30d = sum(r.modal_price for r in results) / len(results)

    if avg_30d == 0:
        rec, reason, reason_hi = (
            "hold",
            "Average price is zero. No actionable data.",
            "औसत मूल्य शून्य है। कोई कार्रवाई योग्य डेटा नहीं।",
        )
    elif current >= avg_30d * 1.1:
        rec, reason, reason_hi = (
            "sell_now",
            f"Current price ₹{current}/q is {((current - avg_30d) / avg_30d * 100):.0f}% above 30-day average. Good time to sell.",
            f"वर्तमान मूल्य ₹{current}/क्विंटल 30 दिन के औसत से ऊपर है। बेचने का अच्छा समय है।",
        )
    elif current <= avg_30d * 0.9:
        rec, reason, reason_hi = (
            "wait",
            f"Current price ₹{current}/q is below 30-day average ₹{avg_30d:.0f}/q. Wait for recovery if storage available.",
            f"वर्तमान मूल्य ₹{current}/क्विंटल 30 दिन के औसत ₹{avg_30d:.0f} से नीचे है। भंडारण हो तो रुकें।",
        )
    else:
        rec, reason, reason_hi = (
            "hold",
            f"Current price ₹{current}/q is near 30-day average ₹{avg_30d:.0f}/q. No strong signal.",
            f"वर्तमान मूल्य ₹{current}/क्विंटल 30 दिन के औसत के करीब है।",
        )

    return SellRecommendation(
        crop_name=crop_name,
        current_price=current,
        avg_price_30d=round(avg_30d, 2),
        msp_price=msp_price,
        recommendation=rec,
        reasoning=reason,
        reasoning_hi=reason_hi,
    )
