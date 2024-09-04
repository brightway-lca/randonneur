from pathlib import Path
from typing import List

import xlsxwriter

ROLES = [
    "author",
    "publisher",
    "maintainer",
    "wrangler",
    "contributor",
]
MAPPINGS = [
    "SIMAPRO_CSV",
    "ECOSPOLD2",
    "ECOSPOLD1_BIO",
    "ECOSPOLD2_BIO",
    "ECOSPOLD2_BIO_FLOWMAPPER",
    "CUSTOM",
]


def create_excel_template(data: List[dict], filepath: Path, replace_existing: bool = False) -> Path:
    """
    Create an Excel template with optionally some data for a new matching data file.

    `data` should be a list of dictionaries like `{'source': {}, 'target': {}}`. The keys and values
    in these sub-dictionaries should be strings, or castable to strings in a way that can be
    reversed. This function doesn't do any type conversion or other data handling.

    `filepath` should be the complete filepath of the file to be created, including directory and
    suffix.

    `replace_existing`: Flag on whether to overwrite `filepath` if it exists.

    Returns the filepath of the created file.
    """
    filepath = Path(filepath)

    if filepath.is_file() and not replace_existing:
        raise OSError("File `{filepath.name}` already exists and `replace_existing` is false.")

    source_fields, target_fields = set(), set()

    for obj in data:
        source_fields.update(set(obj.get("source", [])))
        target_fields.update(set(obj.get("target", [])))

    source_fields, target_fields = sorted(source_fields), sorted(target_fields)
    source_offset = len(source_fields)

    workbook = xlsxwriter.Workbook(filepath)
    header = workbook.add_format({"bold": True, "font_size": 16})
    orange = workbook.add_format({"bg_color": "#ffdfba", "bold": True, "font_size": 14})
    green = workbook.add_format({"bg_color": "#baffc9", "bold": True, "font_size": 14})
    blue = workbook.add_format({"bg_color": "#bae1ff", "bold": True, "font_size": 14})
    yellow = workbook.add_format({"bg_color": "#ffffba", "bold": True, "font_size": 14})
    red = workbook.add_format({"bg_color": "#ffb3ba", "bold": True, "font_size": 14})
    italic = workbook.add_format({"italic": True, "font_size": 12})
    normal = workbook.add_format({"font_size": 12})

    sheet = workbook.add_worksheet("Matching")

    sheet.write_string(0, 0, "Randonneur template matching file", header)
    sheet.write_string(2, 0, "Metadata", header)
    sheet.write_string(3, 0, "Name", orange)
    sheet.write_string(4, 0, "Description", orange)
    sheet.write_string(4, 2, "String; optional", italic)
    sheet.write_string(5, 0, "Version", orange)
    sheet.write_string(5, 2, "String like \"1.0\"; optional", italic)
    sheet.write_string(6, 0, "Source ID", orange)
    sheet.write_string(6, 2, "String like \"SimaPro-9\"; optional", italic)
    sheet.write_string(7, 0, "Target ID", orange)
    sheet.write_string(7, 2, "String like \"lcacommons-2024\"; optional", italic)
    sheet.write_string(9, 0, "Contributors", yellow)
    sheet.write_string(9, 1, "You can add additional rows via copying if needed", italic)
    sheet.write_string(10, 0, "Name", yellow)
    sheet.write_string(10, 1, "Role", yellow)
    sheet.write_string(10, 2, "Homepage", yellow)
    sheet.write_string(13, 0, "Field mapping", red)
    sheet.write_string(13, 1, "CUSTOM mapping needs to be defined on import", italic)
    sheet.write_string(14, 0, "Source mapping", red)
    sheet.write_string(15, 0, "Target mapping", red)
    sheet.write_string(17, 0, "Data", header)
    template_offset = 18

    sheet.data_validation(11, 1, 11, 1, {
        'validate': 'list',
        'source': ROLES
    })
    sheet.write_string(11, 1, "author", normal)
    sheet.data_validation(14, 1, 15, 1, {
        'validate': 'list',
        'source': MAPPINGS
    })
    sheet.write_string(14, 1, "SIMAPRO_CSV", normal)
    sheet.write_string(15, 1, "ECOSPOLD2", normal)

    sheet.write_string(template_offset, 0, "Source", blue)
    for index in range(1, len(source_fields)):
        sheet.write_string(template_offset, index, "", blue)

    sheet.write_string(template_offset, source_offset, "Target", green)
    for index in range(1, len(target_fields)):
        sheet.write_string(template_offset, index + source_offset, "", green)

    for i, label in enumerate(source_fields):
        sheet.write_string(template_offset + 1, i, label, blue)
    for i, label in enumerate(target_fields):
        sheet.write_string(template_offset + 1, i + source_offset, label, green)
    for row_index, row in enumerate(data):
        for column_index, label in enumerate(source_fields):
            if row["source"].get(label):
                sheet.write_string(template_offset + row_index + 2, column_index, row["source"][label], normal)
        for column_index, label in enumerate(target_fields):
            if row["target"].get(label):
                sheet.write_string(
                    template_offset + row_index + 2, source_offset + column_index, row["target"][label], normal
                )

    sheet.autofit()
    workbook.close()
    return filepath
