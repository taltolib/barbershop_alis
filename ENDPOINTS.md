# Эндпоинты The Vanguard — чек-лист

Контракт: `front/vanguard-frontend/API.md`. Эталон поведения (формат ответа, проверки, коды ошибок): `front/vanguard-frontend/assets/js/mock.js`, в скобках указаны строки.

Всего **67**: public 11 · auth 4 · owner 43 · master 9.

## 0. Каркас (до эндпоинтов)
- [ ] Ошибки в формате `{"detail": "текст"}`. Обработчик 422 переопределить: у FastAPI `detail` по умолчанию массив, а фронту нужна строка.
- [ ] Сессия в httpOnly-куке + таблица `sessions` (чтобы сбрасывать сессии при блокировке и смене пароля)
- [ ] CSRF: на POST/PUT/PATCH/DELETE в `/api/auth|owner|master/*` требовать заголовок `X-Requested-With: vanguard`, иначе 403
- [ ] Зависимости `require_owner` (иначе 403) и `require_barber` (у пользователя есть `barber_id`, в том числе у владельца)
- [ ] `StaticFiles` для `site/`, `admin/`, `assets/` и `/media/` (загруженные фото) на том же домене, тогда CORS не нужен
- [ ] Таблицы: `users`, `sessions`, `barbers`, `barber_services`, `categories`, `services`, `bookings`, `promos`, `portfolio_items`, `reviews`, `settings`, `audit_log`
- [ ] Индекс: `UNIQUE (barber_id, date, time) WHERE status <> 'cancelled'` на `bookings`

## 1. Авторизация `/api/auth` (mock.js:360–373)
- [ ] `POST /api/auth/login` — ставит куку, возвращает `Me`; 401 / 403 (заблокирован) / 429
- [ ] `POST /api/auth/logout` — `{ok}`
- [ ] `GET  /api/auth/me` — `Me` или 401
- [ ] `POST /api/auth/password` — 400 при неверном текущем пароле; сбросить остальные сессии

## 2. Прайс, мастера, настройки (шеф)
**Категории** (mock.js:501–511)
- [ ] `GET    /api/owner/categories`
- [ ] `POST   /api/owner/categories`
- [ ] `PATCH  /api/owner/categories/{id}`
- [ ] `DELETE /api/owner/categories/{id}` — непустая → 409

**Услуги** (mock.js:515–543)
- [ ] `GET    /api/owner/services` — с `barber_ids`
- [ ] `POST   /api/owner/services`
- [ ] `PATCH  /api/owner/services/{id}` — изменение цены писать в журнал
- [ ] `DELETE /api/owner/services/{id}` — есть в записях или акциях → 409

**Мастера** (mock.js:431–489)
- [ ] `GET    /api/owner/barbers`
- [ ] `POST   /api/owner/barbers` — вернуть сгенерированный `password` один раз; логин занят → 409
- [ ] `PATCH  /api/owner/barbers/{id}`
- [ ] `DELETE /api/owner/barbers/{id}` — есть записи → 409
- [ ] `POST   /api/owner/barbers/{id}/photo` — multipart `file`
- [ ] `POST   /api/owner/barbers/{id}/block` — сбросить его сессии; владельца нельзя (400)
- [ ] `POST   /api/owner/barbers/{id}/unblock`
- [ ] `POST   /api/owner/barbers/{id}/reset-password` — сбросить его сессии

**Настройки** (mock.js:635–647)
- [ ] `GET  /api/owner/settings`
- [ ] `PUT  /api/owner/settings` — `{values: {...}}`, частичное обновление + валидация
- [ ] `POST /api/owner/settings/image?key=hero_image|about_image_main|about_image_side`

## 3. Публичный сайт и онлайн-запись `/api/public` (mock.js:306–337)
- [ ] `GET  /api/public/site` — без `allow_master_promos` и `max_master_discount_pct`
- [ ] `GET  /api/public/barbers` — только `active` + `show_on_site`, без телефонов и логинов
- [ ] `GET  /api/public/catalog` — без пустых категорий и неактивных услуг
- [ ] `GET  /api/public/days?barber_id=`
- [ ] `GET  /api/public/slots?barber_id=&service_id=&date=` — его же вызывает админка шефа (`owner.js:181`)
- [ ] `POST /api/public/bookings` — **самый важный**: `SELECT … FOR UPDATE` строки мастера + уникальный индекс → 409; `website` заполнен → 400; имя/телефон → 422

