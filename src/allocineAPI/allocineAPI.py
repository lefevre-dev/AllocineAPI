import json
import requests
from bs4 import BeautifulSoup


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

    def get_showtime(self, id_cinema, date_str: str, verbose_url=False):
        """
        Récupération des horaires des seances pour un cinema, pour un jour donné
        :param date_str: date
        :param verbose_url: url de la requête scrapter
        :param id_cinema: id du cinema
        :return:
        """
        formated_data = list()
        page, totalPages = 0, 1
        while page < totalPages:
            if verbose_url:
                print(URLs.showtime_url(id_cinema, date_str, page + 1))
            json_data = self._get_json_request(URLs.showtime_url(id_cinema, date_str, page + 1))
            page = int(json_data["pagination"]["page"])
            totalPages = int(json_data["pagination"]["totalPages"])
            for element in json_data["results"]:
                title = element["movie"]["title"]
                showtimes = list()
                lst_internal_ids = list()
                for showtimes_key in element["showtimes"].keys():
                    for showtime in element["showtimes"][showtimes_key]:
                        if showtime["internalId"] not in lst_internal_ids:
                            lst_internal_ids.append(showtime["internalId"])
                            showtimes.append({
                                "startsAt": showtime["startsAt"],
                                "diffusionVersion": showtime["diffusionVersion"],
                            })

                formated_data.append({
                    "title": title,
                    "showtimes": showtimes
                })

        return formated_data

    def get_movies(self, id_cinema, date_str: str, verbose_url=False):
        """
        Récupération des films pour des cinemas et des jours
        :param date_str: date
        :param verbose_url: url de la requête scrapter
        :param id_cinema: id des cinema
        :return:
        """
        formated_data = list()
        lst_internal_ids = list()
        page, totalPages = 0, 1
        while page < totalPages:
            if verbose_url:
                print(URLs.showtime_url(id_cinema, date_str, page + 1))
            json_data = self._get_json_request(URLs.showtime_url(id_cinema, date_str, page + 1))
            page = int(json_data["pagination"]["page"])
            totalPages = int(json_data["pagination"]["totalPages"])

            for element in json_data["results"]:
                internal_id = element["movie"]["internalId"]
                if internal_id not in lst_internal_ids:
                    lst_internal_ids.append(internal_id)

                    title = element["movie"].get("title")
                    if title is None:
                        title = "Unknown Title"

                    original_title = element["movie"].get("originalTitle")
                    if original_title is None:
                        original_title = "Unknown Original Title"

                    director = ""
                    try:
                        for credit in element["movie"]["credits"]:
                            if credit["position"].get("name") == "DIRECTOR":
                                if director != "":
                                    director += " | "
                                director += credit["person"].get("firstName") + " " + credit["person"].get("lastName")
                    except:
                        director = "Error"

                    if director == "":
                        director = "Unknown Director"

                    synopsis_full = element["movie"].get("synopsisFull")
                    if synopsis_full is None:
                        synopsis_full = "No Synopsis Available"

                    if element["movie"]["poster"] is None:
                        url_poster = "No Poster URL Available"
                    else:
                        url_poster = element["movie"]["poster"].get("url")
                        if url_poster is None:
                            url_poster = "No Poster URL Available"

                    releases = element["movie"]["releases"]
                    result_release = list()
                    for release in releases:
                        name = release.get("name")
                        releaseDate = release.get("releaseDate")
                        if releaseDate is not None:
                            releaseDate = release.get("releaseDate").get("date")
                        result_release.append({'releaseName': name, 'releaseDate': releaseDate})

                    if releaseDate is None:
                        releaseDate = "No Release Date Available"

                    runtime = element["movie"].get("runtime", 0)
                    languages = element["movie"].get("languages", [])  # Return empty list if None
                    has_dvd_release = element["movie"]["flags"].get("hasDvdRelease", False)

                    custom_flags = element["movie"].get("customFlags", False)
                    is_premiere, weekly_outing = False, False
                    if custom_flags:
                        is_premiere = element["movie"]["customFlags"].get("isPremiere", False)
                        weekly_outing = element["movie"]["customFlags"].get("weeklyOuting", False)

                    formated_data.append({
                        "title": title,
                        "originalTitle": original_title,
                        "director": director,
                        "synopsisFull": synopsis_full,
                        "urlPoster": url_poster,
                        "releases": result_release,
                        "runtime": runtime,
                        "languages": languages,
                        "hasDvdRelease": has_dvd_release,
                        "isPremiere": is_premiere,
                        "weeklyOuting": weekly_outing
                    })
        return formated_data


class URLs:
    BASE_URL = "https://www.allocine.fr/"
    SEANCES = "salle/"
    CINEMA = "cinema/"
    SHOWTIMES = "_/showtimes/theater-"

    @staticmethod
    def seance_url():
        return URLs.BASE_URL + URLs.SEANCES

    @staticmethod
    def cinemas_url(id_location):
        if "circuit" in id_location:
            return URLs.BASE_URL + URLs.SEANCES + id_location
        else:
            return URLs.BASE_URL + URLs.SEANCES + URLs.CINEMA + id_location

    @staticmethod
    def showtime_url(id_cinema, date_str: str, page):
        return URLs.BASE_URL + URLs.SHOWTIMES + id_cinema + "/d-" + str(date_str) + "/p-" + str(page)


if __name__ == '__main__':
    api = allocineAPI()
    data = api.get_showtime("P1699", "2025-01-23")
    print(data)

    films = api.get_movies('P0671',"2025-01-23", verbose_url=True)  # Film cité international aujourd'hui
    for film in films:
        print(film)

    print("\n")

    films = api.get_movies('P0671', "2025-01-23")  # Film cité international demain
    for film in films:
        print(film)

    print("\n")

    showtimes = api.get_showtime('P0671', "2025-01-23")  # showtimes cité international aujourd'hui
    for showtime in showtimes:
        print(showtime)

    print("\n")

    showtimes = api.get_showtime('P0671', "2025-01-23")  # showtimes cité international demain
    for showtime in showtimes:
        print(showtime)

    showtimes = api.get_movies('P0036', "2025-01-23", verbose_url=True)  # showtimes cité international demain
    for showtime in showtimes:
        print(showtime)

    ret = api.get_top_villes()
    for elt in ret:
       print(elt)
    ret = api.get_departements()
    for elt in ret:
       print(elt)

    ret = api.get_circuit()
    for elt in ret:
       print(elt)

    # departement
    Ain = "departement-83191"
    # ville
    AixenProvence = "ville-87860"
    # circuit
    PatheCinemas = "circuit-81002"

    # cinemas = api.get_cinema(PatheCinemas)
    # for cinema in cinemas:
    #     print(cinema)

    data = api.get_showtime("P0036", "2025-01-23")

    print(len(data))
