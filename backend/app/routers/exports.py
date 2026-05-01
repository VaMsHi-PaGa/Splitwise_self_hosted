from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
import csv
import io

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.group import GroupMember, Group
from app.models.expense import Expense, ExpenseSplit

router = APIRouter(tags=["exports"])


@router.get("/groups/{group_id}/export.csv")
def export_group_csv(group_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Description", "Amount", "Category", "Paid By", "Split Type", "Who Owes", "Share"])

    for expense in expenses:
        created_user = db.query(User).filter(User.id == expense.created_by).first()
        paid_by_names = ", ".join([payer.user.name for payer in expense.payers])

        for split in expense.splits:
            split_user = split.user
            writer.writerow([
                expense.expense_date.isoformat(),
                expense.description,
                float(expense.amount),
                expense.category,
                paid_by_names,
                expense.split_type,
                split_user.name,
                float(split.share_amount)
            ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={group.name}_expenses.csv"}
    )
