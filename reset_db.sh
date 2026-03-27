#!/bin/bash

# Database Reset Script

echo "======================================"
echo "Database Reset"
echo "======================================"

# Database configuration
DB_USER="root"
DB_PASSWORD="Test@123456"
DB_NAME="bug_management"
INIT_SQL="backend/init_db.sql"

# Find MySQL executable
MYSQL_CMD=""
if command -v mysql &> /dev/null; then
    MYSQL_CMD="mysql"
elif [ -f "/usr/local/mysql/bin/mysql" ]; then
    MYSQL_CMD="/usr/local/mysql/bin/mysql"
elif [ -f "/opt/homebrew/bin/mysql" ]; then
    MYSQL_CMD="/opt/homebrew/bin/mysql"
elif [ -f "/usr/local/bin/mysql" ]; then
    MYSQL_CMD="/usr/local/bin/mysql"
else
    echo "❌ Error: MySQL not found!"
    echo ""
    echo "Please install MySQL or add it to PATH:"
    echo "  export PATH=\$PATH:/usr/local/mysql/bin"
    echo ""
    echo "Or specify MySQL path manually:"
    echo "  MYSQL_CMD=/path/to/mysql ./reset_db.sh"
    exit 1
fi

echo "Found MySQL: $MYSQL_CMD"
echo ""
echo "⚠️  WARNING: This will DELETE ALL DATA!"
echo ""
read -p "Continue? (type 'yes' to proceed): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Operation cancelled"
    exit 1
fi

echo ""
echo "1. Dropping old database..."
$MYSQL_CMD -u${DB_USER} -p${DB_PASSWORD} -e "DROP DATABASE IF EXISTS ${DB_NAME};"

if [ $? -eq 0 ]; then
    echo "✅ Old database dropped"
else
    echo "❌ Failed to drop database"
    echo ""
    echo "Please check:"
    echo "  1. MySQL is running"
    echo "  2. Username and password are correct"
    echo "  3. User has DROP DATABASE permission"
    exit 1
fi

echo ""
echo "2. Running initialization script..."
$MYSQL_CMD -u${DB_USER} -p${DB_PASSWORD} < ${INIT_SQL}

if [ $? -eq 0 ]; then
    echo "✅ Database initialized successfully"
else
    echo "❌ Database initialization failed"
    exit 1
fi

echo ""
echo "======================================"
echo "✅ Database Reset Complete!"
echo "======================================"
echo ""
echo "Default admin account:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "⚠️  Security: Please change password after first login!"
echo ""
echo "Now you can restart services:"
echo "  ./start_all.sh"
echo ""

