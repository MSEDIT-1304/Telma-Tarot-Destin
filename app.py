from flask import Flask, render_template, redirect, session, url_for, request
import stripe
import os

# ==========================================================
# APPLICATION
# ==========================================================

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

def get_panier():

    if "panier" not in session:
        session["panier"] = []

    return session["panier"]


def calcul_total():

    return sum(article["prix"] for article in get_panier())


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

@app.route("/retours-clients")
def retours_clients():
    return render_template("retours_clients.html")

@app.route("/panier")
def panier():

    return render_template(
        "panier.html",
        articles=get_panier(),
        total=calcul_total()
    )


@app.route("/remerciements")
def remerciements():

    return render_template(
        "remerciements.html",
        commandes=[]
    )
# ==========================================================
# AJOUT AU PANIER
# ==========================================================

@app.route("/ajouter/<produit>")
def ajouter(produit):

    if produit not in PRODUITS:
        return redirect(url_for("services"))

    panier = get_panier()

    # Empêche les doublons
    for article in panier:
        if article["code"] == produit:
            return redirect(url_for("panier"))

    panier.append({

        "code": produit,

        "nom": PRODUITS[produit]["nom"],

        "prix": PRODUITS[produit]["prix"]

    })

    session["panier"] = panier

    session.modified = True

    return redirect(url_for("panier"))


# ==========================================================
# SUPPRIMER DU PANIER
# ==========================================================

@app.route("/supprimer/<produit>")
def supprimer(produit):

    panier = get_panier()

    panier = [article for article in panier if article["code"] != produit]

    session["panier"] = panier

    session.modified = True

    return redirect(url_for("panier"))

# ==========================================================
# PAIEMENT STRIPE
# ==========================================================

@app.route("/payer")
def payer():

    if len(get_panier()) == 0:
        return redirect(url_for("panier"))

    line_items = []

    for article in get_panier():

        line_items.append({

            "price_data": {

                "currency": "eur",

                "product_data": {

                    "name": article["nom"]

                },

                "unit_amount": article["prix"] * 100

            },

            "quantity": 1

        })

    checkout_session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        line_items=line_items,

        mode="payment",

        success_url=request.host_url.rstrip("/") + url_for("success"),

        cancel_url=request.host_url.rstrip("/") + url_for("cancel")

    )

    return redirect(checkout_session.url, code=303)


# ==========================================================
# PAIEMENT ACCEPTE
# ==========================================================

@app.route("/success")
def success():

    commandes = list(get_panier())

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

    return redirect(url_for("panier"))


# ==========================================================
# LANCEMENT
# ==========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT", 5000)),

        debug=False

    )


