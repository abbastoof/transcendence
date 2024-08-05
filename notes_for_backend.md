
### Whenever succesfull loggin in:
signup.js:89 
 POST https://localhost:3000/user/register/ 400 (Bad Request)
(anonymous)	@	signup.js:89
signup.js:108 Error: 
Error: Bad Request
    at signup.js:98:23
(anonymous)	@	signup.js:108
Promise.catch (async)		
(anonymous)	@	signup.js:107

## API's
- Place to store avatar
- Logging out
- Where to fetch other user data for friend profile

### Every first login:
login.js:43 
 POST https://localhost:3000/auth/login/ 500 (Internal Server Error)
(anonymous)	@	login.js:43
login.js:69 Error: 
Error: Invalid username or password
    at login.js:52:23
(anonymous)	@	login.js:69
Promise.catch (async)		
(anonymous)	@	login.js:68