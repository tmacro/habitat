#!/bin/sh
set -e

timestamp() {
date -Iseconds -u | tr -d ':'
}

create_backup() {
    /usr/bin/docker run  \
        --volumes-from rancher-data \
        -v /opt/rancher-backup:/backup \
        alpine tar zcvf /backup/rancher-data-backup.tar.gz /var/lib/rancher
}

upload_backup() {
    /usr/bin/rclone copyto \
        /opt/rancher-backup/rancher-data-backup.tar.gz \
        b2:nimbus-backup/manager/rancher-data-backup-$(timestamp).tar.gz
}

cleanup_backup() {
    /bin/rm -f /opt/rancher-backup/rancher-data-backup.tar.gz
}


cleanup_backup
create_backup
upload_backup