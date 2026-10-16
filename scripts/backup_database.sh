#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.prod.yml"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/f1_service_backup}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

if [[ ! "${RETENTION_DAYS}" =~ ^[1-9][0-9]*$ ]]; then
    echo "RETENTION_DAYS must be a positive integer." >&2
    exit 1
fi

if [[ ! -f "${PROJECT_DIR}/.env.prod" ]]; then
    echo "Production environment file not found: ${PROJECT_DIR}/.env.prod" >&2
    exit 1
fi

umask 077
mkdir -p -- "${BACKUP_DIR}"
chmod 700 -- "${BACKUP_DIR}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="${BACKUP_DIR}/f1_service_backup_${timestamp}.dump"
temporary_file="${backup_file}.tmp"

cleanup() {
    rm -f -- "${temporary_file}"
}
trap cleanup EXIT

docker compose --project-directory "${PROJECT_DIR}" -f "${COMPOSE_FILE}" \
    exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-acl' \
    > "${temporary_file}"

if [[ ! -s "${temporary_file}" ]]; then
    echo "pg_dump produced an empty backup." >&2
    exit 1
fi

chmod 600 -- "${temporary_file}"
docker compose --project-directory "${PROJECT_DIR}" -f "${COMPOSE_FILE}" \
    exec -T db pg_restore --list < "${temporary_file}" > /dev/null

mv -- "${temporary_file}" "${backup_file}"
find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'f1_service_backup_*.dump' \
    -mtime "+${RETENTION_DAYS}" -delete

echo "Database backup created and verified: ${backup_file}"
