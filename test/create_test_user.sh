#!/bin/bash
# Test Users Creation Script for Python Teaching Platform
# This script creates 1000 test users for load testing

set -e  # Exit on error

# Configuration
USER_COUNT=1000
ST_NUMBER_START=2024000001
COMMON_PASSWORD="TestPass123!"
OUTPUT_FILE="test_users.csv"

# Get script directory and navigate to backend
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR=/home/tiantian/project/python-teaching-platform/backend
cd "$BACKEND_DIR"

echo "=== Test Users Creation Script ==="
echo "User count: $USER_COUNT"
echo "Common password: $COMMON_PASSWORD"
echo "Output file: $OUTPUT_FILE"
echo ""

# Step 1: Create output CSV with header
echo "Step 1: Initializing CSV file..."
mkdir -p "$(dirname "./$OUTPUT_FILE")"
echo "username,password,st_number" > "$OUTPUT_FILE"
echo "  [OK] CSV header created"

# Step 2: Create users using Django shell
echo "Step 2: Creating $USER_COUNT test users..."
echo "  This may take a minute..."
source .venv/bin/activate
python manage.py shell <<'PYTHON_SCRIPT'
import os
import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

# Check if test users already exist
existing_count = User.objects.filter(username__startswith='testuser_').count()
if existing_count > 0:
    print(f"  [INFO] Found {existing_count} existing test users. Deleting them...")
    User.objects.filter(username__startswith='testuser_').delete()

# Create users in bulk for performance
users_to_create = []
USER_COUNT = 1000

for i in range(1, USER_COUNT + 1):
    st_number = f"2024{i:06d}"
    username = f"testuser_{i:04d}"
    users_to_create.append(User(
        username=username,
        st_number=st_number,
        email=f"{username}@test.com",
        is_active=True
    ))

# Bulk create users (without password first for efficiency)
with transaction.atomic():
    created_users = User.objects.bulk_create(users_to_create, batch_size=500)

# Set passwords for all users
COMMON_PASSWORD = "TestPass123!"
with transaction.atomic():
    for user in created_users:
        user.set_password(COMMON_PASSWORD)
        user.save(update_fields=['password'])

print(f"  [OK] Created {len(created_users)} test users")
PYTHON_SCRIPT

# Step 3: Generate CSV with credentials
echo "Step 3: Exporting credentials to CSV..."
python manage.py shell <<PYTHON_SCRIPT
import os
import csv
from django.contrib.auth import get_user_model

User = get_user_model()
OUTPUT_FILE = "$OUTPUT_FILE"
COMMON_PASSWORD = "$COMMON_PASSWORD"

with open(OUTPUT_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['username', 'password', 'st_number'])

    for user in User.objects.filter(username__startswith='testuser_').order_by('st_number'):
        writer.writerow([user.username, COMMON_PASSWORD, user.st_number])

print(f"  [OK] CSV exported to {OUTPUT_FILE}")
PYTHON_SCRIPT

# Step 4: Show sample data
echo ""
echo "Step 4: Sample credentials (first 5 users):"
head -6 "$OUTPUT_FILE"

# Step 5: Verify count
echo ""
echo "Step 5: Verification..."
TOTAL_COUNT=$(python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())")
TEST_USER_COUNT=$(python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(username__startswith='testuser_').count())")
echo "  Total users in database: $TOTAL_COUNT"
echo "  Test users created: $TEST_USER_COUNT"

echo ""
echo "=== Test Users Creation Complete ==="
echo "CSV file: $OUTPUT_FILE"
echo ""
echo "To run load tests:"
echo "  cd ../test"
echo "  locust -f locustfile.py"
