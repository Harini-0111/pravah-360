import os
import shutil
from datetime import datetime

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = os.path.join('backups', f'review_challenge_{timestamp}')
os.makedirs(backup_dir, exist_ok=True)

for folder in ['frontend', 'backend']:
    if os.path.exists(folder):
        shutil.copytree(folder, os.path.join(backup_dir, folder))

if os.path.exists('data/users.db'):
    shutil.copy('data/users.db', os.path.join(backup_dir, 'users.db'))

print(f"COMPLETE_BACKUP_CREATED_AT: {backup_dir}")
