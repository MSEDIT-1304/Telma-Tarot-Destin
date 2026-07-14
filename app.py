from flask import Flask, render_template, redirect, session, url_for, request
import stripe
import os

app = Flask(__name__)

app.secret_key = "telma_tarot_destin_panier_2026"

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


# ==========================================================
# PRODUITS
# ==========================================================

PRODUITS = {

    "tirage_simple": {
        "nom": "Tirage simple",
        "prix": 30
    },

    "tirage_complet": {
        "nom": "Tirage complet",
        "prix": 50
    },

    "pendule": {
        "nom": "Pendule",
        "prix": 30
    }

}


# ==========================================================
# FONCTIONS
# ==========================================================

def panier():

    if "panier" not in session:
        session["panier"] = []

    return session["panier"]


def total_panier():

    total = 0

    for article in panier():
        total += article["prix"]

    return total


# ==========================================================
# PAGES
# ==========================================================

@app.route("/")
def accueil():

    return render_template("index.html")


@app.route("/services")
def services():

    return render_template("services.html")


@app.route("/contact")
def contact():

    return render_template("contact.html")


@app.route("/panier")
def voir_panier():

    return render_template(

        "panier.html",

        articles=panier(),

        total=total_panier()

    )


# ==========================================================
# AJOUT AU PANIER
# ==========================================================

@app.route("/ajouter/<produit>")
def ajouter(produit):

    if produit not in PRODUITS:

        return redirect(url_for("services"))

    article = {

        "code": produit,

        "nom": PRODUITS[produit]["nom"],

        "prix": PRODUITS[produit]["prix"]

    }

    p = panier()

    p.append(article)

    session["panier"] = p

    session.modified = True

    return redirect(url_for("voir_panier"))

# ==========================================================
# SUPPRIMER DU PANIER
# ==========================================================

@app.route("/supprimer/<produit>")
def supprimer(produit):

    p = panier()

    for article in p:

        if article["code"] == produit:

            p.remove(article)

            break

    session["panier"] = p

    session.modified = True

    return redirect(url_for("voir_panier"))


# ==========================================================
# PAIEMENT STRIPE
# ==========================================================

@app.route("/payer")
def payer():

    if len(panier()) == 0:

        return redirect(url_for("voir_panier"))

    line_items = []

    for article in panier():

        line_items.append({

            "price_data": {

                "currency": "eur",

                "product_data": {

                    "name": article["nom"]

                },

                "unit_amount": int(article["prix"] * 100)

            },

            "quantity": 1

        })

    checkout = stripe.checkout.Session.create(

        payment_method_types=["card"],

        line_items=line_items,

        mode="payment",

        success_url=request.host_url.rstrip("/") + "/success",

        cancel_url=request.host_url.rstrip("/") + "/cancel"

    )

    return redirect(checkout.url, code=303)

# ==========================================================
# PAIEMENT VALIDE
# ==========================================================

@app.route("/success")
def success():

    commandes = list(panier())

    session["panier"] = []

    session.modified = True

    return render_template(

        "remerciements.html",

        commandes=commandes

    )

# ==========================================================
# PAIEMENT ANNULE
# ==========================================================

@app.route("/cancel")
def cancel():

    return redirect(url_for("voir_panier"))


# ==========================================================
# LANCEMENT
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
