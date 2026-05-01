from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Tuple
from uuid import UUID


def split_equal(amount: Decimal, user_ids: List[UUID]) -> Dict[UUID, Decimal]:
    if not user_ids:
        return {}

    n = len(user_ids)
    share = (amount / Decimal(n)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    remainder = amount - (share * Decimal(n))

    splits = {}
    for i, user_id in enumerate(sorted(user_ids)):
        extra = Decimal("0.01") if i < int(remainder * 100) else Decimal("0")
        splits[user_id] = share + extra

    return splits


def split_exact(amount: Decimal, splits: Dict[UUID, Decimal]) -> Dict[UUID, Decimal]:
    total = sum(splits.values())
    if total != amount:
        raise ValueError(f"Splits total {total} != amount {amount}")
    return splits


def split_percent(amount: Decimal, percents: Dict[UUID, Decimal]) -> Dict[UUID, Decimal]:
    total_percent = sum(percents.values())
    if total_percent != Decimal("100"):
        raise ValueError(f"Percents total {total_percent} != 100")

    splits = {}
    total_split = Decimal("0")
    user_ids_sorted = sorted(percents.keys())

    for i, user_id in enumerate(user_ids_sorted):
        if i == len(user_ids_sorted) - 1:
            split = amount - total_split
        else:
            split = (amount * percents[user_id] / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        splits[user_id] = split
        total_split += split

    return splits
