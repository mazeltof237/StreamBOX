"""Seed StreamBOX avec un catalogue de films & séries cultes (posters TMDB)."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import Profile, Plan, Subscription
from catalog.models import Genre, Title, Episode

User = get_user_model()

GENRES = ["Drame", "Comédie", "Documentaire", "Thriller", "Horreur", "Action",
          "Science-fiction", "Romance", "Animation", "Aventure", "Crime",
          "Fantastique", "Mystère", "Biographie", "Guerre"]

# Échantillons vidéo publics (Google sample bucket — toujours disponibles)
SAMPLES = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
]

TMDB_POSTER = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP = "https://image.tmdb.org/t/p/original"

# (titre, kind, year, durée, maturité, rating, featured, trending,
#  genres, description, poster_path, backdrop_path, cast, director, trailer)
TITLES = [
    # ===== FILMS CULTES =====
    ("Inception", "movie", 2010, 148, "13", 8.4, True, True,
     ["Action", "Science-fiction", "Thriller"],
     "Dom Cobb, voleur expérimenté dans l'art périlleux de l'extraction, doit accomplir l'inverse : implanter une idée dans l'esprit d'un PDG. Pour réussir l'impossible, il s'enfonce avec son équipe dans des rêves enchâssés.",
     "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
     "Leonardo DiCaprio, Joseph Gordon-Levitt, Marion Cotillard, Tom Hardy", "Christopher Nolan",
     "https://www.youtube.com/embed/YoHD9XEInc0"),

    ("Interstellar", "movie", 2014, 169, "13", 8.7, True, True,
     ["Science-fiction", "Aventure", "Drame"],
     "Dans un futur où la Terre meurt, un ancien pilote de la NASA et son équipe traversent un trou de ver près de Saturne pour trouver une nouvelle planète habitable. Un voyage où l'amour défie l'espace-temps.",
     "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "/pbrkL804c8yAv3zBZR4QPWZAAn8.jpg",
     "Matthew McConaughey, Anne Hathaway, Jessica Chastain", "Christopher Nolan",
     "https://www.youtube.com/embed/zSWdZVtXT7E"),

    ("The Dark Knight", "movie", 2008, 152, "13", 9.0, False, True,
     ["Action", "Crime", "Drame"],
     "Batman, Gordon et Harvey Dent unissent leurs forces contre la pègre de Gotham. Mais un nouveau criminel, le Joker, plonge la ville dans le chaos et met à l'épreuve l'âme du Chevalier Noir.",
     "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "/hqkIcbrOHL86UncnHIsHVcVmzue.jpg",
     "Christian Bale, Heath Ledger, Aaron Eckhart", "Christopher Nolan",
     "https://www.youtube.com/embed/EXeTwQWrcwY"),

    ("Pulp Fiction", "movie", 1994, 154, "16", 8.9, False, False,
     ["Crime", "Drame", "Thriller"],
     "Les destins entrecroisés de deux tueurs à gages, d'un boxeur, d'un gangster et de sa femme se télescopent dans le Los Angeles des années 90, dans une fresque chorale devenue culte.",
     "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
     "John Travolta, Uma Thurman, Samuel L. Jackson", "Quentin Tarantino",
     "https://www.youtube.com/embed/s7EdQ4FqbhY"),

    ("Le Parrain", "movie", 1972, 175, "16", 9.2, False, False,
     ["Crime", "Drame"],
     "1945, New York. À la tête d'un empire mafieux, Don Vito Corleone refuse de tremper dans le trafic de drogue. Son fils Michael, héros de guerre, est aspiré dans la guerre des familles qui s'ensuit.",
     "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
     "Marlon Brando, Al Pacino, James Caan", "Francis Ford Coppola",
     "https://www.youtube.com/embed/sY1S34973zA"),

    ("The Matrix", "movie", 1999, 136, "13", 8.7, False, True,
     ["Action", "Science-fiction"],
     "Neo, jeune hacker, découvre que la réalité n'est qu'une simulation gérée par des machines. Recruté par Morpheus et Trinity, il devient l'élu d'une humanité asservie.",
     "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
     "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss", "Wachowski",
     "https://www.youtube.com/embed/m8e-FF8MsqU"),

    ("Forrest Gump", "movie", 1994, 142, "13", 8.8, False, False,
     ["Drame", "Romance", "Comédie"],
     "Doté d'un QI faible mais d'un cœur immense, Forrest Gump traverse trois décennies d'histoire américaine — de la guerre du Vietnam à la création d'Apple — sans jamais cesser d'aimer Jenny.",
     "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "/mMtUybQ6hL24FXo0F3Z4j2KG7kZ.jpg",
     "Tom Hanks, Robin Wright, Gary Sinise", "Robert Zemeckis",
     "https://www.youtube.com/embed/bLvqoHBptjg"),

    ("Fight Club", "movie", 1999, 139, "18", 8.8, False, False,
     ["Drame", "Thriller"],
     "Un employé de bureau insomniaque rencontre Tyler Durden, charismatique vendeur de savon. Ensemble, ils fondent un club de combat clandestin qui devient un mouvement anarchiste mondial.",
     "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", "/rr7E0NoGKxvbkb89eR1GwfoYjpA.jpg",
     "Brad Pitt, Edward Norton, Helena Bonham Carter", "David Fincher",
     "https://www.youtube.com/embed/qtRKdVHc-cE"),

    ("Joker", "movie", 2019, 122, "16", 8.4, False, True,
     ["Crime", "Drame", "Thriller"],
     "Arthur Fleck, comédien raté de Gotham, sombre lentement dans la folie face à une société indifférente. Sa transformation en Joker enflamme la ville.",
     "/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg", "/n6bUvigpRFqSwmPp1m2YADdbRBc.jpg",
     "Joaquin Phoenix, Robert De Niro, Zazie Beetz", "Todd Phillips",
     "https://www.youtube.com/embed/zAGVQLHvwOY"),

    ("Parasite", "movie", 2019, 132, "16", 8.5, False, True,
     ["Drame", "Thriller", "Comédie"],
     "La famille Ki-taek, sans emploi, s'introduit progressivement comme personnel dans la villa des Park, riches industriels. Une cohabitation parasitaire qui bascule dans l'horreur.",
     "/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg",
     "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong", "Bong Joon-ho",
     "https://www.youtube.com/embed/5xH0HfJHsaY"),

    ("Avengers : Endgame", "movie", 2019, 181, "13", 8.4, False, True,
     ["Action", "Aventure", "Science-fiction"],
     "Après Thanos, l'univers est en deuil. Les Avengers survivants tentent l'impossible voyage à travers le temps pour ramener ceux qu'ils ont perdus.",
     "/or06FN3Dka5tukK1e9sl16pB3iy.jpg", "/orjiB3oUIsyz60hoEqkiGpy5CeO.jpg",
     "Robert Downey Jr., Chris Evans, Scarlett Johansson", "Anthony & Joe Russo",
     "https://www.youtube.com/embed/TcMBFSGVi1c"),

    ("Avatar", "movie", 2009, 162, "13", 7.9, False, False,
     ["Science-fiction", "Aventure", "Action"],
     "Sur Pandora, le marine Jake Sully découvre les Na'vi à travers son avatar et tombe amoureux de Neytiri. Bientôt, il devra choisir son camp.",
     "/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg", "/Yc9q6QuWrMp9nuDm5R8ExNqbEq.jpg",
     "Sam Worthington, Zoe Saldana, Sigourney Weaver", "James Cameron",
     "https://www.youtube.com/embed/5PSNL1qE6VY"),

    ("Le Seigneur des Anneaux : La Communauté de l'Anneau", "movie", 2001, 178, "13", 8.9, False, False,
     ["Fantastique", "Aventure", "Drame"],
     "Le hobbit Frodon hérite d'un anneau de pouvoir maléfique. Avec une communauté de huit compagnons, il entame le périlleux voyage vers la Montagne du Destin pour le détruire.",
     "/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg", "/x2RS3uTcsJJ9IfjNPcgDmukoEcQ.jpg",
     "Elijah Wood, Ian McKellen, Viggo Mortensen", "Peter Jackson",
     "https://www.youtube.com/embed/V75dMMIW2B4"),

    ("Spider-Man : New Generation", "movie", 2018, 117, "ALL", 8.4, False, False,
     ["Animation", "Action", "Aventure"],
     "L'adolescent Miles Morales devient Spider-Man de son univers — et rencontre cinq autres versions de l'Araignée venues d'autres dimensions.",
     "/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg", "/uUiId6cG32JSRI6RyBQSvQtLjz2.jpg",
     "Shameik Moore, Jake Johnson, Hailee Steinfeld", "Persichetti, Ramsey, Rothman",
     "https://www.youtube.com/embed/g4Hbz2jLxvQ"),

    ("Le Voyage de Chihiro", "movie", 2001, 125, "ALL", 8.6, False, False,
     ["Animation", "Fantastique", "Aventure"],
     "Chihiro, 10 ans, se retrouve piégée dans un monde peuplé d'esprits où ses parents ont été transformés en cochons. Elle doit travailler aux bains pour les sauver.",
     "/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg", "/Ab8mkHmkYADjU7wQiOkia9BzGvS.jpg",
     "Rumi Hiiragi, Miyu Irino, Mari Natsuki", "Hayao Miyazaki",
     "https://www.youtube.com/embed/ByXuk9QqQkk"),

    ("La La Land", "movie", 2016, 128, "ALL", 8.0, False, False,
     ["Romance", "Drame", "Comédie"],
     "À Los Angeles, Mia, comédienne en herbe, et Sebastian, pianiste de jazz, tombent amoureux. Mais leurs rêves vont mettre leur histoire à l'épreuve.",
     "/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg", "/fp6X6yhgcxzxCpmM0EVC6V9B6lR.jpg",
     "Ryan Gosling, Emma Stone, John Legend", "Damien Chazelle",
     "https://www.youtube.com/embed/0pdqf4P9MB8"),

    ("Dune", "movie", 2021, 155, "13", 8.0, False, True,
     ["Science-fiction", "Aventure"],
     "Paul Atréides, héritier d'une noble famille, doit voyager vers Arrakis, la planète la plus dangereuse de l'univers, pour assurer l'avenir de son peuple.",
     "/d5NXSklXo0qyIYkgV94XAgMIckC.jpg", "/jYEW5xZkZk2WTrdbMGAPFuBqbDc.jpg",
     "Timothée Chalamet, Rebecca Ferguson, Zendaya", "Denis Villeneuve",
     "https://www.youtube.com/embed/8g18jFHCLXk"),

    ("Oppenheimer", "movie", 2023, 180, "16", 8.3, False, True,
     ["Biographie", "Drame", "Guerre"],
     "L'histoire du physicien J. Robert Oppenheimer et de son rôle dans le développement de la bombe atomique pendant la Seconde Guerre mondiale.",
     "/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg", "/fm6KqXpk3M2HVveHwCrBSSBaO0V.jpg",
     "Cillian Murphy, Emily Blunt, Matt Damon", "Christopher Nolan",
     "https://www.youtube.com/embed/uYPbbksJxIg"),

    # ===== SÉRIES CULTES =====
    ("Breaking Bad", "series", 2008, 0, "16", 9.5, True, True,
     ["Crime", "Drame", "Thriller"],
     "Walter White, professeur de chimie atteint d'un cancer, s'associe à un ancien élève pour fabriquer la meilleure méthamphétamine du Nouveau-Mexique. Sa descente aux enfers fait de lui une légende.",
     "/ggFHVNu6YYI5L9pCfOacjizRGt.jpg", "/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
     "Bryan Cranston, Aaron Paul, Anna Gunn", "Vince Gilligan",
     "https://www.youtube.com/embed/HhesaQXLuRY"),

    ("Stranger Things", "series", 2016, 0, "13", 8.6, False, True,
     ["Science-fiction", "Drame", "Mystère"],
     "À Hawkins, Indiana, la disparition d'un garçon révèle une fillette aux pouvoirs surnaturels et un monde parallèle peuplé de créatures cauchemardesques.",
     "/49WJfeN0moxb9IPfGn8AIqMGskD.jpg", "/56v2KjBlU4XaOv9rVYEQypROD7P.jpg",
     "Millie Bobby Brown, Finn Wolfhard, Winona Ryder", "Duffer Brothers",
     "https://www.youtube.com/embed/b9EkMc79ZSU"),

    ("Game of Thrones", "series", 2011, 0, "18", 9.2, False, False,
     ["Fantastique", "Drame", "Aventure"],
     "Sept familles nobles s'affrontent pour le contrôle du Trône de Fer de Westeros, pendant qu'un ennemi ancien revient menacer l'humanité depuis le Nord.",
     "/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg", "/suopoADq0k8YZr4dQXcU6pToj6s.jpg",
     "Emilia Clarke, Peter Dinklage, Kit Harington", "David Benioff & D. B. Weiss",
     "https://www.youtube.com/embed/KPLWWIOCOOQ"),

    ("La Casa de Papel", "series", 2017, 0, "16", 8.2, False, True,
     ["Crime", "Drame", "Thriller"],
     "Un mystérieux Professeur recrute une équipe de huit braqueurs pour réaliser le plus grand braquage de l'histoire : imprimer 2,4 milliards d'euros à la Maison de la Monnaie d'Espagne.",
     "/reEMJA1uzscCbkpeRJeTT2bjqUp.jpg", "/gFZriCkpJYsApPZEF3jhxL4yLzG.jpg",
     "Úrsula Corberó, Álvaro Morte, Itziar Ituño", "Álex Pina",
     "https://www.youtube.com/embed/_InqQJRqGW4"),

    ("Squid Game", "series", 2021, 0, "16", 8.0, False, True,
     ["Drame", "Thriller", "Mystère"],
     "Des centaines de joueurs criblés de dettes acceptent une étrange invitation à participer à des jeux d'enfants. La récompense est colossale, mais l'enjeu est mortel.",
     "/dDlEmu3EZ0Pgg93K2SVNLCjCSvE.jpg", "/2meX1nMdScFOoV4370rqHWKmXhY.jpg",
     "Lee Jung-jae, Park Hae-soo, HoYeon Jung", "Hwang Dong-hyuk",
     "https://www.youtube.com/embed/oqxAJKy0ii4"),

    ("The Witcher", "series", 2019, 0, "16", 8.0, False, False,
     ["Fantastique", "Action", "Aventure"],
     "Geralt de Riv, sorceleur mutant chasseur de monstres, lie son destin à celui d'une jeune princesse cachant un terrible secret sur le Continent.",
     "/cZ0d3rtvXPVvuiX22sP79K3Hmjz.jpg", "/7HtvmsLrPpEnaSStvgwKVxlEMQz.jpg",
     "Henry Cavill, Anya Chalotra, Freya Allan", "Lauren Schmidt Hissrich",
     "https://www.youtube.com/embed/ndl1W4ltcmg"),

    ("Peaky Blinders", "series", 2013, 0, "16", 8.8, False, False,
     ["Crime", "Drame"],
     "Birmingham, 1919. Tommy Shelby et son gang de gitans, les Peaky Blinders, étendent leur empire criminel à travers l'Angleterre d'après-guerre.",
     "/vUUqzWa2LnHIVqkaKVlVGkVcZIW.jpg", "/wiE9doxiLwq3WCGamDIOb2PqBqc.jpg",
     "Cillian Murphy, Helen McCrory, Paul Anderson", "Steven Knight",
     "https://www.youtube.com/embed/oVzVdvGIC7U"),

    ("The Crown", "series", 2016, 0, "13", 8.7, False, False,
     ["Drame", "Biographie"],
     "Le règne d'Élisabeth II, de son mariage en 1947 à nos jours, vu à travers les coulisses du pouvoir, les intrigues politiques et la vie privée de la famille royale.",
     "/1M876KPjulVwppEpldhdc8V4o68.jpg", "/dHv5BSPLqQbm3Th9OqlsHmgUVca.jpg",
     "Claire Foy, Olivia Colman, Imelda Staunton", "Peter Morgan",
     "https://www.youtube.com/embed/JWtnJjn6ng0"),
]

PLANS = [
    ("essential", "Essentiel", 7.99, "SD", 1, 1,
     "Idéal pour démarrer. Un écran à la fois, qualité SD."),
    ("standard", "Standard", 13.99, "Full HD", 2, 2,
     "HD jusqu'à 1080p, 2 écrans simultanés, 2 profils."),
    ("premium", "Premium", 19.99, "4K + HDR",  5, 4,
     "4K Ultra HD + HDR, 5 profils, 4 écrans simultanés, son spatial."),
]


class Command(BaseCommand):
    help = "Initialise StreamBOX : genres, plans, films cultes, séries, comptes démo."

    def handle(self, *args, **opts):
        # ----- Genres -----
        for g in GENRES:
            Genre.objects.get_or_create(name=g)
        self.stdout.write(self.style.SUCCESS(f"✔ {Genre.objects.count()} genres."))

        # ----- Plans -----
        for code, name, price, q, mp, ss, desc in PLANS:
            Plan.objects.update_or_create(code=code, defaults=dict(
                name=name, price_eur=price, quality=q, max_profiles=mp,
                simultaneous_streams=ss, description=desc, is_active=True))
        self.stdout.write(self.style.SUCCESS(f"✔ {Plan.objects.count()} plans."))

        # ----- Titres -----
        for i, row in enumerate(TITLES):
            (name, kind, year, dur, mat, rating, feat, trend,
             genres, desc, poster, backdrop, cast, director, trailer) = row
            video = SAMPLES[i % len(SAMPLES)]
            t, _ = Title.objects.update_or_create(
                title=name,
                defaults=dict(
                    kind=kind, year=year, duration_minutes=dur, maturity=mat,
                    rating=rating, is_featured=feat, is_trending=trend,
                    description=desc,
                    poster_url=f"{TMDB_POSTER}{poster}",
                    backdrop_url=f"{TMDB_BACKDROP}{backdrop}",
                    video_url=video,
                    trailer_url=trailer,
                    cast=cast,
                    director=director,
                ),
            )
            t.genres.set(Genre.objects.filter(name__in=genres))
            if kind == "series":
                for s in (1, 2):
                    for ep in range(1, 5):
                        Episode.objects.update_or_create(
                            title=t, season=s, number=ep,
                            defaults=dict(
                                name=f"Épisode {ep}",
                                description="Un épisode haletant qui fait avancer l'intrigue.",
                                duration_minutes=52, video_url=video,
                                thumbnail_url=f"{TMDB_BACKDROP}{backdrop}",
                            ),
                        )
        self.stdout.write(self.style.SUCCESS(f"✔ {Title.objects.count()} titres (films & séries cultes)."))

        # ----- Comptes démo -----
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@streambox.tv", "admin12345")
        demo, created = User.objects.get_or_create(username="demo", defaults={"email": "demo@streambox.tv"})
        if created:
            demo.set_password("demo12345"); demo.save()
        if not demo.profiles.exists():
            Profile.objects.create(user=demo, name="Daniel", avatar_preset="fafi")
            Profile.objects.create(user=demo, name="Kids", avatar_preset="kids", is_kid=True)
        prem = Plan.objects.get(code="premium")
        Subscription.objects.update_or_create(user=demo, defaults=dict(
            plan=prem, status="active",
            started_at=timezone.now(),
            renews_at=timezone.now() + timedelta(days=30),
        ))
        self.stdout.write(self.style.SUCCESS("✔ Comptes : admin/admin12345 · demo/demo12345 (Premium)"))
        self.stdout.write(self.style.SUCCESS("🎬 StreamBOX est prêt. Lance : python manage.py runserver"))
