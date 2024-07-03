# # game_history/tests/test_game_history.py

# import pytest
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework import status
# from game_data.models import GameHistory

# @pytest.fixture
# def api_client():
#     return APIClient()

# @pytest.mark.django_db
# def test_create_game_history(api_client):
#     url = reverse('gamehistory-list') # reverse() is used to generate the URL for the view name 'gamehistory-list'
#     data = {
#         'player1': 'player1',
#         'player2': 'player2',
#         'winner': 'player1',
#         'score': '21-15'
#     }
#     response = api_client.post(url, data, format='json')
#     assert response.status_code == status.HTTP_201_CREATED
#     assert GameHistory.objects.count() == 1
#     game_history = GameHistory.objects.first()
#     assert game_history.player1 == 'player1'
#     assert game_history.player2 == 'player2'
#     assert game_history.winner == 'player1'
#     assert game_history.score == '21-15'

# @pytest.mark.django_db
# def test_list_game_histories(api_client):
#     game1 = GameHistory.objects.create(player1='player1', player2='player2', winner='player1', score='21-15')
#     game2 = GameHistory.objects.create(player1='player3', player2='player4', winner='player4', score='19-21')

#     url = reverse('gamehistory-list')
#     response = api_client.get(url, format='json')
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) == 2
#     assert response.data[0]['player1'] == game1.player1
#     assert response.data[0]['player2'] == game1.player2
#     assert response.data[0]['winner'] == game1.winner
#     assert response.data[0]['score'] == game1.score
#     assert response.data[1]['player1'] == game2.player1
#     assert response.data[1]['player2'] == game2.player2
#     assert response.data[1]['winner'] == game2.winner
#     assert response.data[1]['score'] == game2.score


# game_history/tests/test_game_history.py

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from game_data.models import GameHistory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_create_game_history(api_client):
    url = reverse('game-history-list')
    data = {
        'player1_id': 1,
        'player2_id': 2,
        'winner_id': 1,
        'start_time': '2024-07-03T12:00:00Z',
        'end_time': '2024-07-03T12:30:00Z'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert GameHistory.objects.count() == 1
    game_history = GameHistory.objects.first()
    assert game_history.player1_id == 1
    assert game_history.player2_id == 2
    assert game_history.winner_id == 1
    assert game_history.start_time.isoformat() == '2024-07-03T12:00:00+00:00'
    assert game_history.end_time.isoformat() == '2024-07-03T12:30:00+00:00'

@pytest.mark.django_db
def test_list_game_histories(api_client):
    game1 = GameHistory.objects.create(player1_id=1, player2_id=2, winner_id=1, start_time='2024-07-03T12:00:00Z', end_time='2024-07-03T12:30:00Z')
    game2 = GameHistory.objects.create(player1_id=3, player2_id=4, winner_id=4, start_time='2024-07-03T13:00:00Z', end_time='2024-07-03T13:30:00Z')

    url = reverse('game-history-list')
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['player1_id'] == game1.player1_id
    assert response.data[0]['player2_id'] == game1.player2_id
    assert response.data[0]['winner_id'] == game1.winner_id
    assert response.data[0]['start_time'] == game1.start_time.isoformat()
    assert response.data[0]['end_time'] == game1.end_time.isoformat()
    assert response.data[1]['player1_id'] == game2.player1_id
    assert response.data[1]['player2_id'] == game2.player2_id
    assert response.data[1]['winner_id'] == game2.winner_id
    assert response.data[1]['start_time'] == game2.start_time.isoformat()
    assert response.data[1]['end_time'] == game2.end_time.isoformat()
