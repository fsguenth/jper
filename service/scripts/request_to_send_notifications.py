from service import models

def request_to_send_notifications(account_id, notification_ids, check_none = True):
    if check_none:
        recs = models.RequestNotification.pull_by_ids(None, username, status='queued', size=100)
        if recs is not None:
            return False, f"There are {len(recs)} in queue"
    duplicate = 0
    queued_notifications = []
    for n_id in list(notification_ids):
        rec = models.RequestNotification.pull_by_ids(n_id, account_id, status='queued', size=1)
        if not rec:
            rec = models.RequestNotification()
            rec.account_id = account_id
            rec.notification_id = n_id
            rec.status = 'queued'
            rec.save()
            queued_notifications.append(n_id)
        else:
            duplicate += 1
    msg = "Queued {n} notifications for deposit".format(n=len(queued_notifications))
    if duplicate > 0:
        msg = msg + '<br>' + '{n} notifications are already waiting in queue'.format(n=duplicate)
    return queued_notifications, msg

