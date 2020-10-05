import datetime

import six
import unicodecsv

from geraldo.widgets import ObjectValue

from .base import ReportGenerator


class CSVGenerator(ReportGenerator):
    """This is a generator to output data in CSV format. This format can be
        imported as a spreadsheet to Excel, OpenOffice Calc,
        Google Docs Spreadsheet, and others.

    Attributes:

        * 'filename' - is the file path you can inform optionally to save
                       text to.
        * 'writer' - is unicodecsv.writer function you can inform manually to
                     make it customizable. This function must expects a first
                     argument to receive a file object and returns a
                     unicodecsv.writer object.
    """
    writer = None
    writer_function = unicodecsv.writer
    first_row_with_column_names = False

    mimetype = 'text/csv'

    def __init__(self, report, cache_enabled=None, writer=None,
                 first_row_with_column_names=None, **kwargs):
        super(CSVGenerator, self).__init__(report, **kwargs)

        # Cache enabled
        if cache_enabled is not None:
            self.cache_enabled = cache_enabled
        elif self.cache_enabled is None:
            self.cache_enabled = bool(self.report.cache_status)

        # Sets the writer function
        self.writer = writer or self.writer

        # Sets to append the first row with column names
        # (ObjectValue name/attribute_name/expression)
        if first_row_with_column_names is not None:
            self.first_row_with_column_names = first_row_with_column_names

        # utf-8-sig writes a BOM whereas utf-8 does not
        self.encoding = "utf-8-sig"

        # Additional attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

    def start_writer(self, filename=None):
        if self.writer:
            return

        filename = filename or self.filename

        if isinstance(filename, str):
            filename = open(filename, 'w+b')

        # Default writer uses comma as separator and quotes only when necessary
        self.writer = self.writer_function(
            filename, quoting=unicodecsv.QUOTE_MINIMAL, encoding=self.encoding
        )

    def execute(self):
        super(CSVGenerator, self).execute()

        # Calls the before_print event
        self.report.do_before_print(generator=self)

        # Write the CSV output
        self.generate_csv()

        # Calls the after_print event
        self.report.do_after_print(generator=self)

    def get_hash_key(self, objects):
        """Appends pdf extension to the hash_key"""
        return super(CSVGenerator, self).get_hash_key(objects) + '.csv'

    # METHODS THAT ARE TOTALLY SPECIFIC TO THIS GENERATOR AND MUST
    # OVERRIDE THE SUPERCLASS EQUIVALENT ONES

    def generate_csv(self):
        """Generates the CSV output"""

#        self._current_object_index = 0
#        objects = self.report.get_objects_list()

        self.start_writer()

        # Make a sorted list of columns
        columns = [el for el in self.report.band_detail.elements
                   if isinstance(el, ObjectValue)]
        columns.sort(key=lambda a: a.left)

        # First row with column names
        if self.first_row_with_column_names:
            cells = [(col.name or col.expression or col.attribute_name)
                     for col in columns]
            self.writer.writerow(cells)

#        while self._current_object_index < len(objects):
            # Get current object from list
#            self._current_object = objects[self._current_object_index]
        for row in self.report.get_objects_list():

            cells = []

            for element in columns:
                widget = element.clone()

                # Set widget colors
                widget.font_color = self.report.default_font_color

                # Set widget basic attributes
                widget.instance = row
#                widget.instance = self._current_object
                widget.generator = self
                widget.report = self.report
                widget.band = self.report.band_detail
                widget.page = None

                cells.append(widget.text)

            # Next object
#            self._current_object_index += 1

            if six.PY2:
                self.writer.writerow([cell.encode("utf-8") for cell in cells])
            else:
                self.writer.writerow(cells)
