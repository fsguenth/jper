from service.models import Account, RepositoryDepositLog, DepositRecord
from dateutil.relativedelta import relativedelta
from octopus.core import app
from octopus.lib import dates

def cleanup_repository_logs():
    bibids = Account.pull_all_repositories()
    for bibid in bibids:
        repo_id = bibids[bibid]
        # pull the latest sword repository deposit log
        latest_log = RepositoryDepositLog().pull_by_repo(repo_id)
        if not latest_log:
            continue
        # Get the date to keep logs from
        last_updated = dates.parse(latest_log.last_updated)
        keep = app.config.get('SCHEDULE_KEEP_SWORD_LOGS_MONTHS', 3)
        keep_date = (last_updated - relativedelta(months=keep)).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Get all sword repository deposit logs older than keep_date
        old_logs = RepositoryDepositLog().pull_old_deposit_logs(repo_id, keep_date)
        for log in old_logs.get('hits', {}).get('hits', []):
            deposit_record_logs.append(log['id'])
            messages = log.get('_source', {}).get('messages', [])
            for msg in messages:
                if msg.get('deposit_record', None) and msg['deposit_record'] != "None":
                    detailed_log = DepositRecord.pull(msg['deposit_record'])
                    detailed_log.delete()
                    app.looger.debug(f"Deleted sword deposit record {msg['deposit_record']}")
            deposit_log = RepositoryDepositLog().pull(log['id'])
            deposit_log.delete()
            app.looger.debug(f"Deleted sword deposit log {log['id']}")
