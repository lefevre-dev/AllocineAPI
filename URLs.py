
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
    def showtime_url(id_cinema, day_shift):
        return URLs.BASE_URL + URLs.SHOWTIMES + id_cinema + "/d-" + str(day_shift)

