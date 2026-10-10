from data.compliance.database import write_audit_log

from datetime import datetime

from data.compliance.database import write_audit_log


def record_audit_event(
    action_type: str,
    performed_by: str,
    customer_id: str,
    outcome: str,
):
    return write_audit_log(
        timestamp=datetime.now().isoformat(),
        action_type=action_type,
        performed_by=performed_by,
        customer_id=customer_id,
        outcome=outcome,
    )