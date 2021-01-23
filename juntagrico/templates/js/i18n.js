{% load i18n %}
{% load config %}
var email_string = "{% trans "E-Mail senden" %}";
var send_string = "{% trans "senden" %}";
var email_single_string = "{% trans "E-Mail an dieses" %}";
var email_multi_string = "{% trans "E-Mail an diese" %}";
var member_string = "{% vocabulary "member" %}";
var members_string = "{% vocabulary "member_pl" %}";
var search_field = "{% trans "Suchen: " %}";
var sb_lang = {
       "add":"{% trans "Suchkriterium hinzufügen" %}",
        "clearAll":"{% trans "Leeren" %}",
        "condition":"{% trans "Bedingung" %}",
        "conditions": {
            "date": {
                "after":"{% trans "Nach" %}",
                "before":"{% trans "Vor" %}",
                "between":"{% trans "Zwischen" %}",
                "empty":"{% trans "Leer" %}",
                "equals":"{% trans "Entspricht" %}",
                "not":"{% trans "Nicht" %}",
                "notBetween":"{% trans "Nicht zwischen" %}",
                "notEmpty":"{% trans "Nicht leer" %}"
            },
            "moment": {
                "after":"{% trans "Nach" %}",
                "before":"{% trans "Vor" %}",
                "between":"{% trans "Zwischen" %}",
                "empty":"{% trans "Leer" %}",
                "equals":"{% trans "Entspricht" %}",
                "not":"{% trans "Nicht" %}",
                "notBetween":"{% trans "Nicht zwischen" %}",
                "notEmpty":"{% trans "Nicht leer" %}"
            },
            "number": {
                "between":"{% trans "Zwischen" %}",
                "empty":"{% trans "Leer" %}",
                "equals":"{% trans "Entspricht" %}",
                "gt":"{% trans "Größer als" %}",
                "gte":"{% trans "Größer als oder gleich" %}",
                "lt":"{% trans "Kleiner als" %}",
                "lte":"{% trans "Kleiner als oder gleich" %}",
                "not":"{% trans "Nicht" %}",
                "notBetween":"{% trans "Nicht zwischen" %}",
                "notEmpty":"{% trans "Nicht leer" %}"
            },
            "string": {
                "contains":"{% trans "Beinhaltet" %}",
                "empty":"{% trans "Leer" %}",
                "endsWith":"{% trans "Endet mit" %}",
                "equals":"{% trans "Entspricht" %}",
                "not":"{% trans "Nicht" %}",
                "notEmpty":"{% trans "Nicht leer" %}",
                "startsWith":"{% trans "Startet mit" %}"
            }
        },
        "data":"{% trans "Feld" %}",
        "deleteTitle":"{% trans "Filterregel entfernen" %}",
        "leftTitle":"{% trans "Äußere Kriterien" %}",
        "logicAnd":"{% trans "und" %}",
        "logicOr":"{% trans "oder" %}",
        "rightTitle":"{% trans "Innere Kriterien" %}",
        "title": "",
        "value":"{% trans "Wert" %}"
    };