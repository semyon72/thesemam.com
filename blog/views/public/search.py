# Project: blog_7myon_com
# Package: 
# Filename: search.py
# Generated: 2021 Jun 06 at 07:27 
# Description of <search>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.db.models import fields, Case, When, F, Value, Subquery, OuterRef, Sum, functions

from .entry import EntryListView
from ...models import EntryText
from ...models_tools import IContains, StripTags


class SearchEntryListView(EntryListView):
    """
    This view needs in SQL function 'strip_tags'
    Implementation for MySQL https://stackoverflow.com/a/13346684
    """

    search_kwarg = 'q'
    headline_cost = 50
    body_text_cost = 35

    def _get_value_expression(self):
        q = self.request.GET.get(self.search_kwarg, None)
        if q:
            return [v for v in q.split() if v]

    def get_queryset(self):
        # Need to implement - This more optimized query -
        # duration of execution on 100.000 rows of entries and 160.713 rows of entrytext is 10.593 sec - 11.109 sec
        # if to make use LIKE '%on_%world%' instead of REGEXP '.*on.+world.*' then will be faster, in practice
        # SELECT *
        # FROM (
        # SELECT `blog_entry`.`id`, `blog_entry`.`blog_id`, `blog_entry`.`author_id`,
        #  `blog_entry`.`headline`, `blog_entry`.`create_date`, `blog_entry`.`pub_date`,
        #  `blog_entry`.`mod_date`, `blog_entry`.`inactive`,
        #  COALESCE((
        #     SELECT SUM(0.35) AS `rank`
        #     FROM `blog_entrytext` U0
        #     WHERE (
        #         (STRIP_TAGS(U0.`body_text`) REGEXP '.*on.+world.*')
        #         AND U0.`entry_id` = `blog_entry`.`id`
        #     ) GROUP BY U0.`entry_id` ORDER BY NULL
        # ), 0.0) AS `text_rank`,
        # CASE WHEN (`blog_entry`.`headline` REGEXP '.*on.+world.*') THEN 0.5 ELSE 0.0 END AS `entry_rank`
        # FROM `blog_entry`
        # WHERE NOT `blog_entry`.`inactive`
        # ) as r
        # WHERE r.text_rank + r.entry_rank > 0
        # ORDER BY r.text_rank + r.entry_rank DESC, r.pub_date DESC
        val = self._get_value_expression()
        qs = super().get_queryset()
        if val is not None:
            sq_bt_rank = EntryText.objects.filter(
                # body_text__striptags__iregex=val,
                # Regexp(StripTags(F('body_text')), val),
                IContains(StripTags(F('body_text')), val),
                entry=OuterRef('pk')
            ).values('entry').annotate(rank=Sum(self.body_text_cost, output_field=fields.IntegerField())).values('rank')

            qs = qs.annotate(
                text_rank=functions.Coalesce(Subquery(sq_bt_rank), 0, output_field=fields.IntegerField()),
                # entry_rank=Case(When(Regexp(F('headline'), val), then=Value(50)), default=Value(0), output_field=fields.IntegerField()),
                entry_rank=Case(
                    When(IContains(F('headline'), val), then=Value(self.headline_cost)),
                    default=Value(0),
                    output_field=fields.IntegerField()
                ),
                total_rank=F('text_rank')+F('entry_rank')
            ).filter(inactive=False, total_rank__gt=0).order_by('-total_rank', '-pub_date')

            # Now query is - But this query is less optimized than above "Need to implement" -
            # duration of execution on 100.000 rows of entries and 160.713 rows of entrytext is 24.719 sec - 29.219 sec
            # SELECT `blog_entry`.`id`, `blog_entry`.`blog_id`, `blog_entry`.`author_id`,
            # `blog_entry`.`headline`, `blog_entry`.`create_date`, `blog_entry`.`pub_date`,
            # `blog_entry`.`mod_date`, `blog_entry`.`inactive`,
            # COALESCE((SELECT SUM(0.35e0) AS `rank` FROM `blog_entrytext` U0 WHERE ((STRIP_TAGS(U0.`body_text`) REGEXP '.*ce.+pl.*') AND U0.`entry_id` = `blog_entry`.`id`) GROUP BY U0.`entry_id` ORDER BY NULL), 0.0e0) AS `text_rank`,
            # CASE WHEN (`blog_entry`.`headline` REGEXP '.*ce.+pl.*') THEN 0.5e0 ELSE 0.0e0 END AS `entry_rank`,
            # (COALESCE((SELECT SUM(0.35e0) AS `rank` FROM `blog_entrytext` U0 WHERE ((STRIP_TAGS(U0.`body_text`) REGEXP '.*ce.+pl.*') AND U0.`entry_id` = `blog_entry`.`id`) GROUP BY U0.`entry_id` ORDER BY NULL), 0.0e0) + CASE WHEN (`blog_entry`.`headline` REGEXP '.*ce.+pl.*') THEN 0.5e0 ELSE 0.0e0 END) AS `total_rank`
            # FROM `blog_entry`
            # WHERE (
            # NOT `blog_entry`.`inactive`
            # AND (COALESCE((SELECT SUM(0.35e0) AS `rank` FROM `blog_entrytext` U0 WHERE ((STRIP_TAGS(U0.`body_text`) REGEXP '.*ce.+pl.*') AND U0.`entry_id` = `blog_entry`.`id`) GROUP BY U0.`entry_id` ORDER BY NULL), 0.0e0)
            #     + CASE WHEN (`blog_entry`.`headline` REGEXP '.*ce.+pl.*') THEN 0.5e0 ELSE 0.0e0 END) > 0.0e0
            # )
            # ORDER BY `total_rank` DESC, `blog_entry`.`pub_date` DESC

        return qs

    def add_found_info(self, entry):
        found_entries = entry.fields.get('entry_rank', {}).get('value', 0) // self.headline_cost
        found_entrytexts = entry.fields.get('text_rank', {}).get('value', 0) // self.body_text_cost
        if found_entries + found_entrytexts > 0:
            fi = {'found_entries': found_entries, 'found_entrytexts': found_entrytexts}
            k = 'rank_info'
            entry.fields[k] = entry.create_fields_item(None, k.replace('_', ' '), fi)

    # for object modification purpose need to redefine RepeatableView method
    def get_content_list_item(self, obj, initkwargs=None):
        self.add_found_info(obj)
        return super().get_content_list_item(obj, initkwargs)