## 4. Записи и обзор (шеф) (mock.js:384–415)
- [ ] `GET   /api/owner/dashboard`
- [ ] `GET   /api/owner/bookings?date=&days=&barber_id=`
- [ ] `POST  /api/owner/bookings` — время любое, проверяется только пересечение (409)
- [ ] `PATCH /api/owner/bookings/{id}` — при переносе или возврате из `cancelled` проверять пересечение

## 5. Кабинет мастера `/api/master` (mock.js:659–716)
- [ ] `GET    /api/master/me`
- [ ] `GET    /api/master/bookings?date=&days=7`
- [ ] `PATCH  /api/master/bookings/{id}` — только свои, только `confirmed | completed | no_show`
- [ ] `GET    /api/master/portfolio`
- [ ] `POST   /api/master/portfolio` — multipart, статус `pending`
- [ ] `DELETE /api/master/portfolio/{id}` — только свои
- [ ] `GET    /api/master/promos`
- [ ] `POST   /api/master/promos` — 403 приём закрыт / 400 чужая услуга / 422 скидка
- [ ] `DELETE /api/master/promos/{id}` — только `pending`, иначе 409

## 6. Модерация
**Акции, шеф** (mock.js:553–587)
- [ ] `GET    /api/owner/promos?status=`
- [ ] `POST   /api/owner/promos` — сразу `approved`
- [ ] `PATCH  /api/owner/promos/{id}`
- [ ] `DELETE /api/owner/promos/{id}`
- [ ] `POST   /api/owner/promos/{id}/approve` — `{comment}`
- [ ] `POST   /api/owner/promos/{id}/reject` — `{comment}`
- [ ] `POST   /api/owner/promos/{id}/archive`
- [ ] `POST   /api/owner/promos/{id}/image` — multipart

**Портфолио, шеф** (mock.js:595–622)
- [ ] `GET    /api/owner/portfolio?status=&barber_id=`
- [ ] `POST   /api/owner/portfolio` — multipart, сразу `approved`
- [ ] `PATCH  /api/owner/portfolio/{id}`
- [ ] `DELETE /api/owner/portfolio/{id}`
- [ ] `POST   /api/owner/portfolio/{id}/approve`
- [ ] `POST   /api/owner/portfolio/{id}/reject`

**Отзывы, шеф** (mock.js:628–634)
- [ ] `GET    /api/owner/reviews?status=`
- [ ] `POST   /api/owner/reviews/{id}/approve`
- [ ] `POST   /api/owner/reviews/{id}/reject`
- [ ] `DELETE /api/owner/reviews/{id}`

**Публичные** (mock.js:311–354)
- [ ] `GET  /api/public/promos` — `approved`, не истекла, услуга активна, лимит не исчерпан
- [ ] `GET  /api/public/portfolio`
- [ ] `GET  /api/public/reviews` — `{rating, count, items}` (последние 6)
- [ ] `POST /api/public/reviews` — статус `pending`; `website` заполнен → 400
- [ ] `POST /api/public/portfolio/views` — `{ids}` → +1 к `views`

## 7. Журнал и безопасность (mock.js:651–652)
- [ ] `GET  /api/owner/audit?limit=&level=warn`
- [ ] `POST /api/owner/security/lock-masters` — сбросить сессии всех мастеров
- [ ] Писать в журнал: вход и неудачный вход, изменение цены, модерацию, блокировку, сброс пароля
- [ ] Rate limit: вход (8 неудач за 15 мин), брони и отзывы с одного IP

## На что легко наткнуться
- «Сегодня» считается в часовом поясе салона, а не сервера и не UTC.
- `slots_used` у акции — это записи по ней со статусом ≠ `cancelled`; тот же лимит проверяется при брони.
- Цена брони = `promo_price`, если есть `promo_id`, иначе `service.price`.
- Загрузка фото: не больше 15 МБ, проверять, что файл действительно картинка.

## Как подключить фронт
1. `front/vanguard-frontend/assets/js/config.js` → `mock: false`
2. Убрать `<script src="../assets/js/mock.js">` из `site/*.html` и `admin/*.html`
3. Проверить сценарий: вход `owner` → категория, услуга, мастер → запись с сайта → видна у шефа и мастера → акция от мастера → одобрение → акция на сайте
