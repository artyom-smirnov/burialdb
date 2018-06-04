import csv
import os
import mimetypes

from mimetypes import MimeTypes
from chardet import UniversalDetector

import openpyxl


class ImporterFactory(object):
    def __init__(self, import_object):
        mimetypes.init()
        self._import_object = import_object

    def get_importer(self):
        m = MimeTypes()
        path = self._import_object.file.path
        _, ext = os.path.splitext(path)
        mimetype, _ = m.guess_type(path)
        if mimetype == 'text/csv':
            return CSVImporter(self._import_object)
        elif mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            return XLSXImporter(self._import_object)
        else:
            raise Exception('Не знаю как обработать файл типа {0} ({1})'.format(ext, mimetype))


class CSVImporter(object):
    def __init__(self, import_object):
        self._cvs_file = import_object.file.path
        self._header = import_object.header
        self._numbering = import_object.numbering
        self._delimiter = import_object.delimiter
        self._quotechar = import_object.quotechar

    @staticmethod
    def get_name():
        return 'csv'

    def import_data(self):
        data = []
        data_header = []
        data_cols = 0

        detector = UniversalDetector()
        detector.reset()
        with open(self._cvs_file, 'rb') as f:
            for line in f.readlines():
                detector.feed(line)
                if detector.done: break
            detector.close()
        encoding = detector.result['encoding']

        if not encoding:
            raise Exception('Невозможно определить кодировку или файл бинарный')

        with open(self._cvs_file, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=self._delimiter, quotechar=self._quotechar)
            header = self._header
            for row in reader:
                if row.count('') == len(row):
                    continue
                if header:
                    header -= 1
                    data_header.append(row)
                    continue
                data_cols = max(data_cols, len(row[self._numbering:]))
                data.append((row[0:self._numbering], row[self._numbering:]))

        return data_header, data, data_cols


class XLSXImporter(object):
    def __init__(self, import_object):
        self._xlsx_file = import_object.file.path
        self._header = import_object.header
        self._numbering = import_object.numbering

    @staticmethod
    def get_name():
        return 'xlsx'

    def import_data(self):
        wb = openpyxl.load_workbook(self._xlsx_file)
        wb.template = False
        ws = wb.active

        header = self._header

        data = []
        data_header = []
        data_cols = 0

        for row in ws.rows:
            values_row = [cell.value if cell.value else '' for cell in row]
            if values_row.count('') == len(values_row):
                continue

            if header:
                header -= 1
                data_header.append(values_row)
                continue
            else:
                data_cols = max(data_cols, len(values_row[self._numbering:]))
                data.append((values_row[0:self._numbering], values_row[self._numbering:]))

        return data_header, data, data_cols
