import cloudinary.uploader
import cloudinary.api
import cloudinary
import os
from dotenv import load_dotenv
import csv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

csv_file_path = 'assets.csv'
existing_assets = set()

if os.path.isfile(csv_file_path):
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as existing_csv_file:
        reader = csv.reader(existing_csv_file)
        if next(reader, None):
            existing_assets = set(row[0] for row in reader)

if not existing_assets:
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Public ID', 'URL', 'Tags'])


def fetch_assets(folder_name, existing_assets, next_cursor=None):
    csv_file_path = f'{folder_name}_assets.csv' if folder_name else 'root_assets.csv'

    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Public ID', 'URL', 'Tags'])

    params = {
        'context': 'false',
        'max_results': 500,
        'type': 'upload',
        'next_cursor': next_cursor
    }

    if folder_name:
        params['prefix'] = folder_name + "/"

    try:
        response = cloudinary.api.resources(**params)
        data = response['resources']

        print(
            f"Retrieved {len(data)} assets from folder: {folder_name if folder_name else 'root'}")

        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)

            for resource in data:
                public_id = resource['public_id']
                if public_id not in existing_assets:
                    url = resource['secure_url']
                    tags = resource.get('tags', [])
                    csv_writer.writerow([public_id, url, ','.join(tags)])
                    existing_assets.add(public_id)

        if 'next_cursor' in response and response['next_cursor'] != next_cursor:
            print(
                f"Next cursor for folder {folder_name if folder_name else 'root'}: {response['next_cursor']}")
            fetch_assets(folder_name, existing_assets, response['next_cursor'])

    except cloudinary.exceptions.BadRequest as e:
        print(
            f"Error fetching assets for folder {folder_name if folder_name else 'root'}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


folders = ['', 'meme sound effects', 'The First Great Meme Pack']
resource_types = ['image', 'video', 'raw', 'audio']

existing_assets = set()
for folder in folders:
    for resource_type in resource_types:
        fetch_assets(folder, existing_assets)
