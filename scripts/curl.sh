#!/usr/bin/zsh
# get the token
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=mmerrell@gmail.com&password=a"

# plug the token here
curl -X POST http://localhost:8000/orders/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtbWVycmVsbEBnbWFpbC5jb20iLCJleHAiOjE3NjIxMjA3MzZ9.x7e-AqSjL5jfQbe-xqgC14Kzt1cGbWGPIkCQ3z-3beQ" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":1}]}'
{"message":"Order creation started","workflow_id":"create-order-1-1762118963"}
