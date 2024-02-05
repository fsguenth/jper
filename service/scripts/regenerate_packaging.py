from service import packages, models

def recreate_opus4zip_packaging(notification_ids):
    if isinstance(notification_ids, str):
        notification_ids = [notification_ids]
    source_packaging = 'https://datahub.deepgreen.org/FilesAndJATS'
    destination_packaging = 'http://purl.org/net/sword/package/OPUS4Zip'
    backup_ids = []
    done_ids = []
    for notification_id in notification_ids:
        backups = packages.PackageManager.backup(notification_id, source_packaging, [destination_packaging])
        backup_ids += backups
        done = packages.PackageManager.convert(notification_id, source_packaging, [destination_packaging])
        done_ids += done
    return backup_ids, done_ids


