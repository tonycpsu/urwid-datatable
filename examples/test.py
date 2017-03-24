#!/usr/bin/python
from __future__ import division
import logging
logger = logging.getLogger(__name__)
import urwid
from urwid_datatable import *
from urwid_utils.palette import *
import os
import random
import string
from optparse import OptionParser

screen = urwid.raw_display.Screen()
# screen.set_terminal_properties(1<<24)
screen.set_terminal_properties(256)

NORMAL_FG_MONO = "white"
NORMAL_FG_16 = "light gray"
NORMAL_BG_16 = "black"
NORMAL_FG_256 = "light gray"
NORMAL_BG_256 = "g0"

def main():


    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="count", default=0),
    (options, args) = parser.parse_args()

    if options.verbose:
        formatter = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s",
                                        datefmt='%Y-%m-%d %H:%M:%S')
        fh = logging.FileHandler("datatable.log")
        # fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        if options.verbose > 1:
            logger.setLevel(logging.DEBUG)
            logging.getLogger("urwid_datatable").setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            logging.getLogger("urwid_datatable").setLevel(logging.INFO)
        logger.addHandler(fh)
        logging.getLogger("urwid_datatable").addHandler(fh)
        # logging.getLogger("raccoon.dataframe").setLevel(logging.DEBUG)
        # logging.getLogger("raccoon.dataframe").addHandler(fh)


    entries = DataTable.get_palette_entries()
    palette = Palette("default", **entries)

    class ExampleDataTable(DataTable):

        columns = [
            # DataTableColumn("uniqueid", width=10, align="right", padding=1),
            DataTableColumn("foo", width=10, align="right", padding=0),# margin=1),
            DataTableColumn("bar", width=10, align="right", padding=1),# margin=5),
            DataTableColumn("baz", width=("weight", 1)),
            # DataTableColumn("zzz", width=("weight", 1)),
        ]

        index="index"


        def __init__(self, num_rows = 10, *args, **kwargs):
            self.num_rows = num_rows
            # indexes = random.sample(range(self.num_rows*2), num_rows)
            indexes = range(self.num_rows)
            self.query_data = [
                self.random_row(indexes[i]) for i in range(self.num_rows)
                # self.random_row(i) for i in range(self.num_rows)
            ]
            random.shuffle(self.query_data)
            self.last_rec = len(self.query_data)
            super(ExampleDataTable, self).__init__(*args, **kwargs)

        def random_row(self, uniqueid):
            return dict(uniqueid=uniqueid,
                        foo=random.choice(range(100) + [None]*20),
                        bar = (random.uniform(0, 1000)
                               if random.randint(0, 5)
                               else None),
                        baz =(''.join(random.choice(
                            string.ascii_uppercase
                            + string.lowercase
                            + string.digits + ' ' * 20
                        ) for _ in range(20))
                              if random.randint(0, 5)
                              else None),
                        qux = (random.uniform(0, 200)
                               if random.randint(0, 5)
                               else None),
                        xyzzy = random.randint(10, 100),
                        a = dict(b=dict(c=random.randint(0, 100))),
                        d = dict(e=dict(f=random.randint(0, 100)))

            )


        def query(self, sort=(None, None), offset=None, load_all=False):

            logger.info("query: offset=%s, sort=%s" %(offset, sort))
            try:
                sort_field, sort_reverse = sort
            except:
                sort_field = sort
                sort_reverse = False

            if sort_field:
                kwargs = {}
                kwargs["key"] = lambda x: (x.get(sort_field), x.get(self.index))
                kwargs["reverse"] = sort_reverse
                self.query_data.sort(**kwargs)
            if offset is not None:
                if not load_all:
                    start = offset
                    end = offset + self.limit
                    r = self.query_data[start:end]
                    logger.debug("%s:%s (%s)" %(start, end, len(r)))
                else:
                    r = self.query_data[offset:]
            else:
                r = self.query_data

            for d in r:
                yield d


        def query_result_count(self):
            return self.num_rows


        def keypress(self, size, key):
            if key == "ctrl r":
                self.reset(reset_sort=True)
            if key == "ctrl d":
                self.log_dump(10)
            if key == "ctrl f":
                self.focus_position = 0
            elif key == "1":
                self.sort_by_column("foo")
            elif key == "2":
                self.sort_by_column("bar")
            elif key == "3":
                self.sort_by_column("baz")
            elif key == "a":
                self.add_row(self.random_row(self.last_rec))
                self.last_rec += 1
            elif key == "shift left":
                self.cycle_sort_column(-1)
            elif key == "shift right":
                self.cycle_sort_column(1)
            elif key == "shift end":
                self.load_all()
                self.listbox.focus_position = len(self) -1
            else:
                return super(ExampleDataTable, self).keypress(size, key)


    tables = [

        # ExampleDataTable(
        #     0,
        #     limit=5,
        #     index="uniqueid",
        #     sort_by = ("bar", False),
        #     query_sort=True,
        #     with_header=True,
        #     with_footer=True,
        #     with_scrollbar=True
        # ),

        ExampleDataTable(
            100
        ),
        ExampleDataTable(
            1000,
            limit=100,
            index="uniqueid",
            sort_by = ("bar", False),
            query_sort=True,
            with_footer=True,
            with_scrollbar=True
        ),
        ExampleDataTable(
            10000,
            limit=1000,
            index="uniqueid",
            sort_by = ("foo", True),
            query_sort=True,
            with_scrollbar=True,
            with_header=False,
            with_footer=False,
        ),
    ]


    for table in tables:
        urwid.connect_signal(
            table, "select",
            lambda source, selection: logger.info("selection: %s" %(selection))
        )

    grid_flow = urwid.GridFlow(
        [urwid.BoxAdapter(t, 40) for t in tables], 60, 1, 1, "left"
    )


    pile = urwid.Pile([
        ('weight', 1, urwid.Filler(grid_flow)),
    ])

    def global_input(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        else:
            return False

    main = urwid.MainLoop(
        urwid.LineBox(pile),
        palette = palette,
        screen = screen,
        unhandled_input=global_input

    )

    main.run()

if __name__ == "__main__":
    main()
