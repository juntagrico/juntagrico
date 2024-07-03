{% load i18n %}
{% load juntagrico.config %}
{% vocabulary "member" as v_member %}
{% vocabulary "member_pl" as v_member_pl %}
var email_button_string = [
    "{% trans "E-Mail senden" %}",
    "{% blocktrans %}E-Mail an {{ v_member }} senden{% endblocktrans %}",
    "{% blocktrans %}E-Mail an {count} {{ v_member_pl }} senden{% endblocktrans %}"
]
var dt_language = {
    decimal: "{{ 0.0 }}"[1], {# let django render this as float to take the decimal symbol from here #}
    search: "{% trans "Suchen: " %}",
    emptyTable: "{% trans "Keine Daten verfügbar" %}",
    zeroRecords: "{% trans "Keine passenden Einträge gefunden" %}",
    info: "{% trans "Zeige _TOTAL_ von _MAX_" %}",
    infoFiltered: "{% trans " - gefiltert" %}",
    infoEmpty: "{% trans "Zeige _TOTAL_ von _MAX_" %}",
    select: {
        rows: {
            0: "",
            1: "{% trans "1 Eintrag ausgewählt" %}",
            _: "{% trans "%d Einträge ausgewählt" %}",
        },
    },
    searchBuilder: {
        "search": "{% trans "Suchen" %}",
        "add": "{% trans "Suchkriterium hinzufügen" %}",
        "clearAll": "{% trans "Leeren" %}",
        "condition": "{% trans "Bedingung" %}",
        "conditions": {
            "date": {
                "after": "{% trans "Nach" %}",
                "before": "{% trans "Vor" %}",
                "between": "{% trans "Zwischen" %}",
                "empty": "{% trans "Leer" %}",
                "equals": "{% trans "Entspricht" %}",
                "not": "{% trans "Nicht" %}",
                "notBetween": "{% trans "Nicht zwischen" %}",
                "notEmpty": "{% trans "Nicht leer" %}"
            },
            "moment": {
                "after": "{% trans "Nach" %}",
                "before": "{% trans "Vor" %}",
                "between": "{% trans "Zwischen" %}",
                "empty": "{% trans "Leer" %}",
                "equals": "{% trans "Entspricht" %}",
                "not": "{% trans "Nicht" %}",
                "notBetween": "{% trans "Nicht zwischen" %}",
                "notEmpty": "{% trans "Nicht leer" %}"
            },
            "number": {
                "between": "{% trans "Zwischen" %}",
                "empty": "{% trans "Leer" %}",
                "equals": "{% trans "Entspricht" %}",
                "gt": "{% trans "Größer als" %}",
                "gte": "{% trans "Größer als oder gleich" %}",
                "lt": "{% trans "Kleiner als" %}",
                "lte": "{% trans "Kleiner als oder gleich" %}",
                "not": "{% trans "Nicht" %}",
                "notBetween": "{% trans "Nicht zwischen" %}",
                "notEmpty": "{% trans "Nicht leer" %}"
            },
            "string": {
                "contains": "{% trans "Beinhaltet" %}",
                "empty": "{% trans "Leer" %}",
                "endsWith": "{% trans "Endet mit" %}",
                "equals": "{% trans "Entspricht" %}",
                "not": "{% trans "Nicht" %}",
                "notEmpty": "{% trans "Nicht leer" %}",
                "startsWith": "{% trans "Startet mit" %}"
            }
        },
        "data": "{% trans "Feld" %}",
        "deleteTitle": "{% trans "Filterregel entfernen" %}",
        "leftTitle": "{% trans "Äußere Kriterien" %}",
        "logicAnd": "{% trans "und" %}",
        "logicOr": "{% trans "oder" %}",
        "rightTitle": "{% trans "Innere Kriterien" %}",
        "title": "",
        "value": "{% trans "Wert" %}"
    }
}
