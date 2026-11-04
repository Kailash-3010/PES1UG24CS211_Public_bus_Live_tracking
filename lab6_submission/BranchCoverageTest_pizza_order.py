import pytest
from pizza_order import pizza_price, order_discount, delivery_status

# Test cases written so that every decision in pizza_order.py evaluates to
# both True and False (branch coverage), including boundary values.


# ---------- pizza_price ----------

def test_unknown_size_raises():
    # size not in SIZE_PRICE -> True
    with pytest.raises(ValueError, match="unknown size"):
        pizza_price("extra large", 1, False)


def test_negative_toppings_raises():
    # toppings < 0 -> True
    with pytest.raises(ValueError, match="invalid toppings"):
        pizza_price("medium", -1, False)


def test_plain_medium_pizza():
    # toppings > 3 -> False, is_cheese_burst -> False
    assert pizza_price("medium", 0, False) == 350


def test_exactly_three_toppings_boundary():
    # toppings > 3 -> False at the boundary: 200 + 3*40 = 320
    assert pizza_price("small", 3, False) == 320


def test_four_toppings_boundary():
    # toppings > 3 -> True at the boundary: 200 + 3*40 + 1*30 = 350
    assert pizza_price("small", 4, False) == 350


def test_large_many_toppings_with_cheese_burst():
    # toppings > 3 -> True, cheese burst on non-small: 500 + 120 + 60 + 100 = 780
    assert pizza_price("large", 5, True) == 780


def test_medium_cheese_burst():
    # is_cheese_burst -> True, size == "small" -> False: 350 + 80 + 100 = 530
    assert pizza_price("medium", 2, True) == 530


def test_cheese_burst_on_small_raises():
    # is_cheese_burst -> True, size == "small" -> True
    with pytest.raises(ValueError, match="cheese burst not available for small"):
        pizza_price("small", 1, True)


# ---------- order_discount ----------

def test_total_below_300_gets_no_discount():
    # order_total < 300 -> True
    assert order_discount(299, "tuesday", True) == 0


def test_total_exactly_300_boundary():
    # order_total < 300 -> False at the boundary, weekday, non-student
    assert order_discount(300, "monday", False) == 30


def test_tuesday_half_price_non_student():
    # day == "tuesday" -> True, is_student -> False
    assert order_discount(400, "tuesday", False) == 200


def test_tuesday_half_price_student():
    # day == "tuesday" -> True, is_student -> True
    assert order_discount(400, "tuesday", True) == 250


def test_saturday_no_discount_non_student():
    # day in weekend -> True (saturday), is_student -> False
    assert order_discount(400, "saturday", False) == 0


def test_sunday_student_discount_only():
    # day in weekend -> True (sunday), is_student -> True
    assert order_discount(400, "sunday", True) == 50


def test_weekday_ten_percent_student():
    # day not tuesday and not weekend -> else branch, is_student -> True
    assert order_discount(400, "friday", True) == 90


# ---------- delivery_status ----------

def test_too_far_not_deliverable():
    # distance_km > 10 -> True
    assert delivery_status(20, 11) == "not deliverable"


def test_exactly_10_km_is_deliverable():
    # distance_km > 10 -> False at the boundary
    assert delivery_status(20, 10) == "on time"


def test_on_time_delivery():
    # minutes_taken <= 30 -> True
    assert delivery_status(20, 3) == "on time"


def test_exactly_30_minutes_on_time():
    # minutes_taken <= 30 -> True at the boundary
    assert delivery_status(30, 3) == "on time"


def test_31_minutes_late():
    # minutes_taken <= 30 -> False, minutes_taken <= 45 -> True
    assert delivery_status(31, 3) == "late"


def test_exactly_45_minutes_late():
    # minutes_taken <= 45 -> True at the boundary
    assert delivery_status(45, 3) == "late"


def test_46_minutes_free_pizza():
    # minutes_taken <= 45 -> False
    assert delivery_status(46, 3) == "free pizza"
