## 1. ?꾨줈?앺듃 湲곕컲 ?ㅼ젙

- [x] 1.1 ?붾젆?좊━ 援ъ“ ?앹꽦 (api/, frontend/, tests/)
- [x] 1.2 requirements.txt ?묒꽦 (fastapi, uvicorn, sqlalchemy, python-jose, bcrypt, httpx, pytest)
- [x] 1.3 .env.example ?묒꽦 (DATABASE_URL, SECRET_KEY, ALLOWED_ORIGINS)
- [x] 1.4 .gitignore ?묒꽦 (*.db, .env, __pycache__, .vercel)
- [x] 1.5 api/database.py ?묒꽦 (SQLAlchemy engine, session, DATABASE_URL ?섍꼍蹂??

## 2. DB 紐⑤뜽 (SQLAlchemy)

- [x] 2.1 api/models.py ??users ?뚯씠釉?(id, email, password_hash, team_id FK, created_at)
- [x] 2.2 api/models.py ??teams ?뚯씠釉?(id, name, invite_code UNIQUE, owner_id FK, created_at)
- [x] 2.3 api/models.py ??tasks ?뚯씠釉?(id, team_id FK, title, status, creator_id FK, assignee_id FK nullable, created_at)
- [x] 2.4 api/models.py ??messages ?뚯씠釉?(id, team_id FK, user_id FK, content, created_at)
- [x] 2.5 ?몃뜳??異붽? (tasks.team_id+created_at, messages.team_id+created_at, teams.invite_code)

## 3. ?몄쬆 ?좏떥由ы떚

- [x] 3.1 api/auth.py ??bcrypt 鍮꾨?踰덊샇 ?댁떆/寃利??⑥닔
- [x] 3.2 api/auth.py ??JWT ?앹꽦 ?⑥닔 (24h 留뚮즺, HS256)
- [x] 3.3 api/auth.py ??JWT 寃利?FastAPI Dependency (Bearer ?좏겙 ?뚯떛, 留뚮즺 ??401)
- [x] 3.4 api/schemas.py ??Pydantic 紐⑤뜽 (UserCreate, UserLogin, TeamCreate, TaskCreate ??

## 4. Auth API (4媛??붾뱶?ъ씤??

- [x] 4.1 POST /auth/signup ???대찓??以묐났 泥댄겕, bcrypt ?댁떆, JWT 諛섑솚
- [x] 4.2 POST /auth/login ???먭꺽利앸챸 寃利? JWT 諛섑솚, team_id ?ы븿
- [x] 4.3 GET /auth/me ???꾩옱 ?ъ슜???뺣낫 諛섑솚
- [x] 4.4 POST /auth/logout ??200 諛섑솚 (stateless)

## 5. Team API (5媛??붾뱶?ъ씤??

- [x] 5.1 POST /teams ??? ?앹꽦, 珥덈?肄붾뱶(AAAA-9999) ?먮룞 ?앹꽦, users.team_id UPDATE
- [x] 5.2 POST /teams/join ??珥덈?肄붾뱶 寃利? users.team_id UPDATE, ? ?뺣낫 諛섑솚
- [x] 5.3 GET /teams/{id} ??? ?뺣낫 諛섑솚 (硫ㅻ쾭??寃利?誘몃뱾?⑥뼱)
- [x] 5.4 GET /teams/{id}/members ??硫ㅻ쾭 紐⑸줉 諛섑솚 (owner ?쒖떆)
- [x] 5.5 DELETE /teams/{id}/leave ??users.team_id NULL ?ㅼ젙 (owner 李⑤떒)

## 6. Task API (6媛??붾뱶?ъ씤??

- [x] 6.1 GET /teams/{id}/tasks ??紐⑸줉 諛섑솚 (filter=me/unassigned, created_at desc)
- [x] 6.2 POST /teams/{id}/tasks ???쒖뒪???앹꽦 (湲곕낯 status=TODO)
- [x] 6.3 GET /tasks/{id} ???⑥씪 ?쒖뒪???곸꽭
- [x] 6.4 PUT /tasks/{id} ???쒕ぉ쨌assignee ?섏젙
- [x] 6.5 PATCH /tasks/{id}/status ???곹깭 蹂寃?(TODO/DOING/DONE 寃利?
- [x] 6.6 DELETE /tasks/{id} ??creator ?먮뒗 owner留???젣 媛??(403 泥섎━)

## 7. Message API (3媛??붾뱶?ъ씤??

- [x] 7.1 GET /teams/{id}/messages ??理쒓렐 50媛?諛섑솚, since= 利앸텇 議고쉶 吏??- [x] 7.2 POST /teams/{id}/messages ??1-1000??寃利? 硫붿떆吏 ???- [x] 7.3 DELETE /messages/{id} ??蹂몄씤留???젣 (owner?????硫붿떆吏 遺덇?)

## 8. FastAPI ???ㅼ젙

- [x] 8.1 api/main.py ??FastAPI ???앹꽦, ?쇱슦???깅줉, CORS ?ㅼ젙
- [x] 8.2 api/main.py ??Swagger UI ?쒖꽦??(/docs, /openapi.json)
- [x] 8.3 api/main.py ???꾩뿭 ?먮윭 ?몃뱾??({ error: { code, message } } ?뺥깭 ?듭씪)
- [x] 8.4 vercel.json ?묒꽦 (routes: /api/* ??FastAPI, /* ??frontend/)

## 9. pytest ?뚯뒪??
- [x] 9.1 tests/conftest.py ??TestClient ?ㅼ젙, SQLite in-memory DB fixture, ?좎?/? ?쎌뒪泥?- [x] 9.2 tests/test_auth.py ??signup(?뺤긽/以묐났/?좏슚??, login(?뺤긽/?ㅻ쪟), me, logout
- [x] 9.3 tests/test_teams.py ??? ?앹꽦, ?⑸쪟(?뺤긽/404/409), 硫ㅻ쾭 紐⑸줉, 鍮꾨ħ踰?403
- [x] 9.4 tests/test_tasks.py ??CRUD ?뺤긽 ?먮쫫, ?곹깭 蹂寃? ??젣 沅뚰븳(creator/owner/403)
- [x] 9.5 tests/test_messages.py ???꾩넚(?뺤긽/1000??珥덇낵), since= 議고쉶, ??젣(蹂몄씤/403)

## 10. Frontend ??怨듯넻

- [x] 10.1 frontend/js/api.js ??fetch ?섑띁 (JWT ?ㅻ뜑 ?먮룞 泥⑤?, 401 ??localStorage ??젣 + redirect)
- [x] 10.2 frontend/js/auth.js ??localStorage token ????쎄린/??젣, 濡쒓렇???곹깭 ?뺤씤
- [x] 10.3 Tailwind Play CDN ?ㅽ겕由쏀듃 ?쒓렇 怨듯넻 ?덉씠?꾩썐

## 11. Frontend ???몄쬆 ?붾㈃

- [x] 11.1 frontend/login.html ???대찓??鍮꾨?踰덊샇 ?? 濡쒓렇??API ?몄텧, team_id 遺꾧린 redirect
- [x] 11.2 frontend/signup.html ???뚯썝媛???? ?대씪?댁뼵???좏슚??寃?? ?깃났 ??濡쒓렇???붾㈃ ?대룞

## 12. Frontend ??? ?붾㈃

- [x] 12.1 frontend/team.html ??? 留뚮뱾湲???(POST /teams), 珥덈?肄붾뱶 ?쒖떆/蹂듭궗
- [x] 12.2 frontend/team.html ??珥덈?肄붾뱶 ?⑸쪟 ??(POST /teams/join), ?먮윭 ?쒖떆

## 13. Frontend ??移몃컲 ?붾㈃

- [x] 13.1 frontend/kanban.html ??3而щ읆 ?덉씠?꾩썐 (TODO/DOING/DONE), ?ㅻ뜑 ?ㅻ퉬寃뚯씠??- [x] 13.2 frontend/js/kanban.js ??GET /tasks 議고쉶 諛?移대뱶 ?뚮뜑留? ?꾪꽣(?꾩껜/@me/誘명븷??
- [x] 13.3 frontend/js/kanban.js ??+ 踰꾪듉 ?몃씪???낅젰, POST /tasks 移대뱶 ?앹꽦
- [x] 13.4 frontend/js/kanban.js ??HTML5 drag & drop, PATCH /tasks/{id}/status ?몄텧
- [x] 13.5 frontend/js/kanban.js ??移대뱶 ?대┃ 紐⑤떖 (?쒕ぉ/status/assignee ?섏젙, ??젣)
- [x] 13.6 frontend/kanban.html ??諛섏쓳??768px breakpoint (紐⑤컮?? ???꾪솚)

## 14. Frontend ??梨꾪똿 ?붾㈃

- [x] 14.1 frontend/chat.html ??硫붿떆吏 由ъ뒪?? ?낅젰李? ?꾩넚 踰꾪듉
- [x] 14.2 frontend/js/chat.js ??GET /messages 珥덇린 議고쉶, 5珥?setInterval ?대쭅 (since=)
- [x] 14.3 frontend/js/chat.js ??POST /messages ?꾩넚, 1000??移댁슫??(珥덇낵 ??踰꾪듉 鍮꾪솢?깊솕)
- [x] 14.4 frontend/js/chat.js ??蹂몄씤 硫붿떆吏 ?몃쾭 ????젣 踰꾪듉 ?쒖떆, DELETE /messages/{id}
- [x] 14.5 frontend/chat.html ??諛섏쓳??768px breakpoint (紐⑤컮????ㅽ겕由?

## 15. 諛고룷 ?ㅼ젙

- [x] 15.1 vercel.json ?꾩꽦 (builds: python runtime, routes 留ㅽ븨)
- [x] 15.2 requirements.txt 諛고룷??理쒖쥌 ?뺤씤 (psycopg2-binary ?ы븿)
- [x] 15.3 濡쒖뺄 ?꾩껜 ?숈옉 ?뺤씤 (uvicorn + 釉뚮씪?곗? 怨⑤뱺 ?⑥뒪)
- [x] 15.4 pytest ?꾩껜 ?ㅽ뻾 ?뺤씤 (紐⑤뱺 ?뚯뒪??pass)
- [x] 15.5 Vercel 諛고룷 + Neon DATABASE_URL ?섍꼍蹂???ㅼ젙
- [x] 15.6 諛고룷 ??/docs ?묎렐 諛?怨⑤뱺 ?⑥뒪 ?섎룞 ?뺤씤
