# Profile-service

The profile service is responsible for Login and logout and store JWT tokens in the UserToken database.

After receiving the confirmation from the user service, the profile service will send the username and id to the token service to generate the refresh and access tokens then store them in the UserTokens table.

## Tables

The access token is valid for 60 minutes. The refresh token is valid for 24 hours. The username and Token Data are stored in the UserTokens table.

The UserTokens table consists of the following fields:

| Field Name | Data Type | Description |
| ---------- | --------- | ----------- |
| id         | Integer   | ID          |
| username   | String    | User Name   |
| token_data | JSON      | Token Data  |

token_data consists of the following fields:
| Field Name | Data Type | Description   |
| ---------- | --------- | ------------- |
| token      | String    | Refresh Token |
| token      | String    | Access Token  |

## How to use the profile service

You can use the profile service by sending a POST request to the https://localhost:3000/api/login/ endpoint with the username and password in the body and it will send a message through the message broker to the user service to check the username and password, after receiving the confirmation from the user service, the profile service will send the username to the token service to generate the refresh and access tokens then store them in the UserTokens table.

You can use the profile service by sending a user-id in a POST request to the https://localhost:3000/api/logout/ endpoint. It will delete the id, username and token_data from the UserTokens table.