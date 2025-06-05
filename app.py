import os
from datetime import datetime, date
from flask import Flask, jsonify, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"].strip()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- DB --------------------------------------------------------------------

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Citation(db.Model):
    """Table `citations`
    id              : SERIAL / Primary key
    auteur          : TEXT not null
    date_creation   : DATE (nullable)
    citation        : TEXT not null
    """

    __tablename__ = "citations"

    id = db.Column(db.Integer, primary_key=True)
    auteur = db.Column(db.Text, nullable=False)
    # Nullable pour accepter les dates inconnues
    date_creation = db.Column(db.Date, nullable=True)
    citation = db.Column(db.Text, nullable=False)


# --- Flask‑RESTful ----------------------------------------------------------

CORS(app)
api = Api(app)


def _quote_for_day(target_date: date | None = None):
    """Retourne la citation associée au *jour de l'année* (1‑365).

    · Si l'année est bissextile (366 jours) et qu'il n'y a que 365 citations,
      le 29 février reprend la citation du 1ᵉʳ mars (index modulo).

    · Si la table contient moins de 365 entrées, on boucle avec modulo.
      Si elle en contient plus, seules les 365 premières seront utilisées.
    """

    if target_date is None:
        target_date = datetime.utcnow().date()

    day_of_year = target_date.timetuple().tm_yday  # 1‑366
    total = Citation.query.count()

    if total == 0:
        return None

    # Transforme en index 0‑(total‑1)
    index = (day_of_year - 1) % total

    # Récupère la citation par décalage plutôt que par id aléatoire pour être
    # insensible aux « trous » éventuels dans les IDs (p. ex. après suppressions)
    return (
        Citation.query.order_by(Citation.id)
        .offset(index)
        .limit(1)
        .first()
    )


class DailyQuote(Resource):
    """Citation du jour – déterministe par jour de l'année."""

    def get(self):
        quote = _quote_for_day()

        if quote is None:
            return jsonify({"error": "No citations in the database"})

        return jsonify({
            "id": quote.id,
            "auteur": quote.auteur,
            "date_creation": quote.date_creation.isoformat() if quote.date_creation else None,
            "citation": quote.citation,
        })


api.add_resource(DailyQuote, "/api/daily_quote")


class AllQuotes(Resource):
    def get(self):
        quotes = Citation.query.order_by(Citation.id).all()
        return jsonify([
            {
                "id": q.id,
                "auteur": q.auteur,
                "citation": q.citation,
                "date_creation": q.date_creation.isoformat() if q.date_creation else None,
            }
            for q in quotes
        ])


api.add_resource(AllQuotes, "/api/quotes")


class RandomQuote(Resource):
    """Reste inchangé : citation aléatoire parmi toutes."""

    def get(self):
        total = Citation.query.count()
        if total == 0:
            return jsonify({"error": "No citations in the database"})

        # Choix aléatoire sécurisé via offset pour éviter le biais lié aux IDs
        from random import randint

        offset = randint(0, total - 1)
        quote = Citation.query.offset(offset).limit(1).first()

        return jsonify({
            "id": quote.id,
            "auteur": quote.auteur,
            "date_creation": quote.date_creation.isoformat() if quote.date_creation else None,
            "citation": quote.citation,
        })


api.add_resource(RandomQuote, "/api/random_quote")


class QuoteByID(Resource):
    def get(self, quote_id: int):
        quote = Citation.query.get(quote_id)
        if quote is None:
            return {"error": "Quote not found"}, 404
        return {
            "id": quote.id,
            "auteur": quote.auteur,
            "citation": quote.citation,
            "date_creation": quote.date_creation.isoformat() if quote.date_creation else None,
        }


api.add_resource(QuoteByID, "/api/quote/<int:quote_id>")


# --- Static files (Swagger / OpenAPI) --------------------------------------

@app.route("/swagger/<path:path>")
def send_swagger(path):
    return send_from_directory("swagger", path)


@app.route("/openapi.yaml")
def send_openapi():
    return send_from_directory(".", "openapi.yaml")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
