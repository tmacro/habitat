# This is the sshd server system-wide configuration file.  See
# sshd_config(5) for more information.

# This sshd was compiled with PATH=/usr/bin:/bin:/usr/sbin:/sbin

# The strategy used for options in the default sshd_config shipped with
# OpenSSH is to specify options with their default value where
# possible, but leave them commented.  Uncommented options override the
# default value.

# Explicitly define out protocol version
Protocol 2

# Daemon settings
LogLevel VERBOSE
Subsystem sftp  /usr/lib/ssh/sftp-server -f AUTHPRIV -l INFO
UsePrivilegeSeparation sandbox

# Change to non-standard port
Port ${sshd_port}

# Disable root login
PermitRootLogin no

# restrict logins to admin user
AllowUsers ${admin_user}

# Enable pam authentication
UsePAM yes

# Disable password login and enforce publice key
PasswordAuthentication no
AuthenticationMethods publickey

# Disconnect sessions idle for 10 minutes
ClientAliveInterval 300
ClientAliveCountMax 2

# Disable X11 Forwarding
X11Forwarding no

HostKey /etc/ssh/ssh_host_ed25519_key
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key

KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256

Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr

MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,umac-128@openssh.com
