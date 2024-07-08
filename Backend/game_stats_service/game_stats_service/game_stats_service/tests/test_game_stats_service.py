import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from game_stats.models import game_dataGameStats

@pytest.fixture # This decorator is used to create fixtures, which are reusable components that can be used in multiple test functions
def api_client():
    return APIClient()

@pytest.mark.django_db # This decorator is used to tell pytest to use a Django test database
def test_create_game_stat(api_client):
    url = reverse('gamestats-list')
    data = {
        'player1_score': 10,
        'player2_score': 8,
        'total_hits': 50,
        'longest_rally': 12
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert game_dataGameStats.objects.count() == 1
    assert response.data['player1_score'] == 10
    assert response.data['player2_score'] == 8

@pytest.mark.django_db
def test_list_game_stats(api_client):
    game1 = game_dataGameStats.objects.create(player1_score=10, player2_score=5, total_hits=40, longest_rally=15)
    game2 = game_dataGameStats.objects.create(player1_score=20, player2_score=10, total_hits=80, longest_rally=20)

    url = reverse('gamestats-list')
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2 # Check if the response contains two game stats objects in the list because we created two game stats objects

@pytest.mark.django_db
def test_retrieve_game_stat(api_client):
    game = game_dataGameStats.objects.create(player1_score=15, player2_score=7, total_hits=60, longest_rally=18)

    url = reverse('gamestats-detail', kwargs={'pk': game.game_id})
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['player1_score'] == 15

@pytest.mark.django_db
def test_update_game_stat(api_client):
    game = game_dataGameStats.objects.create(player1_score=10, player2_score=5, total_hits=40, longest_rally=15)

    url = reverse('gamestats-detail', kwargs={'pk': game.game_id})
    data = {
        'player1_score': 20,
        'player2_score': 15,
        'total_hits': 85,
        'longest_rally': 25
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    game.refresh_from_db()
    assert game.player1_score == 20

@pytest.mark.django_db
def test_delete_game_stat(api_client):
    game = game_dataGameStats.objects.create(player1_score=10, player2_score=5, total_hits=40, longest_rally=15) # Create a game stats object

    url = reverse('gamestats-detail', kwargs={'pk': game.game_id}) # Get the URL for the game stats object
    response = api_client.delete(url) # Send a DELETE request to the URL
    assert response.status_code == status.HTTP_204_NO_CONTENT # Check if the response status code is 204 (No Content)
    assert game_dataGameStats.objects.count() == 0 # Check if the game stats object has been deleted from the database
