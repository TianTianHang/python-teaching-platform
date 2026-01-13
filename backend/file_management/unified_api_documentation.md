# Unified Path-Based File and Folder Management API Documentation

This document describes the unified API endpoints for file and folder operations using paths instead of primary keys (PKs).

## Base URL
`/api/v1/path/`

## Authentication
All endpoints (except file download for public files) require authentication using a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. List Contents of Path
**GET** `/api/v1/path/`

Lists all files and folders at a given path.

#### Parameters
- `path` (optional): The path to list contents of. Default is `/` (root).

#### Example Request
```bash
GET /api/v1/path/?path=/documents/
Authorization: Bearer <token>
```

#### Response
```json
{
    "path": "/documents",
    "files": [
        {
            "id": "uuid-of-file",
            "name": "example.txt",
            "file_size": 1024,
            "formatted_file_size": "1.00 KB",
            "mime_type": "text/plain",
            "storage_backend": "local",
            "owner": {...},
            "folder": "uuid-of-parent-folder",
            "folder_name": "documents",
            "is_public": false,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "download_url": "/media/path/to/file.txt",
            "path": "/documents/example.txt"
        }
    ],
    "folders": [
        {
            "id": "uuid-of-folder",
            "name": "subfolder",
            "owner": {...},
            "parent": "uuid-of-parent-folder",
            "is_public": false,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "children_count": {
                "files": 2,
                "folders": 1,
                "total": 3
            },
            "path": "/documents/subfolder"
        }
    ]
}
```

### 2. Get File or Folder by Path
**GET** `/api/v1/path/{path}/`

Retrieves information about a specific file or folder by its path.
The path parameter can contain nested paths with slashes (e.g., `/test/data/`).

#### Parameters
- `path`: The URL path parameter representing the path to the file or folder.

#### Example Request
```bash
GET /api/v1/path/test/data/example.txt/
Authorization: Bearer <token>
```

#### Response
```json
{
    "type": "file",  // or "folder"
    "data": {
        // FileEntry or Folder serializer data
    }
}
```

### 3. Download File by Path
**GET** `/api/v1/path/{path}/?download=1`

Downloads a file by its path using the query parameter `download=1`. No authentication required for public files.

#### Parameters
- `path`: The URL path parameter representing the path to the file.
- `download=1`: Query parameter to indicate download operation.

#### Example Request
```bash
GET /api/v1/path/test/data/example.txt/?download=1
Authorization: Bearer <token>  # Required unless file is public
```

#### Response
Returns the file content with appropriate headers, or redirect URL for cloud storage.

### 4. Delete File or Folder by Path
**DELETE** `/api/v1/path/{path}/?delete=1`

Deletes a file or folder by its path using the query parameter `delete=1`.

#### Parameters
- `path`: The URL path parameter representing the path to the file or folder.
- `delete=1`: Query parameter to indicate delete operation.

#### Example Request
```bash
DELETE /api/v1/path/test/data/example.txt/?delete=1
Authorization: Bearer <token>
```

#### Response
```json
{
    "message": "File \"example.txt\" successfully deleted"
}
```

### 5. Upload File to Path
**POST** `/api/v1/path/upload/`

Uploads a file to a specified path.

#### Query Parameters
- `path`: The destination path for the file.

#### Form Data
- `file`: The file to upload.
- `name` (optional): New name for the file.
- `is_public` (optional): Whether the file should be public (default: false).
- `storage_backend` (optional): Storage backend to use (default: local).

#### Example Request
```bash
POST /api/v1/path/upload/?path=/documents/
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@path/to/local/file.txt
name=new_name.txt
is_public=false
```

#### Response
```json
{
    "id": "uuid-of-new-file",
    "name": "new_name.txt",
    "file_size": 1024,
    "formatted_file_size": "1.00 KB",
    "mime_type": "text/plain",
    "storage_backend": "local",
    "owner": {...},
    "folder": "uuid-of-parent-folder",
    "folder_name": "documents",
    "is_public": false,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "download_url": "/media/path/to/new_file.txt",
    "path": "/documents/new_name.txt"
}
```

### 6. Create Folder at Path
**POST** `/api/v1/path/create-folder/`

Creates a new folder at the specified path.

#### Request Body
- `path`: The full path where the new folder should be created (e.g., `/documents/new-folder/`).

#### Example Request
```bash
POST /api/v1/path/create-folder/
Authorization: Bearer <token>
Content-Type: application/json

{
    "path": "/documents/new-folder/"
}
```

#### Response
```json
{
    "id": "uuid-of-new-folder",
    "name": "new-folder",
    "owner": {...},
    "parent": "uuid-of-parent-folder",
    "is_public": false,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "children_count": {
        "files": 0,
        "folders": 0,
        "total": 0
    },
    "path": "/documents/new-folder"
}
```

### 7. Move/Copy File or Folder
**POST** `/api/v1/path/move_copy/`

Moves or copies a file or folder from one path to another.

#### Request Body
- `source_path`: The path of the file or folder to move/copy.
- `destination_path`: The destination path.
- `operation`: "move" or "copy".

#### Example Request
```bash
POST /api/v1/path/move_copy/
Authorization: Bearer <token>
Content-Type: application/json

{
    "source_path": "/documents/old-file.txt",
    "destination_path": "/documents/new-folder/",
    "operation": "move"
}
```

#### Response for File Operation
```json
{
    "message": "File successfully moved",
    "file": {
        // FileEntry serializer data
    },
    "original_folder": {
        // Folder serializer data
    },
    "new_folder": {
        // Folder serializer data
    }
}
```

#### Response for Folder Operation
```json
{
    "message": "Folder successfully copied",
    "result": {
        "copied_folder": {
            // New folder serializer data
        },
        "destination_folder": {
            // Destination folder serializer data
        }
    }
}
```

## Path Format

- Paths must start with `/`
- Folder paths can optionally end with `/`
- Special cases for destination paths:
  - If destination path ends with `/`: item is moved into that folder with original name
  - If destination path doesn't end with `/` and points to an existing folder: item is moved into that folder with original name
  - If destination path doesn't end with `/` and doesn't point to an existing folder: item is moved to the parent folder with the new name

## Query Parameter Operations

- `?download=1`: Downloads the file at the specified path
- `?delete=1`: Deletes the file or folder at the specified path

## Error Responses

All endpoints return error responses in the following format:

```json
{
    "error": "Error message describing what went wrong"
}
```

## Permissions

- Users can only access their own files and folders unless they are staff
- Public files can be downloaded by any user
- Folder and file operations respect the ownership model