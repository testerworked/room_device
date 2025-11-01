#!/bin/bash

BASE_URL="http://localhost:5000/api"

echo "=== Flask Chat API Demo ==="
echo

# 1. Проверка здоровья API
echo "1. Проверка здоровья API:"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo

# 2. Регистрация первого пользователя
echo "2. Регистрация пользователя Alice:"
ALICE_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "Alice"}')
echo "$ALICE_RESPONSE" | python3 -m json.tool

ALICE_DEVICE_ID=$(echo "$ALICE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['device_id'])")
echo "Device ID Alice: $ALICE_DEVICE_ID"
echo

# 3. Регистрация второго пользователя
echo "3. Регистрация пользователя Bob:"
BOB_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "Bob"}')
echo "$BOB_RESPONSE" | python3 -m json.tool

BOB_DEVICE_ID=$(echo "$BOB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['device_id'])")
echo "Device ID Bob: $BOB_DEVICE_ID"
echo

# 4. Alice отправляет сообщение
echo "4. Alice отправляет сообщение:"
curl -s -X POST "$BASE_URL/send_message" \
  -H "Content-Type: application/json" \
  -d "{\"device_id\": \"$ALICE_DEVICE_ID\", \"message\": \"Привет всем! Как дела?\"}" | python3 -m json.tool
echo

# 5. Bob отправляет сообщение
echo "5. Bob отправляет сообщение:"
curl -s -X POST "$BASE_URL/send_message" \
  -H "Content-Type: application/json" \
  -d "{\"device_id\": \"$BOB_DEVICE_ID\", \"message\": \"Привет Alice! Все отлично, а у тебя?\"}" | python3 -m json.tool
echo

# 6. Alice отправляет второе сообщение
echo "6. Alice отправляет второе сообщение:"
curl -s -X POST "$BASE_URL/send_message" \
  -H "Content-Type: application/json" \
  -d "{\"device_id\": \"$ALICE_DEVICE_ID\", \"message\": \"Тоже хорошо! Рада общению!\"}" | python3 -m json.tool
echo

# 7. Получение всех сообщений (от Alice)
echo "7. Alice получает все сообщения:"
curl -s "$BASE_URL/messages?device_id=$ALICE_DEVICE_ID" | python3 -m json.tool
echo

# 8. Получение последних 2 сообщений (от Bob)
echo "8. Bob получает последние 2 сообщения:"
curl -s "$BASE_URL/messages/latest?device_id=$BOB_DEVICE_ID&limit=2" | python3 -m json.tool
echo

# 9. Получение профиля Alice
echo "9. Профиль Alice:"
curl -s "$BASE_URL/user/profile?device_id=$ALICE_DEVICE_ID" | python3 -m json.tool
echo

# 10. Получение списка онлайн пользователей
echo "10. Список онлайн пользователей:"
curl -s "$BASE_URL/online_users?device_id=$ALICE_DEVICE_ID" | python3 -m json.tool
echo

# 11. Попытка отправить сообщение с неверным device_id
echo "11. Попытка отправить сообщение с неверным device_id:"
curl -s -X POST "$BASE_URL/send_message" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "wrong-device-id", "message": "Это сообщение не отправится"}' | python3 -m json.tool
echo

echo "=== Демонстрация завершена ==="