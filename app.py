from flask_restful import Resource
from flask import jsonify
from datetime import datetime
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask import send_from_directory
import psycopg2
import random

app = Flask(__name__)
api = Api(app)


def random_seed_based_on_date():
    today = datetime.now()
    seed = today.year + today.month + today.day
    return seed


class DailyQuote(Resource):
    def get(self):
        random.seed(random_seed_based_on_date())

        conn = psycopg2.connect(
            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM citations;")
        total_citations = cur.fetchone()[0]

        if total_citations > 0:
            random_id = random.randint(1, total_citations)
            cur.execute("SELECT * FROM citations WHERE id=%s;", (random_id,))
            quote = cur.fetchone()

            if quote:
                quote_data = {
                    "id": quote[0],
                    "auteur": quote[1],
                    "date_creation": str(quote[2]),
                    "citation": quote[3]
                }
            else:
                quote_data = {"error": "Citation not found"}
        else:
            quote_data = {"error": "No citations in the database"}

        cur.close()
        conn.close()

        return jsonify(quote_data)


api.add_resource(DailyQuote, '/api/daily_quote')


@app.route('/swagger/<path:path>')
def send_swagger(path):
    return send_from_directory('swagger', path)


@app.route('/openapi.yaml')
def send_openapi():
    return send_from_directory('.', 'openapi.yaml')


class RandomQuote(Resource):
    def get(self):
        conn = psycopg2.connect(
            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM citations;")
        total_citations = cur.fetchone()[0]

        if total_citations > 0:
            random_id = random.randint(1, total_citations)
            cur.execute("SELECT * FROM citations WHERE id=%s;", (random_id,))
            quote = cur.fetchone()

            if quote:
                quote_data = {
                    "id": quote[0],
                    "auteur": quote[1],
                    "date_creation": str(quote[2]),
                    "citation": quote[3]
                }
            else:
                quote_data = {"error": "Citation not found"}
        else:
            quote_data = {"error": "No citations in the database"}

        cur.close()
        conn.close()

        return jsonify(quote_data)


api.add_resource(RandomQuote, '/api/random_quote')


class DeleteQuote(Resource):
    def delete(self, quote_id):
        conn = psycopg2.connect(
            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
        cur = conn.cursor()

        cur.execute("DELETE FROM citations WHERE id=%s;", (quote_id,))
        deleted_rows = cur.rowcount

        conn.commit()
        cur.close()
        conn.close()

        if deleted_rows > 0:
            return jsonify({"status": "success", "message": f"Citation with ID {quote_id} deleted"})
        else:
            return jsonify({"status": "error", "message": f"Citation with ID {quote_id} not found"})


api.add_resource(DeleteQuote, '/api/delete_quote/<int:quote_id>')


class AddQuote(Resource):
    def post(self):
        data = request.get_json()

        auteur = data.get('auteur')
        date_creation = data.get('date_creation')
        citation = data.get('citation')

        conn = psycopg2.connect(
            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
        cur = conn.cursor()

        cur.execute("INSERT INTO citations (auteur, date_creation, citation) VALUES (%s, %s, %s);",
                    (auteur, date_creation, citation))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"status": "success", "message": "Citation added"})


api.add_resource(AddQuote, '/api/add_quote')


class QuoteByID(Resource):
    def get(self, quote_id):
        conn = psycopg2.connect(
            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
        cur = conn.cursor()

        cur.execute(
            "SELECT id, auteur, citation, date_creation FROM citations WHERE id=%s", (quote_id,))
        quote = cur.fetchone()

        if quote is None:
            return {"error": "Quote not found"}, 404

        cur.close()
        conn.close()

        return {
            "id": quote[0],
            "auteur": quote[1],
            "citation": quote[2],
            "date_creation": quote[3].strftime('%Y-%m-%d')
        }


api.add_resource(QuoteByID, "/api/quote/<int:quote_id>")


class UpdateQuote(Resource):
    def put(self, quote_id):
        data = request.get_json()

        auteur = data.get('auteur')
        date_creation = data.get('date_creation')
        citation = data.get('citation')

        conn = psycopg2.connect(
            "dbname=vidlhusi user=vidlhusi password=u3aP566U2_RYk8GtBufXTz3Na3867Do4 host=lucky.db.elephantsql.com")
        cur = conn.cursor()

        cur.execute("UPDATE citations SET auteur=%s, date_creation=%s, citation=%s WHERE id=%s;",
                    (auteur, date_creation, citation, quote_id))
        updated_rows = cur.rowcount
        conn.commit()

        cur.close()
        conn.close()

        if updated_rows > 0:
            return jsonify({"status": "success", "message": f"Citation with ID {quote_id} updated"})
        else:
            return jsonify({"status": "error", "message": f"Citation with ID {quote_id} not found"})


api.add_resource(UpdateQuote, '/api/update_quote/<int:quote_id>')

if __name__ == '__main__':
    app.run(debug=True)
