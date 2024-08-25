import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from game_data.models import GameHistory, GameStat
from django.utils.timezone import now
from datetime import datetime

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_create_game_history(api_client):
    url = reverse('game-history-list') # reverse() is used to generate the URL for the 'game-history-list' view
    data = {
        'player1_username': 'player1',
        'player1_id': 1,
        'player2_username': 'player2',
        'player2_id': 2,
        'winner_id': 1,
        'start_time': '2024-07-03T12:00:00Z'
    }
    response = api_client.post(url, data, format='json') # send a POST request to the URL with the data as the request body
    assert response.status_code == status.HTTP_201_CREATED
    assert GameHistory.objects.count() == 1 # Objects count should be 1 after creating a new GameHistory object in the database
    game_history = GameHistory.objects.first() # Get the first GameHistory object from the database (there should be only one) because we just created it
    assert game_history.player1_username == 'player1'
    assert game_history.player1_id == 1 # The player1_id should be 1 because we set it to 1 in the data
    assert game_history.player2_username == 'player2'
    assert game_history.player2_id == 2 # The player2_id should be 2 because we set it to 2 in the data
    assert game_history.winner_id == 1 # The winner_id should be 1 because we set it to 1 in the data
    assert game_history.start_time.isoformat() == '2024-07-03T12:00:00+00:00' # The start_time should be '2024-07-03T12:00:00+00:00' because we set it to that value in the data
    assert game_history.end_time is None

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
    game = GameHistory.objects.create(player1_username='player1', player1_id=1, player2_username='player2', player2_id=2, winner_id=1, start_time=now())

    url = reverse('game-history-detail', args=[game.pk])
    data = {
        'player1_username': 'player1_updated',
        'player1_id': 1,
        'player2_username': 'player2_updated',
        'player2_id': 2,
        'winner_id': 2,
        'start_time': game.start_time.isoformat().replace('+00:00', 'Z')
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    game.refresh_from_db()
    assert game.player1_username == 'player1_updated'
    assert game.player2_username == 'player2_updated'
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

@pytest.mark.django_db
def test_primary_key_increment(api_client):
    initial_count = GameHistory.objects.count()

    data = {
        'player1_username': 'player1',
        'player1_id': 1,
        'player2_username': 'player2',
        'player2_id': 2,
        'winner_id': 1,
        'start_time': '2024-07-03T12:00:00Z',
        'end_time': '2024-07-03T12:30:00Z'
    }
    response = api_client.post('/game-history/', data, format='json')
    assert response.status_code == 201

    new_count = GameHistory.objects.count()
    assert new_count == initial_count + 1

    latest_entry = GameHistory.objects.latest('game_id')
    print(latest_entry.game_id)

@pytest.mark.django_db
def test_create_game_stat(api_client):
    game = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())
    url = reverse('gamestat-list')
    data = {
        'game_id': game.game_id,
        'player1_score': 10,
        'player2_score': 5,
        'player1_hits': 0,
        'player2_hits': 2,
        'longest_rally': 4
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert GameStat.objects.count() == 1
    game_stat = GameStat.objects.first()
    assert game_stat.player1_score == 10
    assert game_stat.player2_score == 5
    assert game_stat.player1_hits == 0
    assert game_stat.player2_hits == 2
    assert game_stat.longest_rally == 4

@pytest.mark.django_db
def test_list_game_stat(api_client):
    game1 = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())
    GameStat.objects.create(game_id=game1, player1_score=10, player2_score=5, player1_hits=0, player2_hits=2, longest_rally=4)

    game2 = GameHistory.objects.create(player1_id=3, player2_id=4, winner_id=4, start_time=now())
    GameStat.objects.create(game_id=game2, player1_score=8, player2_score=7, player1_hits=20, player2_hits=0, longest_rally=5)

    url = reverse('gamestat-list')
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['player1_score'] == 10
    assert response.data[0]['player2_score'] == 5
    assert response.data[0]['player1_hits'] == 0
    assert response.data[0]['player2_hits'] == 2
    assert response.data[0]['longest_rally'] == 4
    assert response.data[1]['player1_score'] == 8
    assert response.data[1]['player2_score'] == 7
    assert response.data[1]['player1_hits'] == 20
    assert response.data[1]['player2_hits'] == 0
    assert response.data[1]['longest_rally'] == 5

@pytest.mark.django_db
def test_retrieve_game_stat(api_client):
    game = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())
    game_stat = GameStat.objects.create(game_id=game, player1_score=10, player2_score=5, player1_hits=15, player2_hits=2, longest_rally=4)

    url = reverse('gamestat-detail', args=[game_stat.pk])
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['player1_score'] == game_stat.player1_score
    assert response.data['player2_score'] == game_stat.player2_score
    assert response.data['player1_hits'] == game_stat.player1_hits
    assert response.data['player2_hits'] == game_stat.player2_hits
    assert response.data['longest_rally'] == game_stat.longest_rally

@pytest.mark.django_db
def test_update_game_stat(api_client):
    game = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())
    game_stat = GameStat.objects.create(game_id=game, player1_score=10, player2_score=5, player1_hits=15, player2_hits=2, longest_rally=4)

    url = reverse('gamestat-detail', args=[game_stat.pk])
    data = {
        'game_id': game.game_id,
        'player1_score': 12,
        'player2_score': 6,
        'player1_hits': 18,
        'player2_hits': 0,
        'longest_rally': 5
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    game_stat.refresh_from_db()
    assert game_stat.player1_score == 12
    assert game_stat.player2_score == 6
    assert game_stat.player1_hits == 18
    assert game_stat.player2_hits == 0
    assert game_stat.longest_rally == 5

@pytest.mark.django_db
def test_delete_game_stat(api_client):
    game = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time=now())
    game_stat = GameStat.objects.create(game_id=game, player1_score=10, player2_score=5, player1_hits=15, player2_hits=2, longest_rally=4)

    url = reverse('gamestat-detail', args=[game_stat.pk])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert GameStat.objects.count() == 0
