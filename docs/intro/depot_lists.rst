.. _setup-depot-lists:

Depot Lists
===========

Depot lists are generated files that contain a summary of the subscription parts for each depot on a given date.
They are used for packing and distribution at the depots.

Juntagrico comes with three default depot lists:

- **depotlist**: The main depot list, showing who should pick up what in the depot, or what should go in whose bag, depending on your method of distribution.
- **depot_overview**: Overview of quantities per depot, grouped by tour.
- **amount_overview**: Summary of total quantities per weekday.

This page explains how to customize these lists and create your own.
For the detailed reference on available settings, context variables, template tags, and filters,
see :ref:`DEPOT_LISTS <settings-depot-lists>` and :ref:`Depot List Templates <reference-depot-list-templates>`.


Generating Depot Lists
----------------------

Depot lists are generated using the :ref:`generate_depot_list <reference-generate-depot-list>` management command.
It can be called manually or scheduled via a cron job.

.. code-block:: bash

    python manage.py generate_depot_list

The command generates all lists defined in the :ref:`DEPOT_LISTS <settings-depot-lists>` setting.


Default Depot Lists
-------------------

By default, three depot lists are configured:

.. code-block:: python

    {
        'depotlist': 'exports/depotlist.html',
        'depot_overview': 'exports/depot_overview.html',
        'amount_overview': 'exports/amount_overview.html',
    }

Each key is the file name (without extension) of the generated PDF, and each value is the template path.


Customizing a Template
----------------------

Use template overrides to change the default depot lists. See :ref:`reference-templates` and :ref:`reference-depot-list-templates`.

Adding Extra Context
--------------------

If you need to change or add context data, provide an ``extra_context`` callable:

.. code-block:: python

    from juntagrico import defaults

    def my_extra_context(context):
        # context contains date, subscriptions, products, depots, tours, etc.
        return {
            'custom_greeting': 'Willkommen!',
        }

    DEPOT_LISTS = defaults.DEPOT_LISTS | {
        'depotlist': {
            'name': 'Meine Depotliste',
            'template': 'exports/my_depotlist.html',  # optionally define a custom template
            'extra_context': my_extra_context,
        },
    }

The callable receives the default context dictionary and must return a dictionary of extra variables.

Default Context Variables
^^^^^^^^^^^^^^^^^^^^^^^^^

- ``date`` (``datetime.date``): The date for which the depot list is generated.
- ``subscriptions`` (QuerySet): Subscriptions on the depot list served on the given date.
- ``products`` (QuerySet): ``SubscriptionProduct`` objects on the depot list.
- ``depots`` (list): ``Depot`` objects for the depot list.
- ``tours`` (QuerySet): Visible ``Tour`` objects.
- ``tour_days`` (dict): Maps tour weekday integers to display names.
- ``messages`` (QuerySet): Active ``ListMessage`` objects.
- ``vocabulary``: ``Vocabulary`` helper for configured vocabulary terms.


Creating an Additional List
---------------------------

To add a completely new depot list, simply add a new entry to ``DEPOT_LISTS``:

.. code-block:: python

    from juntagrico import defaults

    DEPOT_LISTS = defaults.DEPOT_LISTS | {
        'my_custom_list': 'exports/my_custom_list.html',
    }

The minimal form (just a template path) uses the key as the file name and generates the default context.


Filtering Subscriptions
-----------------------

You can pass a custom set of subscriptions to the template via ``extra_context``:

.. code-block:: python

    from juntagrico import defaults
    from juntagrico.entity.subs import Subscription

    def filtered_context(context):
        return {
            'subscriptions': Subscription.objects.served_on(context['date']).filter(
                depot__tour__name='Montag'
            ),
        }

    DEPOT_LISTS = defaults.DEPOT_LISTS | {
        'monday_list': {
            'name': 'Montag Liste',
            'template': 'exports/monday_list.html',
            'extra_context': filtered_context,
        },
    }


Template Tags and Filters
--------------------------

.. note::

    **Renamed in Juntagrico 2.1:** The ``active_on`` filter has been deprecated. Use the equivalent ``served_on`` instead.

Depot list templates use several template tags and filters from ``juntagrico.depot_extras``.
Load them with ``{% load juntagrico.depot_extras %}``.

Common patterns include:

.. code-block:: html

    {# Count parts of a specific size for a depot on a date #}
    {{ subscriptions|by_depot:depot|parts_by_size:size|served_on:date|count }}

    {# Count units for a tour on a date #}
    {{ subscriptions|by_tour:tour|count_units:date }}

For the full list of available filters and context variables, see :ref:`Depot List Templates <reference-depot-list-templates>`.


Example: Minimal Custom Template
---------------------------------

Here is a minimal custom depot list template that extends the default structure:

.. code-block:: html

    {% load juntagrico.depot_extras %}
    {% load juntagrico.config %}
    {% load i18n %}
    {% vocabulary "depot" as v_depot %}
    <html>
    <head>
        <title>{{ v_depot }}-Liste</title>
        <meta charset="utf-8">
        <style>{% include "./snippets/snippet_depotlist_style.css" %}</style>
    </head>
    <body>
    {% for depot in depots %}
        {% include "./snippets/snippet_depotlist_header.html" with first=True %}
        {% for sub in subscriptions|by_depot:depot %}
            <tr class="bottom-border">
                <td class="namecol top-border left-border horz-left">
                    {% include "juntagrico/snippets/subscription/recipients.html" with subscription=sub %}
                </td>
                {% for product in products %}
                    {% for size in product.sizes.on_depot_list.sorted %}
                        <td class="top-border left-border">
                            {{ sub|parts_by_size:size|served_on:date|count|default:'' }}
                        </td>
                    {% endfor %}
                {% endfor %}
                <td class="checkboxcol top-border left-border"></td>
                <td class="checkboxcol top-border left-border right-border"></td>
            </tr>
        {% endfor %}
        </table>
        <div class="page-break"></div>
    {% endfor %}
    </body>
    </html>


See :ref:`Depot List Templates <reference-depot-list-templates>` for a complete reference of all context variables,
template tags, filters, and snippets.
