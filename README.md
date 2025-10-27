# Package
https://pypi.org/project/allocine-seances/
```
pip install allocine-seances
```

# Warning
- v0.0.11 : Modification du paramètre day_shift en date_str
- v0.0.12 : Correction du endpoint /cinema

# Description
Objectif : récupération des horaires des séances de cinéma.

Les méthodes ```get_top_villes()```, ```get_departements()``` et ```get_circuit()``` retournent un id d’emplacement.

La méthode ```get_cinema(id_location)``` retourne un id de cinéma pour un emplacement donné.

La méthode ```get_showtime(id_cinema, date_str)``` retourne la liste des séances pour un cinema donné et un jour.

# Import

```python
from allocineAPI.allocineAPI import allocineAPI

api = allocineAPI()
```
# Liste des méthodes
## Listes des villes
```python
ret = api.get_top_villes()
# {'id': 'ville-87860', 'name': 'Aix-en-Provence'}
# {'id': 'ville-96943', 'name': 'Bordeaux'}
# {'id': 'ville-85268', 'name': 'Cannes'}
# {'id': 'ville-110514', 'name': 'Clermont-Ferrand'}
# ...
```

## Liste des départements
```python
ret = api.get_departements()
# {'id': 'departement-83191', 'name': 'Ain'}
# {'id': 'departement-83178', 'name': 'Aisne'}
# {'id': 'departement-83111', 'name': 'Allier'}
# {'id': 'departement-83185', 'name': 'Alpes de Haute-Provence'}
# ...
```
## Liste des circuits
```python
ret = api.get_circuit()
# {'id': 'circuit-81002', 'name': 'Pathé Cinémas'}
# {'id': 'circuit-81005', 'name': 'CGR'}
# {'id': 'circuit-4750', 'name': 'UGC'}
# {'id': 'circuit-81027', 'name': 'Megarama'}
# ...
```

## liste des cinemas
```python
cinemas = api.get_cinema("departement-83191")
# {'id': 'B0242', 'name': 'Gaumont Stade de France - 4DX', 'address': '8, rue du Mondial 98 93210 Saint-Denis'}
# {'id': 'C0037', 'name': 'Pathé Alésia - Dolby Cinema', 'address': '73 avenue du Général Leclerc 75014 Paris 14e arrondissement'}
# {'id': 'C0116', 'name': 'Gaumont Aquaboulevard - 4DX', 'address': '8-16, rue du Colonel-Pierre-Avia 75015 Paris 13e arrondissement'}
# {'id': 'C0161', 'name': 'Pathé Convention', 'address': '27, rue Alain-Chartier 75015 Paris'}
# ...
```

## liste des seances
```python
data = api.get_showtime("W2920", "2024-01-01")
# {'title': 'Les Aventures de Ricky', 'duration': '1h 25min', 'VF': [], 'VO': ['2023-04-15T13:45:00', '2023-04-15T15:45:00']}
# {'title': "Donjons & Dragons : L'Honneur des voleurs", 'duration': '2h 14min', 'VF': [], 'VO': ['2023-04-15T10:30:00', '2023-04-15T13:45:00', '2023-04-15T17:00:00', '2023-04-15T18:25:00', '2023-04-15T21:00:00']}
# {'title': 'Une histoire d’amour', 'duration': '1h 30min', 'VF': [], 'VO': ['2023-04-15T14:40:00', '2023-04-15T16:45:00', '2023-04-15T19:50:00', '2023-04-15T21:55:00']}
# {'title': 'Princes et princesses : le spectacle au cinéma', 'duration': '1h 00min', 'VF': [], 'VO': ['2023-04-15T10:50:00']}
# ...
```