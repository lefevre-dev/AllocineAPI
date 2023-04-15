import json
import requests
from bs4 import BeautifulSoup
from URLs import URLs


class allocineAPI:
    TOP_VILLE_TITLE = "Top villes"
    DEPARTEMENTS_TITLE = "Départements"
    CIRCUIT_TITLE = "Les cinémas par circuit"

    def _get_json_request(self, path, url_params: dict = None) -> dict:
        req = requests.get(path, params=url_params)
        if req.status_code != 200:
            raise
        try:
            return json.loads(req.text)
        except ValueError:
            raise

    def _get_request(self, path, params=None):
        req = requests.get(path, params=params)
        if req.status_code != 200:
            raise
        return req.text

    def _scrap_sceances(self):
        webpage = self._get_request(URLs.seance_url())
        soup = BeautifulSoup(webpage, 'html.parser')
        sections = soup.find_all('section')
        return sections

    def _scrap_cinemas(self, id_location, page=1):
        webpage = self._get_request(URLs.cinemas_url(id_location), params={"page": page})
        soup = BeautifulSoup(webpage, 'html.parser')
        cinemas = soup.select('*[class*="theater-card"]')
        buttons = soup.select('*[class*="button-right"]')
        next_page = None
        if len(buttons) and "button-disabled" not in buttons[-1]["class"]:
            next_page = page + 1
        return cinemas, next_page

    def _get_section(self, title):
        sections = self._scrap_sceances()
        for section in sections:
            h2 = section.find("h2")
            if h2 is None:
                continue
            title_text = h2.text
            if title_text == title:
                return section

    def get_top_villes(self):
        """
        Liste des id de villes
        :return:
        """
        section = self._get_section(allocineAPI.TOP_VILLE_TITLE)
        links = section.find_all("a")
        result = list()
        for link in links:
            ville_id = link['href'].split("/")[-2]
            result.append({"id": ville_id, "name": link["title"]})
        return result

    def get_departements(self):
        """
        Liste des id de départements
        :return:
        """
        section = self._get_section(allocineAPI.DEPARTEMENTS_TITLE)
        links = section.find_all("a")
        result = list()
        for link in links:
            departement_id = link['href'].split("/")[-2]
            result.append({"id": departement_id, "name": link["title"]})
        return result

    def get_circuit(self):
        """
        Liste des id de circuit
        :return:
        """
        section = self._get_section(allocineAPI.CIRCUIT_TITLE)
        links = section.find_all("a")
        result = list()
        for link in links:
            circuit_id = link['href'].split("/")[-2]
            circuit_name = link.find("span").text
            result.append({"id": circuit_id, "name": circuit_name})
        return result

    def get_cinema(self, id_location):
        """
        Récupération des id de cinema à partir des id de location
        :param id_location: id de ville, id de département ou id de circuit
        :return:
        """
        result = list()
        next_page = 1
        while next_page is not None:
            cinemas, next_page = self._scrap_cinemas(id_location, page=next_page)
            for cinema in cinemas:
                data = cinema.select('*[class*="add-theater-anchor"]')[0]
                cinema_data = json.loads(data["data-theater"])
                address = cinema.find("address").text
                result.append({
                    "id": cinema_data["id"],
                    "name": cinema_data["name"],
                    "address": address
                })

        return result

    def get_showtime(self, id_cinema, day_shift=0):
        """
        Récupération des horaires des seances pour un cinema, pour un jour donné
        :param id_cinema: id du cinema
        :param day_shift: décalage en jours par rapport à la date actuelle (positif)
        :return:
        """
        json_data = self._get_json_request(URLs.showtime_url(id_cinema, day_shift))
        formated_data = list()
        for movie in json_data["results"]:
            title = movie["movie"]["title"]
            duration = movie["movie"]["runtime"]
            list_vf = list()
            for showtime_original in movie["showtimes"]["original"]:
                list_vf.append(showtime_original["startsAt"])
            list_vo = list()
            for showtime_multiple in movie["showtimes"]["multiple"]:
                list_vo.append(showtime_multiple["startsAt"])
            formated_data.append({
                "title": title,
                "duration": duration,
                "VF": list_vf,
                "VO": list_vo
            })
        return formated_data


if __name__ == '__main__':

    api = allocineAPI()

    # ret = api.get_top_villes()
    # for elt in ret: print(elt)

    # ret = api.get_departements()
    # for elt in ret: print(elt)

    # ret = api.get_circuit()
    # for elt in ret: print(elt)

    # departement
    Ain = "departement-83191"
    # ville
    AixenProvence = "ville-87860"
    # circuit
    PatheCinemas = "circuit-81002"

    # cinemas = api.get_cinema(PatheCinemas)
    # for cinema in cinemas:
    #     print(cinema)

    data = api.get_showtime("W2920")
    for showtime in data:
        print(showtime)
