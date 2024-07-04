import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from game_data.models import GameHistory
from django.utils.timezone import now
from datetime import datetime

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_create_game_history(api_client):
    url = reverse('game-history-list') # reverse() is used to generate the URL for the 'game-history-list' view
    data = {
        'player1_id': 1,
        'player2_id': 2,
        'winner_id': 1,
        'start_time': '2024-07-03T12:00:00Z'
    }
    response = api_client.post(url, data, format='json') # send a POST request to the URL with the data as the request body
    assert response.status_code == status.HTTP_201_CREATED
    assert GameHistory.objects.count() == 1 # Objects count should be 1 after creating a new GameHistory object in the database
    game_history = GameHistory.objects.first() # Get the first GameHistory object from the database
    assert game_history.player1_id == 1
    assert game_history.player2_id == 2
    assert game_history.winner_id == 1
    assert game_history.start_time.isoformat() == '2024-07-03T12:00:00+00:00'
    assert game_history.end_time is not None

@pytest.mark.django_db
def test_list_game_histories(api_client):
    game1 = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())
    game2 = GameHistory.objects.create(player1_id=3, player2_id=4, winner_id=4, start_time=now())

    url = reverse('game-history-list')
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2 # The response should contain two GameHistory objects in the data field because we created two GameHistory objects in the database
    assert response.data[0]['player1_id'] == game1.player1_id
    assert response.data[0]['player2_id'] == game1.player2_id
    assert response.data[0]['winner_id'] == game1.winner_id

    start_time_response = datetime.fromisoformat(response.data[0]['start_time'].replace('Z', '+00:00'))
    start_time_expected = game1.start_time
    assert start_time_response == start_time_expected

    assert response.data[1]['player1_id'] == game2.player1_id
    assert response.data[1]['player2_id'] == game2.player2_id
    assert response.data[1]['winner_id'] == game2.winner_id

    start_time_response = datetime.fromisoformat(response.data[1]['start_time'].replace('Z', '+00:00'))
    start_time_expected = game2.start_time
    assert start_time_response == start_time_expected

@pytest.mark.django_db
def test_retrieve_game_history(api_client):
    game = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())

    url = reverse('game-history-detail', args=[game.pk])
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['player1_id'] == game.player1_id
    assert response.data['player2_id'] == game.player2_id
    assert response.data['winner_id'] == game.winner_id
    assert response.data['start_time'] == game.start_time.isoformat().replace('+00:00', 'Z')

@pytest.mark.django_db
def test_update_game_history(api_client):
    game = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())

    url = reverse('game-history-detail', args=[game.pk])
    data = {
        'player1_id': 1,
        'player2_id': 2,
        'winner_id': 2,
        'start_time': game.start_time.isoformat().replace('+00:00', 'Z')
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    game.refresh_from_db()
    assert game.winner_id == 2

@pytest.mark.django_db
def test_delete_game_history(api_client):
    game = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())

    url = reverse('game-history-detail', args=[game.pk])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert GameHistory.objects.count() == 0

@pytest.mark.django_db
def test_create_game_history_validation_error(api_client):
    url = reverse('game-history-list')
    data = {
        'player1_id': 1,
        # 'player2_id' is missing
        'winner_id': 1,
        'start_time': '2024-07-03T12:00:00Z'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'player2_id' in response.data
