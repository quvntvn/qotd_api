import os
from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Citation(db.Model):
    __tablename__ = 'citations'
    id = db.Column(db.Integer, primary_key=True)
    auteur = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.Date, nullable=False)
    citation = db.Column(db.Text, nullable=False)

CORS(app)
api = Api(app)


def random_seed_based_on_date():
    today = datetime.now()
    seed = today.year + today.month + today.day
    return seed


class DailyQuote(Resource):
    def get(self):
        random.seed(random_seed_based_on_date())

        total_citations = Citation.query.count()

        if total_citations > 0:
            random_id = random.randint(1, total_citations)
            quote = Citation.query.get(random_id)

            if quote:
                quote_data = {
                    "id": quote.id,
                    "auteur": quote.auteur,
                    "date_creation": quote.date_creation.strftime('%Y-%m-%d'),
                    "citation": quote.citation
                }
            else:
                quote_data = {"error": "Citation not found"}
        else:
            quote_data = {"error": "No citations in the database"}

        return jsonify(quote_data)


api.add_resource(DailyQuote, '/api/daily_quote')


class AllQuotes(Resource):
    def get(self):
        quotes = Citation.query.all()

        quotes_data = []
        for quote in quotes:
            quote_data = {
                "id": quote.id,
                "auteur": quote.auteur,
                "citation": quote.citation,
                "date_creation": quote.date_creation.strftime('%Y-%m-%d')
            }
            quotes_data.append(quote_data)

        return jsonify(quotes_data)



api.add_resource(AllQuotes, "/api/quotes")


@app.route('/swagger/<path:path>')
def send_swagger(path):
    return send_from_directory('swagger', path)


@app.route('/openapi.yaml')
def send_openapi():
    return send_from_directory('.', 'openapi.yaml')


class RandomQuote(Resource):
    def get(self):
        total_citations = Citation.query.count()

        if total_citations > 0:
            random_id = random.randint(1, total_citations)
            quote = Citation.query.get(random_id)

            if quote:
                quote_data = {
                    "id": quote.id,
                    "auteur": quote.auteur,
                    "date_creation": quote.date_creation.strftime('%Y-%m-%d'),
                    "citation": quote.citation
                }
            else:
                quote_data = {"error": "Citation not found"}
        else:
            quote_data = {"error": "No citations in the database"}

        return jsonify(quote_data)


api.add_resource(RandomQuote, '/api/random_quote')

# class DeleteQuote(Resource):
#    def delete(self, quote_id):
#        conn = psycopg2.connect(
#            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
#        cur = conn.cursor()

#        cur.execute("DELETE FROM citations WHERE id=%s;", (quote_id,))
#        deleted_rows = cur.rowcount

#        conn.commit()
#        cur.close()
#        conn.close()

#        if deleted_rows > 0:
#            return jsonify({"status": "success", "message": f"Citation with ID {quote_id} deleted"})
#        else:
#            return jsonify({"status": "error", "message": f"Citation with ID {quote_id} not found"})


# api.add_resource(DeleteQuote, '/api/delete_quote/<int:quote_id>')


# class AddQuote(Resource):
#    def post(self):
#        data = request.get_json()

#        auteur = data.get('auteur')
#        date_creation = data.get('date_creation')
#        citation = data.get('citation')

#        conn = psycopg2.connect(
#            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
#        cur = conn.cursor()

#        cur.execute("INSERT INTO citations (auteur, date_creation, citation) VALUES (%s, %s, %s);",
#                    (auteur, date_creation, citation))
#        conn.commit()

#        cur.close()
#        conn.close()

#        return jsonify({"status": "success", "message": "Citation added"})


# api.add_resource(AddQuote, '/api/add_quote')


class QuoteByID(Resource):
    def get(self, quote_id):
        quote = Citation.query.get(quote_id)

        if quote is None:
            return {"error": "Quote not found"}, 404

        return {
            "id": quote.id,
            "auteur": quote.auteur,
            "citation": quote.citation,
            "date_creation": quote.date_creation.strftime('%Y-%m-%d')
        }



api.add_resource(QuoteByID, "/api/quote/<int:quote_id>")


# class UpdateQuote(Resource):
#    def put(self, quote_id):
#        data = request.get_json()

#       auteur = data.get('auteur')
#       date_creation = data.get('date_creation')
#       citation = data.get('citation')

#        conn = psycopg2.connect(
#            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
#        cur = conn.cursor()

#        cur.execute("UPDATE citations SET auteur=%s, date_creation=%s, citation=%s WHERE id=%s;",
#                    (auteur, date_creation, citation, quote_id))
#        updated_rows = cur.rowcount
#        conn.commit()

#        cur.close()
#        conn.close()

#        if updated_rows > 0:
#            return jsonify({"status": "success", "message": f"Citation with ID {quote_id} updated"})
#        else:
#            return jsonify({"status": "error", "message": f"Citation with ID {quote_id} not found"})


# api.add_resource(UpdateQuote, '/api/update_quote/<int:quote_id>')

if __name__ == '__main__':
    app.run(debug=True)
