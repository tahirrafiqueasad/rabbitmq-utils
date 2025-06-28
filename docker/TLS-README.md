## Making dir

```bash
mkdir ./certs
cd ./certs
```

## Create CA

```bash
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=RootCA"
```

## Create server key

```bash
openssl genrsa -out server.key 2048
```

## Create CSR with SAN = localhost

```bash
cat > server.cnf <<EOF
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
CN = localhost

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
DNS.2 = rabbitmq
EOF

openssl req -new -key server.key -out server.csr -config server.cnf
```

# Sign with CA and include SAN

```bash
cat > ca.cnf <<EOF
[ v3_ca ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
DNS.2 = rabbitmq
EOF

openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
-out server.crt -days 3650 -sha256 -extfile ca.cnf -extensions v3_ca
```

# Management

## Create CA

```bash
openssl genrsa -out management_ca.key 2048
openssl req -x509 -new -nodes -key management_ca.key -sha256 -days 3650 -out management_ca.crt -subj "/CN=DonutCA"
```

## Create server key

```bash
openssl genrsa -out management_server.key 2048
```

## Create CSR with SAN = localhost

```bash
cat > management_server.cnf <<EOF
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
CN = localhost

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
DNS.2 = 192.168.15.104
EOF

openssl req -new -key management_server.key -out management_server.csr -config management_server.cnf
```

# Sign with CA and include SAN

```bash
cat > management_ca.cnf <<EOF
[ v3_ca ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
DNS.2 = 192.168.15.104
EOF

openssl x509 -req -in management_server.csr -CA management_ca.crt -CAkey management_ca.key -CAcreateserial \
-out management_server.crt -days 3650 -sha256 -extfile management_ca.cnf -extensions v3_ca
```

# Chaining Permissions

```bash

```