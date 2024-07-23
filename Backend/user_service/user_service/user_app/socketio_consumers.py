import socketio
import requests
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

sio = socketio.AsyncServer(async_mode='asgi')

@sio.event
async def connect(sid, environ):
    user = environ['asgi.scope'].get('user')
    if user and user.is_authenticated:
        await sio.save_session(sid, {'user': user})
        await sio.emit('connect', {'message': 'User connected', 'ENGINE': 'django.db.backends.postgresql'}, room=sid)
        await update_user_status(user, 'online')
    else:
        await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    user = session.get('user')
    if user:
        await update_user_status(user, 'offline')

@sync_to_async
def update_user_status(user, status):
    user_id = user.id
    if user_id:
        response = requests.post(f'http://user-service:8001/user/{user_id}/update-status/', json={
            'user_id': user_id,
            'status': status
        })
        if response.status_code == 200:
            print(f'User status updated to {status}')
        else:
            print(f'Failed to update status for user {user_id}: {response.status_code} - {response.text}')
