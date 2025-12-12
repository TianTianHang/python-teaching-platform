# File Management API Documentation

This documentation describes the file management API endpoints implemented in the Django application. The API allows users to upload, download, list, update, and delete files with support for both local and object storage backends.

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Models](#models)
4. [Storage Backends](#storage-backends)
5. [Examples](#examples)

## Authentication

All endpoints (except public file downloads) require JWT authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### POST /api/v1/files/upload/
Upload a new file to the system.

**Request:**
- Method: `POST`
- URL: `/api/v1/files/upload/`
- Authentication: Required (User must be authenticated)
- Content-Type: `multipart/form-data`

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | The file to upload |
| name | String | No | Custom name for the file (defaults to original filename) |
| is_public | Boolean | No | Whether the file is publicly accessible (default: false) |
| storage_backend | String | No | Storage backend to use: 'local', 's3', or 'minio' (default: 'local') |

**Response:**
- Status Code: `201 Created`
- Body: File entry object

**Example Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "is_public=false" \
  -F "storage_backend=local" \
  http://localhost:8000/api/v1/files/upload/
```

### GET /api/v1/files/
List all accessible files.

**Request:**
- Method: `GET`
- URL: `/api/v1/files/`
- Authentication: Required for non-public files

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | Integer | Page number for pagination |
| page_size | Integer | Number of items per page |

**Response:**
- Status Code: `200 OK`
- Body: Paginated list of file entries

### GET /api/v1/files/{id}/
Retrieve details of a specific file.

**Request:**
- Method: `GET`
- URL: `/api/v1/files/{id}/`
- Authentication: Required for non-public files

**Response:**
- Status Code: `200 OK`
- Body: File entry object

### PATCH /api/v1/files/{id}/
Update file metadata.

**Request:**
- Method: `PATCH`
- URL: `/api/v1/files/{id}/`
- Authentication: Required (User must be file owner or staff)

**Request Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| name | String | New name for the file |
| is_public | Boolean | Whether the file is publicly accessible |
| storage_backend | String | Storage backend to use: 'local', 's3', or 'minio' |

**Response:**
- Status Code: `200 OK`
- Body: Updated file entry object

### DELETE /api/v1/files/{id}/
Delete a file.

**Request:**
- Method: `DELETE`
- URL: `/api/v1/files/{id}/`
- Authentication: Required (User must be file owner or staff)

**Response:**
- Status Code: `204 No Content`

### GET /api/v1/files/{id}/download/
Download a file.

**Request:**
- Method: `GET`
- URL: `/api/v1/files/{id}/download/`
- Authentication: Required for non-public files

**Response:**
- Status Code: `200 OK`
- Body: File content for download

### GET /api/v1/user-files/
List files owned by the authenticated user.

**Request:**
- Method: `GET`
- URL: `/api/v1/user-files/`
- Authentication: Required

**Response:**
- Status Code: `200 OK`
- Body: List of file entries owned by the user

## Models

### FileEntry
Represents an uploaded file in the system.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier for the file entry |
| name | String | Original name of the file |
| file | File | The actual file stored in the system |
| file_size | Integer | Size of the file in bytes |
| formatted_file_size | String | Human-readable file size (e.g., "2.5 MB") |
| mime_type | String | MIME type of the file |
| storage_backend | String | Storage backend used ('local', 's3', 'minio') |
| owner | User | User who uploaded the file |
| is_public | Boolean | Whether the file is publicly accessible |
| created_at | DateTime | When the file was uploaded |
| updated_at | DateTime | When the file metadata was last updated |
| download_url | String | URL to download the file |

## Storage Backends

The system supports multiple storage backends:

1. **Local Storage** - Files are stored on the local filesystem in the media directory
2. **Amazon S3** - Files are stored in an S3-compatible object storage service
3. **MinIO** - Files are stored in a MinIO object storage service

The storage backend for each file is determined by the `storage_backend` field on the FileEntry model.

## Examples

### Upload a File
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "file=@my_document.pdf" \
  -F "name=My Important Document" \
  -F "is_public=false" \
  http://localhost:8000/api/v1/files/upload/
```

### List User's Files
```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/user-files/
```

### Update File Metadata
```bash
curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"is_public": true, "name": "Public Document"}' \
  http://localhost:8000/api/v1/files/123e4567-e89b-12d3-a456-426614174000/
```

### Download a File
```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/files/123e4567-e89b-12d3-a456-426614174000/download/
```

## Permissions

- **Authenticated Users**: Can upload files, view their own files and public files, update their own files
- **Staff Users**: Can access all files regardless of ownership
- **Public Access**: Only applies to files where `is_public` is set to `true`