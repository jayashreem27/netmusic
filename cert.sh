#!/bin/bash

# Generate Certificate Authority (CA)
openssl genpkey -algorithm RSA -out ca.key
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 -out ca.crt

# Generate Server Key and Certificate
openssl genpkey -algorithm RSA -out server.key
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256
rm ./ca.* ./server.csr
